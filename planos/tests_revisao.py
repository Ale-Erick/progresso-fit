from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from contas.models import Especialista
from metricas.models import MetricaCorporal

from .models import PlanoAlimentar


def criar_usuario(email, tipo):
    user = User.objects.create_user(username=email, email=email, password="TreinoForte2026")
    user.perfil.tipo = tipo
    user.perfil.nome_completo = email.split("@")[0].title()
    user.perfil.save()
    return user


def criar_especialista(email, status="Verificado", registro="CRN-1"):
    user = criar_usuario(email, "Especialista")
    especialista = Especialista.objects.create(user=user, area_atuacao="Nutricionista", registro_profissional=registro, status_verificacao=status)
    return user, especialista


class RevisaoTestBase(TestCase):
    def setUp(self):
        self.aluno = criar_usuario("aluno@exemplo.com", "Aluno")
        MetricaCorporal.objects.create(user=self.aluno, data=date(2026, 11, 1), peso=80, altura=1.75)
        self.nutri, self.especialista = criar_especialista("nutri@exemplo.com")
        self.plano = PlanoAlimentar.objects.create(
            user=self.aluno, especialista=self.especialista, titulo="Plano alimentar - Emagrecimento", descricao="Sugestão da IA",
        )
        self.client.force_login(self.nutri)

    def url_revisar(self, plano=None):
        return reverse("planos:revisar", args=[(plano or self.plano).id])


