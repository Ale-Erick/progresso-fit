from django.apps import AppConfig


class ContasConfig(AppConfig):
    name = 'contas'

    def ready(self):
        # importa os signals quando o app carrega, para que o Django os registre
        from . import signals
