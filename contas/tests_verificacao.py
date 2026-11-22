import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from contas.forms import EspecialistaForm
from contas.models import Especialista

# pasta temporária para os documentos dos testes (não suja a pasta media/ do projeto)
MEDIA_TESTE = tempfile.mkdtemp()


def pdf(nome="registro.pdf"):
    return SimpleUploadedFile(nome, b"%PDF-1.4 documento de teste", content_type="application/pdf")


def dados_pedido(**alteracoes):
    dados = {"area_atuacao": "Nutricionista", "registro_profissional": "CRN-12345"}
    dados.update(alteracoes)
    return dados


@override_settings(MEDIA_ROOT=MEDIA_TESTE)
class VerificacaoTest(TestCase):
    """RF008 / UC05 / UC11 / RN007."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TESTE, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username="nutri@exemplo.com", email="nutri@exemplo.com", password="TreinoForte2026")
        self.user.perfil.tipo = "Especialista"
        self.user.perfil.save()
        self.client.force_login(self.user)

    def test_primeiro_acesso_mostra_o_formulario(self):
        resposta = self.client.get(reverse("contas:verificacao"))
        self.assertContains(resposta, "Enviar pedido")

    def test_enviar_pdf_cria_pedido_pendente(self):
        resposta = self.client.post(reverse("contas:verificacao"), {**dados_pedido(), "documento": pdf()})
        self.assertRedirects(resposta, reverse("contas:verificacao"))
        pedido = Especialista.objects.get(user=self.user)
        self.assertEqual(pedido.status_verificacao, "Pendente")
        self.assertTrue(pedido.documento.name.startswith("documentos/"))

    def test_pedido_pendente_mostra_status_sem_formulario(self):
        self.client.post(reverse("contas:verificacao"), {**dados_pedido(), "documento": pdf()})
        resposta = self.client.get(reverse("contas:verificacao"))
        self.assertContains(resposta, "Pendente de verificação")
        self.assertNotContains(resposta, "Enviar pedido")

    def test_formato_invalido_e_recusado(self):
        exe = SimpleUploadedFile("virus.exe", b"MZ...", content_type="application/octet-stream")
        resposta = self.client.post(reverse("contas:verificacao"), {**dados_pedido(), "documento": exe})
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.context["form"].has_error("documento"))
        self.assertFalse(Especialista.objects.exists())

    def test_sem_documento_e_recusado(self):
        resposta = self.client.post(reverse("contas:verificacao"), dados_pedido())
        self.assertTrue(resposta.context["form"].has_error("documento"))

    def test_documento_maior_que_5mb_e_recusado(self):
        grande = pdf()
        grande.size = 6 * 1024 * 1024  # finge um arquivo de 6 MB
        form = EspecialistaForm(dados_pedido(), {"documento": grande})
        self.assertFalse(form.is_valid())
        self.assertIn("O documento deve ter no máximo 5 MB.", form.errors["documento"])

    def test_registro_repetido_e_recusado(self):
        outro = User.objects.create_user(username="outro@exemplo.com", password="TreinoForte2026")
        Especialista.objects.create(user=outro, area_atuacao="Nutricionista", registro_profissional="CRN-12345")
        resposta = self.client.post(reverse("contas:verificacao"), {**dados_pedido(), "documento": pdf()})
        self.assertTrue(resposta.context["form"].has_error("registro_profissional"))

    def test_pedido_pendente_nao_pode_ser_alterado(self):
        self.client.post(reverse("contas:verificacao"), {**dados_pedido(), "documento": pdf()})
        self.client.post(reverse("contas:verificacao"), {**dados_pedido(registro_profissional="CRN-99999"), "documento": pdf()})
        self.assertEqual(Especialista.objects.get(user=self.user).registro_profissional, "CRN-12345")

    def test_rejeitado_pode_reenviar_e_volta_para_pendente(self):
        self.client.post(reverse("contas:verificacao"), {**dados_pedido(), "documento": pdf()})
        Especialista.objects.filter(user=self.user).update(status_verificacao="Rejeitado")  # o admin rejeitou
        resposta = self.client.get(reverse("contas:verificacao"))
        self.assertContains(resposta, "Reenviar pedido")
        self.client.post(reverse("contas:verificacao"), {**dados_pedido(registro_profissional="CRN-54321"), "documento": pdf("novo.pdf")})
        pedido = Especialista.objects.get(user=self.user)  # continua sendo um registro só
        self.assertEqual(pedido.status_verificacao, "Pendente")
        self.assertEqual(pedido.registro_profissional, "CRN-54321")

    def test_verificado_ve_link_para_o_painel(self):
        Especialista.objects.create(user=self.user, area_atuacao="Nutricionista", registro_profissional="CRN-1", status_verificacao="Verificado")
        self.assertContains(self.client.get(reverse("contas:verificacao")), "Abrir painel de validações")

    def test_aluno_nao_acessa_verificacao(self):
        self.user.perfil.tipo = "Aluno"
        self.user.perfil.save()
        resposta = self.client.post(reverse("contas:verificacao"), {**dados_pedido(), "documento": pdf()})
        self.assertRedirects(resposta, reverse("contas:home"))
        self.assertFalse(Especialista.objects.exists())

    def test_admin_lista_o_pedido_com_link_do_documento(self):
        self.client.post(reverse("contas:verificacao"), {**dados_pedido(), "documento": pdf()})
        admin = User.objects.create_superuser(username="admin", password="TreinoForte2026")
        self.client.force_login(admin)
        resposta = self.client.get(reverse("admin:contas_especialista_changelist"))
        self.assertContains(resposta, "Abrir documento")
