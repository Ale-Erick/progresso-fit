from django import forms
from django.utils import timezone

from .models import MetricaCorporal

# campos opcionais que não podem ser negativos nem absurdos (valor máximo aceito)
LIMITES_OPCIONAIS = {
    "gordura_visceral": 60,
    "metabolismo_basal": 10000,
    "peitoral": 300,
    "braco_esq": 300,
    "braco_dir": 300,
    "cintura": 300,
    "abdomen": 300,
    "quadril": 300,
    "coxa_esq": 300,
    "coxa_dir": 300,
    "panturrilha_esq": 300,
    "panturrilha_dir": 300,
}


class MetricaForm(forms.ModelForm):
    """Registro de medição corporal (RF005 / UC03).
    Peso e altura são obrigatórios porque no model eles não têm blank=True (RN003)."""

    class Meta:
        model = MetricaCorporal
        # todos os campos do model, menos o usuário: ele vem do login, não do formulário
        exclude = ["user"]

    def clean_data(self):
        data = self.cleaned_data["data"]
        if data > timezone.localdate():
            raise forms.ValidationError("A data da medição não pode estar no futuro.")
        return data

    def clean_peso(self):
        peso = self.cleaned_data["peso"]
        if peso < 1 or peso > 999:
            raise forms.ValidationError("Informe um peso entre 1 e 999 kg.")
        return peso

    def clean_altura(self):
        altura = self.cleaned_data["altura"]
        if altura < 0.5 or altura > 2.99:
            raise forms.ValidationError("Informe a altura em metros, entre 0.50 e 2.99.")
        return altura

    def clean_percentual_gordura(self):
        gordura = self.cleaned_data["percentual_gordura"]
        # campo opcional: só valida se foi preenchido
        if gordura is not None and (gordura < 0 or gordura > 100):
            raise forms.ValidationError("O percentual de gordura deve ficar entre 0 e 100.")
        return gordura

    def clean(self):
        dados = super().clean()
        # mesma regra para todos os campos opcionais: se preenchido, entre 0 e o limite
        for campo, maximo in LIMITES_OPCIONAIS.items():
            valor = dados.get(campo)
            if valor is not None and (valor < 0 or valor > maximo):
                self.add_error(campo, f"Informe um valor entre 0 e {maximo}.")
        return dados
