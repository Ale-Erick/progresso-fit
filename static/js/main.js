document.addEventListener("DOMContentLoaded", function () {
    var ano = document.getElementById("ano");
    if (ano) { ano.textContent = new Date().getFullYear(); }

    validarFormularios();
    confirmarSenha();
    contarCaracteres();
    validarArquivos();
    previewFoto();
    alternarAjuste();
});

// Validação no navegador com o estilo do Bootstrap (formulários com a classe .pf-validar)
function validarFormularios() {
    document.querySelectorAll("form.pf-validar").forEach(function (form) {
        form.addEventListener("input", function () { marcarNeutros(form); });
        form.addEventListener("submit", function (evento) {
            marcarNeutros(form);
            if (!form.checkValidity()) {
                evento.preventDefault();
                evento.stopPropagation();
                var primeiro = form.querySelector(":invalid");
                if (primeiro) { primeiro.focus(); }
            }
            form.classList.add("was-validated");
        });
    });
}

// Campos opcionais vazios (RN003) ficam neutros: sem verde e sem vermelho
function marcarNeutros(form) {
    form.querySelectorAll("input, select, textarea").forEach(function (campo) {
        if (campo.type === "hidden" || campo.required) { return; }
        var vazio = campo.type === "checkbox" || campo.value.trim() === "";
        campo.classList.toggle("pf-neutro", vazio);
    });
}

// Exceção 3b do UC01: as senhas precisam coincidir
function confirmarSenha() {
    document.querySelectorAll("[data-confirma]").forEach(function (campo) {
        var original = document.getElementById(campo.dataset.confirma);
        if (!original) { return; }

        function conferir() {
            campo.setCustomValidity(campo.value && campo.value !== original.value ? "As senhas não coincidem." : "");
        }

        campo.addEventListener("input", conferir);
        original.addEventListener("input", conferir);
    });
}

// Contador de caracteres (descrição do perfil limitada a 150)
function contarCaracteres() {
    document.querySelectorAll("[data-contador]").forEach(function (campo) {
        var saida = document.getElementById(campo.dataset.contador);
        if (!saida) { return; }

        function atualizar() {
            saida.textContent = campo.value.length + "/" + campo.maxLength;
        }

        campo.addEventListener("input", atualizar);
        atualizar();
    });
}

// Exceção 3a do UC05: o documento deve ser PDF ou imagem
function validarArquivos() {
    document.querySelectorAll("input[type=file][data-tipos]").forEach(function (campo) {
        var tipos = campo.dataset.tipos.split(",");

        campo.addEventListener("change", function () {
            var arquivo = campo.files[0];
            var valido = !arquivo || tipos.some(function (tipo) {
                return tipo.endsWith("/") ? arquivo.type.indexOf(tipo) === 0 : arquivo.type === tipo;
            });
            campo.setCustomValidity(valido ? "" : "Formato inválido.");
        });
    });
}

// Pré-visualização da foto de perfil antes de salvar
function previewFoto() {
    var campo = document.getElementById("foto");
    var preview = document.getElementById("foto-preview");
    if (!campo || !preview) { return; }

    campo.addEventListener("change", function () {
        var arquivo = campo.files[0];
        if (!arquivo || arquivo.type.indexOf("image/") !== 0) { return; }
        preview.innerHTML = "";
        var img = document.createElement("img");
        img.src = URL.createObjectURL(arquivo);
        img.alt = "Prévia da foto de perfil";
        preview.appendChild(img);
    });
}

// UC10: o campo de plano ajustado só aparece quando o especialista escolhe "Ajustar"
function alternarAjuste() {
    var campo = document.getElementById("campo-ajuste");
    if (!campo) { return; }
    var texto = campo.querySelector("textarea");

    document.querySelectorAll("input[name=decisao]").forEach(function (opcao) {
        opcao.addEventListener("change", function () {
            var ajustar = opcao.value === "Ajustado" && opcao.checked;
            campo.classList.toggle("d-none", !ajustar);
            texto.required = ajustar;
        });
    });
}