class PainelTest(RevisaoTestBase):
    """UC10, passos 1 e 2 / RN007 / RN008."""

    def test_painel_lista_os_planos_pendentes_do_especialista(self):
        resposta = self.client.get(reverse("planos:validacoes"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Plano alimentar - Emagrecimento")
        self.assertContains(resposta, "Aluno")  # nome do aluno vem do perfil

    def test_painel_nao_mostra_planos_de_outro_especialista(self):
        _, outro = criar_especialista("outro@exemplo.com", registro="CRN-2")
        PlanoAlimentar.objects.create(user=self.aluno, especialista=outro, titulo="Plano do outro especialista", descricao="x")
        resposta = self.client.get(reverse("planos:validacoes") + "?status=Todos")
        self.assertNotContains(resposta, "Plano do outro especialista")

    def test_filtro_por_status(self):
        PlanoAlimentar.objects.create(user=self.aluno, especialista=self.especialista, titulo="Plano já aprovado", descricao="x", status="Aprovado")
        pendentes = self.client.get(reverse("planos:validacoes"))
        aprovados = self.client.get(reverse("planos:validacoes") + "?status=Aprovado")
        todos = self.client.get(reverse("planos:validacoes") + "?status=Todos")
        self.assertNotContains(pendentes, "Plano já aprovado")
        self.assertContains(aprovados, "Plano já aprovado")
        self.assertNotContains(aprovados, "Plano alimentar - Emagrecimento")
        self.assertEqual(len(todos.context["page_obj"]), 2)

    def test_painel_paginado(self):
        for numero in range(11):
            PlanoAlimentar.objects.create(user=self.aluno, especialista=self.especialista, titulo=f"Plano {numero}", descricao="x")
        pagina2 = self.client.get(reverse("planos:validacoes") + "?status=Pendente&page=2")
        self.assertEqual(len(pagina2.context["page_obj"]), 2)  # 12 pendentes: 10 + 2

    def test_especialista_pendente_e_bloqueado(self):
        pendente, _ = criar_especialista("pendente@exemplo.com", status="Pendente", registro="CRN-3")
        self.client.force_login(pendente)
        for rota in [reverse("planos:validacoes"), self.url_revisar()]:
            resposta = self.client.get(rota, follow=True)
            self.assertRedirects(resposta, reverse("contas:verificacao"))
            self.assertContains(resposta, "só é liberado depois que o administrador verificar")

    def test_especialista_sem_pedido_de_verificacao_e_bloqueado(self):
        self.client.force_login(criar_usuario("novo@exemplo.com", "Especialista"))
        self.assertRedirects(self.client.get(reverse("planos:validacoes")), reverse("contas:verificacao"))

    def test_aluno_e_bloqueado(self):
        self.client.force_login(self.aluno)
        self.assertRedirects(self.client.get(reverse("planos:validacoes")), reverse("contas:home"))


class RevisarTest(RevisaoTestBase):
    """UC10, passos 3 a 5 / RF010 / RN006."""

    def test_tela_de_revisao_mostra_plano_e_metricas(self):
        resposta = self.client.get(self.url_revisar())
        self.assertContains(resposta, "Sugestão da IA")
        self.assertContains(resposta, "80")  # peso da última medição
        self.assertContains(resposta, "Confirmar revisão")
        self.assertNotContains(resposta, "em breve")

    def test_aprovar_libera_o_plano_para_o_aluno(self):
        resposta = self.client.post(self.url_revisar(), {"decisao": "Aprovado", "observacao": "Beba bastante água."})
        self.assertRedirects(resposta, reverse("planos:validacoes"))
        self.plano.refresh_from_db()
        self.assertEqual(self.plano.status, "Aprovado")
        self.assertEqual(self.plano.observacao, "Beba bastante água.")
        self.assertIsNotNone(self.plano.revisado_em)
        # RN006: agora o aluno vê o conteúdo do plano
        self.client.force_login(self.aluno)
        self.assertContains(self.client.get(reverse("planos:nutricao")), "Sugestão da IA")

    def test_ajustar_troca_a_descricao(self):
        self.client.post(self.url_revisar(), {"decisao": "Ajustado", "descricao_ajustada": "Plano revisado pelo especialista"})
        self.plano.refresh_from_db()
        self.assertEqual(self.plano.status, "Ajustado")
        self.assertEqual(self.plano.descricao, "Plano revisado pelo especialista")

    def test_ajustar_sem_texto_mostra_erro(self):
        resposta = self.client.post(self.url_revisar(), {"decisao": "Ajustado", "descricao_ajustada": "   "})
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.context["form"].has_error("descricao_ajustada"))
        self.plano.refresh_from_db()
        self.assertEqual(self.plano.status, "Pendente")

    def test_sem_decisao_mostra_erro(self):
        resposta = self.client.post(self.url_revisar(), {"observacao": "sem decisão"})
        self.assertTrue(resposta.context["form"].has_error("decisao"))

    def test_rejeitar_nao_libera_o_plano(self):
        self.client.post(self.url_revisar(), {"decisao": "Rejeitado"})
        self.plano.refresh_from_db()
        self.assertEqual(self.plano.status, "Rejeitado")
        self.client.force_login(self.aluno)
        self.assertNotContains(self.client.get(reverse("planos:nutricao")), "Sugestão da IA")

    def test_plano_revisado_abre_so_para_leitura_e_nao_muda(self):
        self.client.post(self.url_revisar(), {"decisao": "Aprovado"})
        resposta = self.client.get(self.url_revisar())
        self.assertNotContains(resposta, "Confirmar revisão")
        self.client.post(self.url_revisar(), {"decisao": "Rejeitado"})  # tentativa de mudar depois
        self.plano.refresh_from_db()
        self.assertEqual(self.plano.status, "Aprovado")

    def test_nao_revisa_plano_de_outro_especialista(self):
        _, outro = criar_especialista("outro@exemplo.com", registro="CRN-2")
        plano_do_outro = PlanoAlimentar.objects.create(user=self.aluno, especialista=outro, titulo="Plano do outro", descricao="x")
        self.assertEqual(self.client.get(self.url_revisar(plano_do_outro)).status_code, 404)
        self.assertEqual(self.client.post(self.url_revisar(plano_do_outro), {"decisao": "Aprovado"}).status_code, 404)
        plano_do_outro.refresh_from_db()
        self.assertEqual(plano_do_outro.status, "Pendente")
