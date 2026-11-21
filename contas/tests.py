from django.contrib.auth.models import User
from django.test import TestCase

from .models import Perfil


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
