from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.files.uploadedfile import UploadedFile

from .models import Perfil

# tamanho máximo da foto de perfil: 2 MB (em bytes)
TAMANHO_MAXIMO_FOTO = 2 * 1024 * 1024


class CadastroForm(UserCreationForm):
    """Cadastro de conta (UC01). O UserCreationForm já traz password1 e password2,
    confere se as duas são iguais e aplica as regras de senha do settings."""

    nome_completo = forms.CharField(label="Nome completo", max_length=150)
    email = forms.EmailField(label="E-mail")
    tipo = forms.ChoiceField(label="Tipo de conta", choices=Perfil.TIPO_CHOICES, initial="Aluno")

    class Meta:
        model = User
        # o username não aparece no formulário: ele recebe o próprio e-mail no save()
        fields = ["email"]

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        # RN001: não pode existir outra conta com o mesmo e-mail (UC01, exceção 3a)
        if User.objects.filter(email__iexact=email).exists() or User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError("Já existe uma conta com este e-mail.")
        return email

    def save(self, commit=True):
        # super().save(commit=False) monta o User e guarda a senha criptografada (hash)
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        # RN002: a conta só é ativada depois que o usuário confirma o e-mail
        user.is_active = False
        if commit:
            user.save()  # o signal post_save cria o Perfil aqui
            user.perfil.nome_completo = self.cleaned_data["nome_completo"]
            user.perfil.tipo = self.cleaned_data["tipo"]
            user.perfil.save()
        return user


class LoginForm(AuthenticationForm):
    """Login com e-mail e senha (UC02). O campo continua se chamando "username"
    porque é assim que o Django espera; quem procura pelo e-mail é o EmailBackend."""

    error_messages = {
        "invalid_login": "E-mail ou senha incorretos.",
        # UC02, exceção 3b: conta criada, mas e-mail ainda não confirmado
        "inactive": "Confirme seu e-mail antes de entrar. Procure o link que enviamos no seu e-mail.",
    }


class ReenviarConfirmacaoForm(forms.Form):
    """Pede o e-mail para mandar de novo o link de confirmação."""

    email = forms.EmailField(label="E-mail")


class UsuarioForm(forms.ModelForm):
    """Parte do User que o usuário pode editar no perfil (UC04): o nome de usuário.
    O ModelForm já confere se outro usuário usa o mesmo nome (UC04, exceção 4a)."""

    class Meta:
        model = User
        fields = ["username"]
        labels = {"username": "Nome de usuário"}


class PerfilForm(forms.ModelForm):
    """Dados do Perfil editados pelo usuário (RF004 e RF007)."""

    class Meta:
        model = Perfil
        fields = ["foto", "nome_completo", "descricao", "nivel_conhecimento", "publico"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # o nível de conhecimento corporal é só do aluno (UC07): o especialista não vê esse campo
        if self.instance.tipo == "Especialista":
            del self.fields["nivel_conhecimento"]

    def clean_foto(self):
        foto = self.cleaned_data.get("foto")
        # só confere arquivos novos (a foto que já estava salva não é enviada de novo)
        # o ImageField já recusa arquivos que não são imagem
        if isinstance(foto, UploadedFile) and foto.size > TAMANHO_MAXIMO_FOTO:
            raise forms.ValidationError("A foto deve ter no máximo 2 MB.")
        return foto
