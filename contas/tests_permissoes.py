from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from contas.models import Especialista


def criar_usuario(email, tipo="Aluno"):
    user = User.objects.create_user(username=email, email=email, password="TreinoForte2026")
    user.perfil.nome_completo = f"Usuário {tipo}"
    user.perfil.tipo = tipo
    user.perfil.save()
    return user


# rotas internas, separadas por quem pode abrir
ROTAS_DE_TODOS = ["contas:home", "contas:perfil", "contas:perfil_editar"]
ROTAS_DO_ALUNO = ["metricas:registrar", "metricas:evolucao", "planos:treinos", "planos:nutricao"]
ROTAS_DO_ESPECIALISTA = ["contas:verificacao", "planos:validacoes"]
# o painel exige especialista VERIFICADO (RN007); ver planos/tests_revisao.py
ROTAS_DO_ESPECIALISTA_SEM_VERIFICACAO = ["contas:verificacao"]


class VisitanteTest(TestCase):
    """Sem login, nenhuma tela interna abre: tudo vai para o login (rubrica: rotas protegidas)."""

    def test_rotas_internas_mandam_para_o_login(self):
        for nome in ROTAS_DE_TODOS + ROTAS_DO_ALUNO + ROTAS_DO_ESPECIALISTA:
            rota = reverse(nome)
            resposta = self.client.get(rota)
            self.assertRedirects(resposta, f"{reverse('login')}?next={rota}", msg_prefix=nome)

    def test_inicio_sem_login_vai_para_o_login(self):
        resposta = self.client.get("/")
        self.assertRedirects(resposta, f"{reverse('login')}?next=/")

    def test_telas_de_acesso_continuam_abertas(self):
        for nome in ["login", "contas:cadastro", "contas:confirmar_email", "password_reset"]:
            self.assertEqual(self.client.get(reverse(nome)).status_code, 200, nome)


class AlunoTest(TestCase):
    def setUp(self):
        self.aluno = criar_usuario("aluno@exemplo.com", "Aluno")
        self.client.force_login(self.aluno)

    def test_aluno_abre_as_rotas_do_aluno(self):
        for nome in ROTAS_DE_TODOS + ROTAS_DO_ALUNO:
            self.assertEqual(self.client.get(reverse(nome)).status_code, 200, nome)

    def test_aluno_nao_abre_rotas_do_especialista(self):
        for nome in ROTAS_DO_ESPECIALISTA:
            resposta = self.client.get(reverse(nome), follow=True)
            self.assertRedirects(resposta, reverse("contas:home"), msg_prefix=nome)
            self.assertContains(resposta, "Esta área é exclusiva para especialistas.")

    def test_menu_do_aluno(self):
        resposta = self.client.get(reverse("contas:home"))
        self.assertContains(resposta, "Evolução")
        self.assertContains(resposta, "Nutrição")
        self.assertNotContains(resposta, "Painel de validações")
        self.assertNotContains(resposta, reverse("contas:verificacao"))

    def test_header_mostra_usuario_e_sair(self):
        resposta = self.client.get(reverse("contas:home"))
        self.assertContains(resposta, "Usuário Aluno")
        self.assertContains(resposta, "Sair")
        self.assertNotContains(resposta, "Criar conta")
        self.assertNotContains(resposta, ">Entrar<")

    def test_perfil_do_aluno_nao_mostra_verificacao(self):
        self.assertNotContains(self.client.get(reverse("contas:perfil")), "Verificação profissional")


class EspecialistaTest(TestCase):
    def setUp(self):
        self.especialista = criar_usuario("nutri@exemplo.com", "Especialista")
        self.client.force_login(self.especialista)

    def test_especialista_abre_as_rotas_do_especialista(self):
        for nome in ROTAS_DE_TODOS + ROTAS_DO_ESPECIALISTA_SEM_VERIFICACAO:
            self.assertEqual(self.client.get(reverse(nome)).status_code, 200, nome)

    def test_especialista_nao_abre_rotas_do_aluno(self):
        for nome in ROTAS_DO_ALUNO:
            resposta = self.client.get(reverse(nome), follow=True)
            self.assertRedirects(resposta, reverse("contas:home"), msg_prefix=nome)
            self.assertContains(resposta, "Esta área é exclusiva para alunos.")

    def test_especialista_nao_solicita_plano(self):
        resposta = self.client.post(reverse("planos:solicitar_plano"))
        self.assertRedirects(resposta, reverse("contas:home"))

    def test_menu_do_especialista(self):
        resposta = self.client.get(reverse("contas:home"))
        self.assertContains(resposta, "Painel de validações")
        self.assertContains(resposta, reverse("contas:verificacao"))
        self.assertNotContains(resposta, reverse("metricas:evolucao"))
        self.assertNotContains(resposta, reverse("planos:nutricao"))

    def test_inicio_mostra_situacao_da_verificacao(self):
        self.assertContains(self.client.get(reverse("contas:home")), "Enviar documentos")
        Especialista.objects.create(user=self.especialista, area_atuacao="Nutricionista", registro_profissional="CRN-1", status_verificacao="Verificado")
        resposta = self.client.get(reverse("contas:home"))
        self.assertContains(resposta, "Verificado")
        self.assertContains(resposta, "Abrir painel de validações")

    def test_perfil_do_especialista_mostra_verificacao(self):
        self.assertContains(self.client.get(reverse("contas:perfil")), "Verificação profissional")
