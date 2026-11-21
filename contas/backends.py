from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailBackend(ModelBackend):
    """Permite entrar com e-mail e senha (RF003).

    O Django chama o authenticate() de cada backend listado em
    AUTHENTICATION_BACKENDS, em ordem, até um deles devolver um usuário.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        # no formulário de login, o campo "username" recebe o e-mail digitado
        user = User.objects.filter(email__iexact=username).first()
        if user is None:
            return None

        # check_password compara a senha digitada com o hash salvo no banco (RNF001)
        if user.check_password(password):
            # De propósito não conferimos is_active aqui: assim o LoginForm consegue
            # mostrar "Confirme seu e-mail antes de entrar" para a conta inativa.
            return user
        return None
