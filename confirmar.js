const mensagem =
    document.getElementById(
        "mensagem"
    );

const conteudo =
    document.getElementById(
        "conteudoConfirmacao"
    );

const titulo =
    document.getElementById(
        "tituloReuniaoConfirmacao"
    );

const nome =
    document.getElementById(
        "nomeMembroConfirmacao"
    );

const data =
    document.getElementById(
        "dataReuniaoConfirmacao"
    );

const local =
    document.getElementById(
        "localReuniaoConfirmacao"
    );

const statusAtual =
    document.getElementById(
        "statusAtualConfirmacao"
    );

const btnConfirmar =
    document.getElementById(
        "btnConfirmarPresenca"
    );

const btnRecusar =
    document.getElementById(
        "btnNaoParticiparei"
    );

const areaJustificativa =
    document.getElementById(
        "areaJustificativa"
    );

const justificativa =
    document.getElementById(
        "justificativaAusencia"
    );

const btnEnviarJustificativa =
    document.getElementById(
        "btnEnviarJustificativa"
    );


const partesUrl =
    window.location.pathname
        .split("/")
        .filter(Boolean);


const token =
    partesUrl[
        partesUrl.length - 1
    ];


carregarConvocacao();


btnConfirmar.addEventListener(
    "click",
    function () {

        responderConvocacao(
            "CONFIRMADO",
            ""
        );
    }
);


btnRecusar.addEventListener(
    "click",
    function () {

        areaJustificativa.style.display =
            "block";

        mensagem.textContent =
            "Informe o motivo da ausência.";
    }
);


btnEnviarJustificativa.addEventListener(
    "click",
    function () {

        const texto =
            justificativa.value.trim();


        if (texto === "") {

            mensagem.textContent =
                "Informe a justificativa.";

            return;
        }


        responderConvocacao(
            "RECUSADO",
            texto
        );
    }
);


async function carregarConvocacao() {

    try {

        const resposta = await fetch(
            "/api/confirmar/" +
            encodeURIComponent(token)
        );


        const dados =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                dados.mensagem
            );
        }


        const convocacao =
            dados.convocacao;


        titulo.textContent =
            convocacao.titulo;


        nome.textContent =
            convocacao.nome;


        const dataObjeto =
            new Date(
                convocacao.data_hora
            );


        data.textContent =
            "Data: " +
            dataObjeto.toLocaleString(
                "pt-BR"
            );


        local.textContent =
            "Local: " +
            (
                convocacao.local
                || "Não informado"
            );


        statusAtual.textContent =
            "Situação atual: " +
            convocacao.status_confirmacao;


        if (
            convocacao.status_confirmacao
            === "CONFIRMADO"
        ) {

            mensagem.textContent =
                "Sua presença já está confirmada.";

        } else if (
            convocacao.status_confirmacao
            === "RECUSADO"
        ) {

            mensagem.textContent =
                "Sua ausência já foi registrada.";

        } else {

            mensagem.textContent =
                "Informe sua participação.";
        }


        conteudo.style.display =
            "block";


    } catch (erro) {

        mensagem.textContent =
            erro.message;


        console.error(
            "Erro ao carregar convite:",
            erro
        );
    }
}


async function responderConvocacao(
    status,
    textoJustificativa
) {

    try {

        const resposta = await fetch(
            "/api/confirmar/" +
            encodeURIComponent(token),
            {
                method: "PUT",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    status_confirmacao:
                        status,

                    justificativa:
                        textoJustificativa
                })
            }
        );


        const dados =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                dados.mensagem
            );
        }


        mensagem.textContent =
            dados.mensagem;


        statusAtual.textContent =
            "Situação atual: " +
            dados.resposta.status_confirmacao;


        btnConfirmar.disabled =
            true;

        btnRecusar.disabled =
            true;

        btnEnviarJustificativa.disabled =
            true;


        areaJustificativa.style.display =
            "none";


    } catch (erro) {

        mensagem.textContent =
            erro.message;


        console.error(
            "Erro ao responder convite:",
            erro
        );
    }
}