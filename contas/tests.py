import re

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import Perfil

# dados de um cadastro válido, reaproveitados nos testes
DADOS_CADASTRO = {
    "nome_completo": "Maria Souza",
    "email": "maria@exemplo.com",
    "tipo": "Aluno",
    "password1": "TreinoForte2026",
    "password2": "TreinoForte2026",
}


def link_do_email(mensagem):
    """Pega o link de ativação de dentro do texto do e-mail."""
    return re.search(r"http://testserver(\S+)", mensagem.body).group(1)


class CadastroTest(TestCase):
    """UC01 / RF001 / RN001 / RN002."""

    def test_cadastro_cria_usuario_inativo_com_perfil_e_envia_email(self):
        resposta = self.client.post(reverse("contas:cadastro"), DADOS_CADASTRO)
        self.assertRedirects(resposta, reverse("contas:confirmar_email"))

        user = User.objects.get(email="maria@exemplo.com")
        self.assertFalse(user.is_active)  # RN002: inativa até confirmar
        self.assertEqual(user.username, "maria@exemplo.com")
        self.assertEqual(user.perfil.nome_completo, "Maria Souza")
        self.assertEqual(user.perfil.tipo, "Aluno")
        self.assertNotEqual(user.password, "TreinoForte2026")  # RNF001: senha salva como hash

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["maria@exemplo.com"])
        self.assertIn("/ativar/", mail.outbox[0].body)
        # o link precisa sair inteiro no terminal (sem a quebra "=" do quoted-printable)
        self.assertNotIn("quoted-printable", mail.outbox[0].message().as_string())

    def test_cadastro_de_especialista_guarda_o_tipo(self):
        self.client.post(reverse("contas:cadastro"), {**DADOS_CADASTRO, "tipo": "Especialista"})
        self.assertEqual(User.objects.get(email="maria@exemplo.com").perfil.tipo, "Especialista")

    def test_email_repetido_mostra_erro(self):
        User.objects.create_user(username="maria@exemplo.com", email="maria@exemplo.com", password="x")
        resposta = self.client.post(reverse("contas:cadastro"), {**DADOS_CADASTRO, "email": "MARIA@exemplo.com"})
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Já existe uma conta com este e-mail.")
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)

    def test_senhas_diferentes_mostram_erro(self):
        resposta = self.client.post(reverse("contas:cadastro"), {**DADOS_CADASTRO, "password2": "OutraSenha2026"})
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.context["form"].has_error("password2"))
        self.assertFalse(User.objects.exists())

    def test_senha_fraca_mostra_erro(self):
        resposta = self.client.post(reverse("contas:cadastro"), {**DADOS_CADASTRO, "password1": "12345678", "password2": "12345678"})
        self.assertTrue(resposta.context["form"].has_error("password2"))
        self.assertFalse(User.objects.exists())


class AtivacaoTest(TestCase):
    """RF002: link de confirmação de uso único."""

    def setUp(self):
        self.client.post(reverse("contas:cadastro"), DADOS_CADASTRO)
        self.link = link_do_email(mail.outbox[0])

    def test_link_valido_ativa_a_conta(self):
        resposta = self.client.get(self.link)
        self.assertRedirects(resposta, reverse("login"))
        self.assertTrue(User.objects.get(email="maria@exemplo.com").is_active)

    def test_link_usado_de_novo_so_avisa(self):
        self.client.get(self.link)
        resposta = self.client.get(self.link, follow=True)
        self.assertContains(resposta, "Sua conta já está ativa")

    def test_link_invalido_nao_ativa(self):
        user = User.objects.get(email="maria@exemplo.com")
        link_errado = self.link.rsplit("/", 2)[0] + "/token-errado/"
        resposta = self.client.get(link_errado, follow=True)
        self.assertContains(resposta, "Link de confirmação inválido ou expirado")
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_reenviar_manda_novo_email_so_para_conta_inativa(self):
        self.client.post(reverse("contas:confirmar_email"), {"email": "maria@exemplo.com"})
        self.assertEqual(len(mail.outbox), 2)
        # e-mail sem conta: a resposta é a mesma, mas nada é enviado
        resposta = self.client.post(reverse("contas:confirmar_email"), {"email": "ninguem@exemplo.com"}, follow=True)
        self.assertContains(resposta, "Se houver uma conta aguardando confirmação")
        self.assertEqual(len(mail.outbox), 2)


class LoginLogoutTest(TestCase):
    """UC02 / RF003: login com e-mail e senha."""

    def setUp(self):
        self.user = User.objects.create_user(username="joao@exemplo.com", email="joao@exemplo.com", password="TreinoForte2026")

    def test_login_com_email_vai_para_o_perfil(self):
        resposta = self.client.post(reverse("login"), {"username": "joao@exemplo.com", "password": "TreinoForte2026"})
        self.assertRedirects(resposta, reverse("contas:perfil"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_senha_errada_mostra_erro(self):
        resposta = self.client.post(reverse("login"), {"username": "joao@exemplo.com", "password": "errada"})
        self.assertContains(resposta, "E-mail ou senha incorretos.")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_conta_nao_confirmada_pede_confirmacao(self):
        self.user.is_active = False
        self.user.save()
        resposta = self.client.post(reverse("login"), {"username": "joao@exemplo.com", "password": "TreinoForte2026"})
        self.assertContains(resposta, "Confirme seu e-mail antes de entrar.")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logado_ve_sair_e_nao_ve_entrar(self):
        self.client.force_login(self.user)
        resposta = self.client.get(reverse("contas:home"))
        self.assertContains(resposta, "Sair")
        self.assertNotContains(resposta, "Criar conta")

    def test_logout_por_post_encerra_a_sessao(self):
        self.client.force_login(self.user)
        resposta = self.client.post(reverse("logout"))
        self.assertRedirects(resposta, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_admin_continua_entrando_com_username(self):
        User.objects.create_superuser(username="admin", password="TreinoForte2026")
        self.assertTrue(self.client.login(username="admin", password="TreinoForte2026"))


class PerfilAutomaticoTest(TestCase):
    """Signal post_save: todo User criado ganha um Perfil (issue Base da Etapa 2)."""

    def test_usuario_novo_ganha_perfil(self):
        user = User.objects.create_user(username="maria", password="SenhaForte123")
        self.assertTrue(Perfil.objects.filter(user=user).exists())

    def test_perfil_comeca_como_aluno_iniciante(self):
        user = User.objects.create_user(username="joao", password="SenhaForte123")
        self.assertEqual(user.perfil.tipo, "Aluno")
        self.assertEqual(user.perfil.nivel_conhecimento, "Iniciante")

    def test_nome_completo_vem_do_usuario(self):
        user = User.objects.create_user(
            username="ana", password="SenhaForte123", first_name="Ana", last_name="Lima"
        )
        self.assertEqual(user.perfil.nome_completo, "Ana Lima")

    def test_superusuario_tambem_ganha_perfil(self):
        admin = User.objects.create_superuser(username="admin", password="SenhaForte123")
        self.assertEqual(admin.perfil.nome_completo, "admin")

    def test_salvar_de_novo_nao_duplica_perfil(self):
        user = User.objects.create_user(username="pedro", password="SenhaForte123")
        user.first_name = "Pedro"
        user.save()
        self.assertEqual(Perfil.objects.filter(user=user).count(), 1)
