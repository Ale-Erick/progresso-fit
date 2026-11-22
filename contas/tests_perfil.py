import shutil
import tempfile
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from contas.forms import PerfilForm
from metricas.models import MetricaCorporal

# pasta temporária para as fotos dos testes (não suja a pasta media/ do projeto)
MEDIA_TESTE = tempfile.mkdtemp()


def imagem_png(nome="foto.png", tamanho=(10, 10)):
    """Cria uma imagem PNG de verdade, na memória, para simular o upload."""
    arquivo = BytesIO()
    Image.new("RGB", tamanho, "green").save(arquivo, "PNG")
    return SimpleUploadedFile(nome, arquivo.getvalue(), content_type="image/png")


def dados_perfil(**alteracoes):
    dados = {
        "username": "maria",
        "nome_completo": "Maria Souza",
        "descricao": "Foco em constância",
        "nivel_conhecimento": "Intermediário",
        "publico": "on",
    }
    dados.update(alteracoes)
    return dados


@override_settings(MEDIA_ROOT=MEDIA_TESTE)
class PerfilTest(TestCase):
    """RF004 / RF007 / UC04 / UC07."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TESTE, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username="maria@exemplo.com", email="maria@exemplo.com", password="TreinoForte2026")
        self.user.perfil.nome_completo = "Maria"
        self.user.perfil.save()
        self.client.force_login(self.user)

    def test_perfil_mostra_os_dados_reais(self):
        resposta = self.client.get(reverse("contas:perfil"))
        self.assertContains(resposta, "Maria")
        self.assertContains(resposta, "@maria@exemplo.com")
        self.assertNotContains(resposta, "perfil de exemplo")

    def test_editar_vem_preenchido(self):
        resposta = self.client.get(reverse("contas:perfil_editar"))
        self.assertContains(resposta, 'value="maria@exemplo.com"')
        self.assertContains(resposta, 'value="Maria"')

    def test_editar_salva_os_dados(self):
        resposta = self.client.post(reverse("contas:perfil_editar"), dados_perfil())
        self.assertRedirects(resposta, reverse("contas:perfil"))
        self.user.refresh_from_db()
        self.user.perfil.refresh_from_db()
        self.assertEqual(self.user.username, "maria")
        self.assertEqual(self.user.perfil.nome_completo, "Maria Souza")
        self.assertEqual(self.user.perfil.nivel_conhecimento, "Intermediário")
        self.assertTrue(self.user.perfil.publico)

    def test_desmarcar_publico_deixa_o_perfil_privado(self):
        self.client.post(reverse("contas:perfil_editar"), dados_perfil())
        dados = dados_perfil()
        del dados["publico"]  # checkbox desmarcado não é enviado pelo navegador
        self.client.post(reverse("contas:perfil_editar"), dados)
        self.user.perfil.refresh_from_db()
        self.assertFalse(self.user.perfil.publico)

    def test_envia_e_remove_foto(self):
        self.client.post(reverse("contas:perfil_editar"), dados_perfil(foto=imagem_png()))
        self.user.perfil.refresh_from_db()
        self.assertTrue(self.user.perfil.foto.name.startswith("perfis/"))
        # a foto aparece no perfil e no header
        self.assertContains(self.client.get(reverse("contas:perfil")), self.user.perfil.foto.url, count=2)

        self.client.post(reverse("contas:perfil_editar"), dados_perfil(**{"foto-clear": "on"}))
        self.user.perfil.refresh_from_db()
        self.assertFalse(self.user.perfil.foto)

    def test_arquivo_que_nao_e_imagem_e_recusado(self):
        falso = SimpleUploadedFile("foto.png", b"isto nao e uma imagem", content_type="image/png")
        resposta = self.client.post(reverse("contas:perfil_editar"), dados_perfil(foto=falso))
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.context["perfil_form"].has_error("foto"))
        self.user.perfil.refresh_from_db()
        self.assertFalse(self.user.perfil.foto)

    def test_foto_maior_que_2mb_e_recusada(self):
        # testa o PerfilForm direto: assim dá para "fingir" o tamanho do arquivo
        grande = imagem_png()
        grande.size = 3 * 1024 * 1024  # 3 MB
        form = PerfilForm(dados_perfil(), {"foto": grande}, instance=self.user.perfil)
        self.assertFalse(form.is_valid())
        self.assertIn("A foto deve ter no máximo 2 MB.", form.errors["foto"])

    def test_username_repetido_mostra_erro_e_nao_salva_nada(self):
        User.objects.create_user(username="joao", password="TreinoForte2026")
        resposta = self.client.post(reverse("contas:perfil_editar"), dados_perfil(username="joao", nome_completo="Outro Nome"))
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.context["usuario_form"].has_error("username"))
        self.user.refresh_from_db()
        self.user.perfil.refresh_from_db()
        self.assertEqual(self.user.username, "maria@exemplo.com")
        self.assertEqual(self.user.perfil.nome_completo, "Maria")  # o perfil também não foi salvo

    def test_descricao_com_mais_de_150_caracteres_e_recusada(self):
        resposta = self.client.post(reverse("contas:perfil_editar"), dados_perfil(descricao="x" * 151))
        self.assertTrue(resposta.context["perfil_form"].has_error("descricao"))

    def test_especialista_nao_tem_campo_de_nivel(self):
        self.user.perfil.tipo = "Especialista"
        self.user.perfil.save()
        resposta = self.client.get(reverse("contas:perfil_editar"))
        self.assertNotContains(resposta, "Nível de conhecimento corporal")
        dados = dados_perfil()
        del dados["nivel_conhecimento"]
        self.assertRedirects(self.client.post(reverse("contas:perfil_editar"), dados), reverse("contas:perfil"))


@override_settings(MEDIA_ROOT=MEDIA_TESTE)
class ExcluirContaTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="ana@exemplo.com", email="ana@exemplo.com", password="TreinoForte2026")
        MetricaCorporal.objects.create(user=self.user, data="2026-11-01", peso=70, altura=1.65)
        self.client.force_login(self.user)

    def test_excluir_conta_apaga_usuario_e_dados(self):
        resposta = self.client.post(reverse("contas:excluir_conta"), follow=True)
        self.assertRedirects(resposta, reverse("login"))
        self.assertContains(resposta, "Sua conta foi excluída.")
        self.assertFalse(User.objects.filter(email="ana@exemplo.com").exists())
        self.assertFalse(MetricaCorporal.objects.exists())  # cascata
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_excluir_por_get_nao_apaga(self):
        self.assertEqual(self.client.get(reverse("contas:excluir_conta")).status_code, 405)
        self.assertTrue(User.objects.filter(email="ana@exemplo.com").exists())
