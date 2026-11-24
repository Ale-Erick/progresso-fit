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


class RevisaoForm(forms.Form):
    """Decisão do especialista sobre um plano alimentar (UC10 / RF010).
    É um forms.Form (e não ModelForm) porque os campos não são iguais aos do model:
    a decisão vira o status e o texto ajustado substitui a descrição."""

    DECISOES = (
        ("Aprovado", "Aprovar"),
        ("Ajustado", "Ajustar"),
        ("Rejeitado", "Rejeitar"),
    )

    decisao = forms.ChoiceField(choices=DECISOES, error_messages={"required": "Escolha aprovar, ajustar ou rejeitar."})
    descricao_ajustada = forms.CharField(required=False)
    observacao = forms.CharField(required=False, max_length=500)

    def clean(self):
        dados = super().clean()
        # validação que depende de dois campos: "Ajustar" exige o plano ajustado
        if dados.get("decisao") == "Ajustado" and not dados.get("descricao_ajustada", "").strip():
            self.add_error("descricao_ajustada", "Descreva o plano ajustado que o aluno vai receber.")
        return dados
