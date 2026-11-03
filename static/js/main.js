document.addEventListener("DOMContentLoaded", function () {
    var ano = document.getElementById("ano");
    if (ano) { ano.textContent = new Date().getFullYear(); }

    marcarObrigatorios();
    validarFormularios();
    confirmarSenha();
    checarRegrasSenha();
    contarCaracteres();
    validarArquivos();
    previewFoto();
    alternarAjuste();
    abrirComTeclado();
});

// Cards clicáveis (ex.: treinos) também abrem com Enter ou espaço
function abrirComTeclado() {
    document.querySelectorAll("[role=button][data-bs-toggle]").forEach(function (card) {
        card.addEventListener("keydown", function (evento) {
            if (evento.key === "Enter" || evento.key === " ") {
                evento.preventDefault();
                card.click();
            }
        });
    });
}

// Coloca * no rótulo de todo campo obrigatório e a legenda antes do botão de enviar
function marcarObrigatorios() {
    document.querySelectorAll("form").forEach(function (form) {
        var temObrigatorio = false;

        form.querySelectorAll("[required]").forEach(function (campo) {
            var rotulo = campo.id ? form.querySelector("label[for='" + campo.id + "']") : null;
            if (rotulo && !rotulo.classList.contains("btn")) {
                rotulo.classList.add("pf-obrigatorio");
                temObrigatorio = true;
            }
        });

        var botao = form.querySelector("[type=submit]");
        if (!temObrigatorio || !botao) { return; }

        var legenda = document.createElement("p");
        legenda.className = "pf-legenda-obrigatorio";
        legenda.innerHTML = "<span>*</span> Campos obrigatórios";
        var corpoModal = form.querySelector(".modal-body");
        if (corpoModal) {
            legenda.classList.add("mt-3", "mb-0");
            corpoModal.appendChild(legenda);
            return;
        }
        var bloco = botao.closest(".d-grid, .d-flex") || botao;
        bloco.parentNode.insertBefore(legenda, bloco);
    });
}

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

// Item 6: regras da senha no cadastro marcadas enquanto o usuário digita
function checarRegrasSenha() {
    var lista = document.getElementById("regras-senha");
    var senha = document.getElementById("password");
    var confirmacao = document.getElementById("password_confirm");
    if (!lista || !senha) { return; }

    var regras = {
        tamanho: function () { return senha.value.length >= 8; },
        numeros: function () { return senha.value !== "" && !/^\d+$/.test(senha.value); },
        iguais: function () { return senha.value !== "" && confirmacao && senha.value === confirmacao.value; }
    };

    function atualizar() {
        Object.keys(regras).forEach(function (nome) {
            var item = lista.querySelector("[data-regra='" + nome + "']");
            if (!item) { return; }
            var ok = regras[nome]();
            item.classList.toggle("ok", ok);
            item.querySelector("i").className = ok ? "bi bi-check-circle-fill" : "bi bi-circle";
        });
    }

    senha.addEventListener("input", atualizar);
    if (confirmacao) { confirmacao.addEventListener("input", atualizar); }
    atualizar();
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
            campo.querySelector("label").classList.toggle("pf-obrigatorio", ajustar);
        });
    });
}
