from django import forms

from .models import Treino


class TreinoForm(forms.ModelForm):
    """Ficha de treino do aluno: criar e editar usam o mesmo formulário."""

    class Meta:
        model = Treino
        fields = ["titulo", "descricao"]
        labels = {"titulo": "Título", "descricao": "Exercícios"}
        help_texts = {"descricao": "Um exercício por linha, ex.: Supino reto 4x10"}

    def clean_descricao(self):
        descricao = self.cleaned_data["descricao"]
        # cada linha com texto vira um exercício; a ficha precisa ter pelo menos um
        linhas = [linha for linha in descricao.splitlines() if linha.strip()]
        if not linhas:
            raise forms.ValidationError("Informe pelo menos um exercício.")
        return descricao
