from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Treino


class TreinoCrudTest(TestCase):
    """CRUD da ficha de treino (item 07) e privacidade (RN008)."""

    def setUp(self):
        self.aluno = User.objects.create_user(username="aluno@exemplo.com", email="aluno@exemplo.com", password="TreinoForte2026")
        self.outro = User.objects.create_user(username="outro@exemplo.com", email="outro@exemplo.com", password="TreinoForte2026")
        self.client.force_login(self.aluno)

    def criar_treino(self, user, titulo="Treino A"):
        return Treino.objects.create(user=user, titulo=titulo, descricao="Supino reto 4x10\nCrucifixo 3x12")

    def test_criar_treino(self):
        resposta = self.client.post(reverse("planos:treino_criar"), {"titulo": "Treino A", "descricao": "Supino reto 4x10\nAgachamento 4x8"})
        self.assertRedirects(resposta, reverse("planos:treinos"))
        treino = Treino.objects.get()
        self.assertEqual(treino.user, self.aluno)
        self.assertEqual(len(treino.exercicios()), 2)

    def test_criar_sem_exercicios_mostra_erro(self):
        resposta = self.client.post(reverse("planos:treino_criar"), {"titulo": "Treino A", "descricao": "   \n  "})
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.context["form"].has_error("descricao"))
        self.assertFalse(Treino.objects.exists())

    def test_criar_sem_titulo_mostra_erro(self):
        resposta = self.client.post(reverse("planos:treino_criar"), {"titulo": "", "descricao": "Supino 4x10"})
        self.assertTrue(resposta.context["form"].has_error("titulo"))

    def test_lista_mostra_so_os_treinos_do_aluno(self):
        self.criar_treino(self.aluno, "Meu treino")
        self.criar_treino(self.outro, "Treino do outro")
        resposta = self.client.get(reverse("planos:treinos"))
        self.assertContains(resposta, "Meu treino")
        self.assertNotContains(resposta, "Treino do outro")

    def test_editar_vem_preenchido_e_salva(self):
        treino = self.criar_treino(self.aluno)
        resposta = self.client.get(reverse("planos:treino_editar", args=[treino.id]))
        self.assertContains(resposta, 'value="Treino A"')
        resposta = self.client.post(reverse("planos:treino_editar", args=[treino.id]), {"titulo": "Treino B", "descricao": "Remada 4x10"})
        self.assertRedirects(resposta, reverse("planos:treinos"))
        treino.refresh_from_db()
        self.assertEqual(treino.titulo, "Treino B")

    def test_nao_edita_treino_de_outro_aluno(self):
        treino = self.criar_treino(self.outro)
        self.assertEqual(self.client.get(reverse("planos:treino_editar", args=[treino.id])).status_code, 404)
        self.client.post(reverse("planos:treino_editar", args=[treino.id]), {"titulo": "Invadido", "descricao": "x 1x1"})
        treino.refresh_from_db()
        self.assertEqual(treino.titulo, "Treino A")

    def test_excluir_por_post(self):
        treino = self.criar_treino(self.aluno)
        resposta = self.client.post(reverse("planos:treino_excluir", args=[treino.id]), follow=True)
        self.assertRedirects(resposta, reverse("planos:treinos"))
        self.assertContains(resposta, "excluído")
        self.assertFalse(Treino.objects.exists())

    def test_excluir_por_get_nao_apaga(self):
        treino = self.criar_treino(self.aluno)
        self.assertEqual(self.client.get(reverse("planos:treino_excluir", args=[treino.id])).status_code, 405)
        self.assertTrue(Treino.objects.exists())

    def test_nao_exclui_treino_de_outro_aluno(self):
        treino = self.criar_treino(self.outro)
        self.assertEqual(self.client.post(reverse("planos:treino_excluir", args=[treino.id])).status_code, 404)
        self.assertTrue(Treino.objects.exists())

    def test_especialista_nao_acessa_treinos(self):
        self.aluno.perfil.tipo = "Especialista"
        self.aluno.perfil.save()
        resposta = self.client.get(reverse("planos:treino_criar"))
        self.assertRedirects(resposta, reverse("contas:home"))
