from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import MetricaCorporal


def criar_medicao(user, data, peso="80.00", altura="1.75", **extras):
    return MetricaCorporal.objects.create(user=user, data=data, peso=peso, altura=altura, **extras)


class MetricasTestBase(TestCase):
    def setUp(self):
        self.aluno = User.objects.create_user(username="aluno@exemplo.com", email="aluno@exemplo.com", password="TreinoForte2026")
        self.outro = User.objects.create_user(username="outro@exemplo.com", email="outro@exemplo.com", password="TreinoForte2026")
        self.client.force_login(self.aluno)


class RotasProtegidasTest(TestCase):
    def test_sem_login_vai_para_o_login(self):
        for rota in [reverse("metricas:registrar"), reverse("metricas:evolucao"), reverse("metricas:detalhe", args=[1])]:
            resposta = self.client.get(rota)
            self.assertRedirects(resposta, f"{reverse('login')}?next={rota}")


class RegistrarTest(MetricasTestBase):
    """UC03 / RF005 / RN003."""

    def test_post_valido_salva_para_o_usuario_logado(self):
        resposta = self.client.post(reverse("metricas:registrar"), {
            "data": timezone.localdate().isoformat(), "peso": "72.5", "altura": "1.80", "percentual_gordura": "16.3", "cintura": "82",
        })
        self.assertRedirects(resposta, reverse("metricas:evolucao"))
        metrica = MetricaCorporal.objects.get()
        self.assertEqual(metrica.user, self.aluno)
        self.assertEqual(float(metrica.peso), 72.5)
        self.assertEqual(metrica.cintura, 82)
        self.assertIsNone(metrica.quadril)  # campo opcional vazio fica em branco

    def test_sem_peso_e_altura_mostra_erro(self):
        resposta = self.client.post(reverse("metricas:registrar"), {"data": timezone.localdate().isoformat()})
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.context["form"].has_error("peso"))
        self.assertTrue(resposta.context["form"].has_error("altura"))
        self.assertFalse(MetricaCorporal.objects.exists())

    def test_data_no_futuro_mostra_erro(self):
        amanha = (timezone.localdate() + timedelta(days=1)).isoformat()
        resposta = self.client.post(reverse("metricas:registrar"), {"data": amanha, "peso": "72.5", "altura": "1.80"})
        self.assertContains(resposta, "A data da medição não pode estar no futuro.")
        self.assertFalse(MetricaCorporal.objects.exists())

    def test_valores_fora_do_limite_mostram_erro(self):
        resposta = self.client.post(reverse("metricas:registrar"), {
            "data": timezone.localdate().isoformat(), "peso": "72.5", "altura": "3.50", "percentual_gordura": "120", "cintura": "-5",
        })
        form = resposta.context["form"]
        self.assertTrue(form.has_error("altura"))
        self.assertTrue(form.has_error("percentual_gordura"))
        self.assertTrue(form.has_error("cintura"))

    def test_formulario_vem_com_a_ultima_medicao(self):
        criar_medicao(self.aluno, date(2026, 10, 1), peso="90.00")
        criar_medicao(self.aluno, date(2026, 11, 1), peso="85.50", cintura=88)
        resposta = self.client.get(reverse("metricas:registrar"))
        form = resposta.context["form"]
        self.assertEqual(str(form["peso"].value()), "85.50")
        self.assertEqual(form["cintura"].value(), 88)
        self.assertEqual(form["data"].value(), timezone.localdate().isoformat())
        # o valor aparece com ponto no <input type="number"> (e não com vírgula)
        self.assertContains(resposta, 'value="85.50"')


class EvolucaoTest(MetricasTestBase):
    """UC06 / RF006 / RN008."""

    def test_mostra_so_as_medicoes_do_aluno(self):
        criar_medicao(self.aluno, date(2026, 11, 1), peso="81.00")
        criar_medicao(self.outro, date(2026, 11, 2), peso="99.00")
        resposta = self.client.get(reverse("metricas:evolucao"))
        self.assertContains(resposta, "81")
        self.assertNotContains(resposta, "99,00")
        self.assertEqual(len(resposta.context["page_obj"]), 1)

    def test_sem_medicoes_mostra_aviso(self):
        resposta = self.client.get(reverse("metricas:evolucao"))
        self.assertContains(resposta, "Você ainda não registrou nenhuma medição.")

    def test_historico_paginado_de_10_em_10(self):
        for dia in range(1, 13):
            criar_medicao(self.aluno, date(2026, 10, dia))
        pagina1 = self.client.get(reverse("metricas:evolucao"))
        pagina2 = self.client.get(reverse("metricas:evolucao") + "?page=2")
        self.assertEqual(len(pagina1.context["page_obj"]), 10)
        self.assertEqual(len(pagina2.context["page_obj"]), 2)
        # o gráfico continua com todas as medições
        self.assertEqual(len(pagina1.context["grafico"]["datas"]), 12)

    def test_mostra_o_nivel_do_perfil(self):
        self.aluno.perfil.nivel_conhecimento = "Avançado"
        self.aluno.perfil.save()
        criar_medicao(self.aluno, date(2026, 11, 1))
        self.assertContains(self.client.get(reverse("metricas:evolucao")), "Avançado")


class DetalheExcluirTest(MetricasTestBase):
    """RN008 (privacidade) e exclusão por POST."""

    def test_detalhe_da_propria_medicao(self):
        metrica = criar_medicao(self.aluno, date(2026, 11, 1))
        self.assertEqual(self.client.get(reverse("metricas:detalhe", args=[metrica.id])).status_code, 200)

    def test_detalhe_de_outro_aluno_da_404(self):
        metrica = criar_medicao(self.outro, date(2026, 11, 1))
        self.assertEqual(self.client.get(reverse("metricas:detalhe", args=[metrica.id])).status_code, 404)

    def test_excluir_por_post(self):
        metrica = criar_medicao(self.aluno, date(2026, 11, 1))
        resposta = self.client.post(reverse("metricas:excluir", args=[metrica.id]))
        self.assertRedirects(resposta, reverse("metricas:evolucao"))
        self.assertFalse(MetricaCorporal.objects.exists())

    def test_excluir_por_get_nao_apaga(self):
        metrica = criar_medicao(self.aluno, date(2026, 11, 1))
        self.assertEqual(self.client.get(reverse("metricas:excluir", args=[metrica.id])).status_code, 405)
        self.assertTrue(MetricaCorporal.objects.exists())

    def test_nao_exclui_medicao_de_outro_aluno(self):
        metrica = criar_medicao(self.outro, date(2026, 11, 1))
        self.assertEqual(self.client.post(reverse("metricas:excluir", args=[metrica.id])).status_code, 404)
        self.assertTrue(MetricaCorporal.objects.exists())
