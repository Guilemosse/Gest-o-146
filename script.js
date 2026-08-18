const formulario = document.getElementById("formMembro");
const resultado = document.getElementById("resultado");
const listaMembros = document.getElementById("listaMembros");


formulario.addEventListener("submit", salvarMembro);


// Carrega os membros quando a página abre
carregarMembros();


// =========================================================
// CRIAR MEMBRO
// =========================================================

async function salvarMembro(event) {

    event.preventDefault();

    const nome =
    document
        .getElementById("nomeMembro")
        .value
        .trim();


    const email =
        document
            .getElementById("emailMembro")
            .value
            .trim();


    if (nome === "") {

        resultado.textContent =
            "Informe o nome do membro.";

        return;
    }


    const membro = {
        nome: nome,
        email: email
    };


try {

    const resposta = await fetch(
            "/api/membros",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(membro)
            }
        );


        const dados = await resposta.json();


        if (!resposta.ok) {
            throw new Error(dados.mensagem);
        }


        resultado.textContent =
            dados.mensagem;


        formulario.reset();


        await carregarMembros();


    } catch (erro) {

        console.error(
            "Erro ao cadastrar membro:",
            erro
        );


        resultado.textContent =
            "Erro ao cadastrar membro.";
    }
}


// =========================================================
// LISTAR MEMBROS
// =========================================================

async function carregarMembros() {

    try {

        const resposta = await fetch(
            "/api/membros"
        );

        const dados =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                dados.mensagem
                || "Erro ao carregar membros"
            );
        }


        listaMembros.innerHTML = "";


        if (
            !dados.membros
            || dados.membros.length === 0
        ) {

            listaMembros.textContent =
                "Nenhum membro cadastrado.";

            return;
        }


        dados.membros.forEach(
            function (membro) {

                const item =
                    document.createElement(
                        "li"
                    );


                const texto =
                    document.createElement(
                        "span"
                    );


                texto.textContent =
                    membro.id +
                    " - " +
                    membro.nome +
                    (
                        membro.email
                            ? " - " + membro.email
                            : " - Sem e-mail"
                    );


                // =====================================
                // BOTÃO EDITAR
                // =====================================

                const botaoEditar =
                    document.createElement(
                        "button"
                    );

                botaoEditar.type =
                    "button";

                botaoEditar.addEventListener(
    "click",
    async function () {

        const novoNome = window.prompt(
            "Nome do membro:",
            membro.nome
        );

        if (novoNome === null) {
            return;
        }


        const nomeTratado =
            novoNome.trim();


        if (nomeTratado === "") {

            window.alert(
                "O nome não pode ficar vazio."
            );

            return;
        }


        const novoEmail = window.prompt(
            "E-mail do membro:",
            membro.email || ""
        );

        if (novoEmail === null) {
            return;
        }


        const emailTratado =
            novoEmail.trim();


        try {

            const url =
                "/api/membros/" +
                String(membro.id);


            const resposta = await fetch(
                url,
                {
                    method: "PUT",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        nome: nomeTratado,
                        email: emailTratado
                    })
                }
            );


            const dados =
                await resposta.json();


            if (!resposta.ok) {

                throw new Error(
                    dados.mensagem
                    || "Erro ao atualizar membro"
                );
            }


            resultado.textContent =
                dados.mensagem;


            await carregarMembros();


        } catch (erro) {

            console.error(
                "Erro ao editar membro:",
                erro
            );


            resultado.textContent =
                erro.message;
        }
    }
);


                // =====================================
                // BOTÃO EXCLUIR
                // =====================================

                const botaoExcluir =
                    document.createElement(
                        "button"
                    );

                botaoExcluir.type =
                    "button";

                botaoExcluir.textContent =
                    "Excluir";


                botaoExcluir.addEventListener(
                    "click",
                    async function () {

                        const confirmar =
                            window.confirm(
                                "Excluir " +
                                membro.nome +
                                "?"
                            );


                        if (!confirmar) {
                            return;
                        }


                        try {

                            const respostaExcluir =
                                await fetch(
                                    "/api/membros/" +
                                    membro.id,
                                    {
                                        method: "DELETE"
                                    }
                                );


                            const dadosExcluir =
                                await respostaExcluir.json();


                            if (!respostaExcluir.ok) {

                                throw new Error(
                                    dadosExcluir.mensagem
                                );
                            }


                            await carregarMembros();


                        } catch (erro) {

                            console.error(
                                "Erro ao excluir membro:",
                                erro
                            );

                            alert(
                                erro.message
                            );
                        }
                    }
                );


                item.appendChild(
                    texto
                );


                item.appendChild(
                    document.createTextNode(" ")
                );


                item.appendChild(
                    botaoEditar
                );


                item.appendChild(
                    document.createTextNode(" ")
                );


                item.appendChild(
                    botaoExcluir
                );


                listaMembros.appendChild(
                    item
                );
            }
        );


    } catch (erro) {

        console.error(
            "Erro ao carregar membros:",
            erro
        );


        listaMembros.textContent =
            "Erro ao carregar membros.";
    }
}


// =========================================================
// EDITAR MEMBRO
// =========================================================

async function editarMembro(membro) {

    const novoNome = prompt(
        "Informe o novo nome:",
        membro.nome
    );


    if (novoNome === null) {
        return;
    }


    const nome = novoNome.trim();


    if (nome === "") {

        alert(
            "O nome não pode ficar vazio."
        );

        return;
    }


    try {

        const resposta = await fetch(
            "/api/membros/" + membro.id,
            {
                method: "PUT",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                nome: nome,
                email: email
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


        resultado.textContent =
            dados.mensagem;


        await carregarMembros();


    } catch (erro) {

        console.error(
            "Erro ao editar membro:",
            erro
        );


        resultado.textContent =
            "Erro ao editar membro.";
    }
}


// =========================================================
// EXCLUIR MEMBRO
// =========================================================

async function excluirMembro(membro) {

    const confirmar = confirm(
        "Deseja realmente excluir " +
        membro.nome +
        "?"
    );


    if (!confirmar) {
        return;
    }


    try {

        const resposta = await fetch(
            "/api/membros/" + membro.id,
            {
                method: "DELETE"
            }
        );


        const dados =
            await resposta.json();


        if (!resposta.ok) {
            throw new Error(
                dados.mensagem
            );
        }


        resultado.textContent =
            dados.mensagem;


        await carregarMembros();


    } catch (erro) {

        console.error(
            "Erro ao excluir membro:",
            erro
        );


        resultado.textContent =
            "Erro ao excluir membro.";
    }
}

// =========================================================
// REUNIÕES
// =========================================================

const formReuniao =
    document.getElementById("formReuniao");

const resultadoReuniao =
    document.getElementById("resultadoReuniao");

const listaReunioes =
    document.getElementById("listaReunioes");


const areaParticipantes =
    document.getElementById("areaParticipantes");

const tituloParticipantes =
    document.getElementById("tituloParticipantes");

const selectMembroParticipante =
    document.getElementById(
        "selectMembroParticipante"
    );

const btnAdicionarParticipante =
    document.getElementById(
        "btnAdicionarParticipante"
    );

const resultadoParticipante =
    document.getElementById(
        "resultadoParticipante"
    );

const listaParticipantes =
    document.getElementById(
        "listaParticipantes"
    );


let reuniaoSelecionadaId = null;


formReuniao.addEventListener(
    "submit",
    salvarReuniao
);


btnAdicionarParticipante.addEventListener(
    "click",
    adicionarParticipante
);


// Carrega reuniões ao abrir a página
carregarReunioes();

// =========================================================
// CRIAR REUNIÃO
// =========================================================

async function salvarReuniao(event) {

    async function salvarReuniaoUnica(
    titulo,
    objetivo,
    local
) {

    const data =
        document
            .getElementById("dataReuniao")
            .value;


    const hora =
        document
            .getElementById("horaReuniao")
            .value;


    if (
        data === ""
        || hora === ""
    ) {

        resultadoReuniao.textContent =
            "Data e hora são obrigatórias.";

        return;
    }


    const reuniao = {

        titulo: titulo,
        objetivo: objetivo,

        data_hora:
            data + " " + hora,

        local: local
    };


    try {

        const resposta = await fetch(
            "/api/reunioes",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify(
                    reuniao
                )
            }
        );


        const dados =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                dados.mensagem
            );
        }


        resultadoReuniao.textContent =
            dados.mensagem;


        formReuniao.reset();


        atualizarTipoReuniao();


        await carregarReunioes();


    } catch (erro) {

        console.error(
            "Erro ao criar reunião:",
            erro
        );


        resultadoReuniao.textContent =
            erro.message;
    }
}

    event.preventDefault();


    const tipoReuniao =
        document.querySelector(
            'input[name="tipoReuniao"]:checked'
        ).value;


    const titulo =
        document
            .getElementById("tituloReuniao")
            .value
            .trim();


    const objetivo =
        document
            .getElementById("objetivoReuniao")
            .value
            .trim();


    const local =
        document
            .getElementById("localReuniao")
            .value
            .trim();


    if (titulo === "") {

        resultadoReuniao.textContent =
            "O título é obrigatório.";

        return;
    }


    if (tipoReuniao === "UNICA") {

        await salvarReuniaoUnica(
            titulo,
            objetivo,
            local
        );

        return;
    }


    await salvarReuniaoRecorrente(
        titulo,
        objetivo,
        local
    );
}

// =========================================================
// LISTAR REUNIÕES
// =========================================================

async function carregarReunioes() {

    try {

        const resposta =
            await fetch(
                "/api/reunioes"
            );


        const dados =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                "Erro ao carregar reuniões"
            );
        }


        listaReunioes.innerHTML = "";


        dados.reunioes.forEach(
            function(reuniao) {

                const bloco =
                    document.createElement(
                        "div"
                    );


                const titulo =
                    document.createElement(
                        "h4"
                    );


                titulo.textContent =
                    reuniao.titulo;


                const data =
                    document.createElement(
                        "p"
                    );


                const dataObjeto =
                    new Date(
                        reuniao.data_hora
                    );


                data.textContent =
                    "Data: " +
                    dataObjeto.toLocaleString(
                        "pt-BR"
                    );


                const local =
                    document.createElement(
                        "p"
                    );


                local.textContent =
                    "Local: " +
                    (
                        reuniao.local ||
                        "Não informado"
                    );


                const status =
                    document.createElement(
                        "p"
                    );


                status.textContent =
                    "Status: " +
                    reuniao.status;


                const botaoParticipantes =
                    document.createElement(
                        "button"
                    );


                botaoParticipantes.textContent =
                    "Participantes";


                botaoParticipantes.addEventListener(
                    "click",
                    function() {

                        abrirParticipantes(
                            reuniao
                        );

                    }
                );


                bloco.appendChild(
                    titulo
                );

                bloco.appendChild(
                    data
                );

                bloco.appendChild(
                    local
                );

                bloco.appendChild(
                    status
                );

                bloco.appendChild(
                    botaoParticipantes
                );


                listaReunioes.appendChild(
                    bloco
                );
            }
        );


    } catch (erro) {

        console.error(
            "Erro ao carregar reuniões:",
            erro
        );
    }
}

// =========================================================
// ABRIR PARTICIPANTES
// =========================================================

async function abrirParticipantes(
    reuniao
) {

    reuniaoSelecionadaId =
        reuniao.id;


    tituloParticipantes.textContent =
        "Participantes - " +
        reuniao.titulo;


    areaParticipantes.style.display =
        "block";


    resultadoParticipante.textContent =
        "";


    await carregarMembrosParaParticipantes();

    await carregarParticipantes();
}

// =========================================================
// CARREGAR MEMBROS NO SELECT
// =========================================================

async function carregarMembrosParaParticipantes() {

    try {

        const resposta =
            await fetch(
                "/api/membros"
            );


        const dados =
            await resposta.json();


        selectMembroParticipante.innerHTML =
            '<option value="">Selecione...</option>';


        dados.membros.forEach(
            function(membro) {

                const opcao =
                    document.createElement(
                        "option"
                    );


                opcao.value =
                    membro.id;


                opcao.textContent =
                    membro.nome;


                selectMembroParticipante.appendChild(
                    opcao
                );
            }
        );


    } catch (erro) {

        console.error(
            "Erro ao carregar membros:",
            erro
        );
    }
}

// =========================================================
// ADICIONAR PARTICIPANTE
// =========================================================

async function adicionarParticipante() {

    if (reuniaoSelecionadaId === null) {

        return;
    }


    const membroId =
        selectMembroParticipante.value;


    if (membroId === "") {

        resultadoParticipante.textContent =
            "Selecione um membro.";

        return;
    }


    try {

        const resposta = await fetch(
            "/api/reunioes/" +
            reuniaoSelecionadaId +
            "/participantes",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    membro_id:
                        Number(membroId)
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


        resultadoParticipante.textContent =
            dados.mensagem;


        selectMembroParticipante.value =
            "";


        await carregarParticipantes();


    } catch (erro) {

        console.error(
            "Erro ao adicionar participante:",
            erro
        );


        resultadoParticipante.textContent =
            erro.message;
    }
}

// =========================================================
// LISTAR PARTICIPANTES
// =========================================================

async function carregarParticipantes() {

    if (reuniaoSelecionadaId === null) {
        return;
    }


    try {

        const resposta = await fetch(
            "/api/reunioes/" +
            reuniaoSelecionadaId +
            "/participantes"
        );


        const dados =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                "Erro ao carregar participantes"
            );
        }


        listaParticipantes.innerHTML =
            "";


        dados.participantes.forEach(
    function(participante) {

        const bloco =
            document.createElement("div");


        const nome =
            document.createElement("h4");


        nome.textContent =
            participante.nome;


        const confirmacao =
            document.createElement("p");


        confirmacao.textContent =
            "Confirmação: " +
            participante.status_confirmacao;


        const presenca =
            document.createElement("p");


        presenca.textContent =
            "Presença: " +
            participante.status_presenca;


        const justificativa =
            document.createElement("p");


        if (participante.justificativa) {

            justificativa.textContent =
                "Justificativa: " +
                participante.justificativa;

        }


        // =============================================
        // BOTÃO CONFIRMAR
        // =============================================

        const botaoConfirmar =
            document.createElement("button");


        botaoConfirmar.textContent =
            "Confirmar";


        botaoConfirmar.addEventListener(
            "click",
            function() {

                responderParticipacao(
                    participante,
                    "CONFIRMADO"
                );

            }
        );


        // =============================================
        // BOTÃO NÃO PARTICIPAREI
        // =============================================

        const botaoRecusar =
            document.createElement("button");


        botaoRecusar.textContent =
            "Não participarei";


        botaoRecusar.addEventListener(
            "click",
            function() {

                responderParticipacao(
                    participante,
                    "RECUSADO"
                );

            }
        );


        // =============================================
        // BOTÃO PRESENTE
        // =============================================

        const botaoPresente =
            document.createElement("button");


        botaoPresente.textContent =
            "Presente";


        botaoPresente.addEventListener(
            "click",
            function() {

                registrarPresenca(
                    participante,
                    "PRESENTE"
                );

            }
        );


        // =============================================
        // BOTÃO AUSENTE
        // =============================================

        const botaoAusente =
            document.createElement("button");


        botaoAusente.textContent =
            "Ausente";


        botaoAusente.addEventListener(
            "click",
            function() {

                registrarPresenca(
                    participante,
                    "AUSENTE"
                );

            }
        );


        bloco.appendChild(nome);
        bloco.appendChild(confirmacao);
        bloco.appendChild(presenca);


        if (participante.justificativa) {
            bloco.appendChild(justificativa);
        }


        bloco.appendChild(botaoConfirmar);
        bloco.appendChild(botaoRecusar);
        bloco.appendChild(botaoPresente);
        bloco.appendChild(botaoAusente);


        listaParticipantes.appendChild(
            bloco
        );
    }
);

    } catch (erro) {

        console.error(
            "Erro ao carregar participantes:",
            erro
        );
    }
}

async function responderParticipacao(
    participante,
    status
) {

    let justificativa = "";


    if (status === "RECUSADO") {

        justificativa = prompt(
            "Informe a justificativa da ausência:"
        );


        if (justificativa === null) {
            return;
        }


        justificativa =
            justificativa.trim();


        if (justificativa === "") {

            alert(
                "A justificativa é obrigatória."
            );

            return;
        }
    }


    try {

        const resposta = await fetch(
            "/api/reunioes/" +
            reuniaoSelecionadaId +
            "/participantes/" +
            participante.membro_id +
            "/confirmacao",
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
                        justificativa
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


        resultadoParticipante.textContent =
            dados.mensagem;


        await carregarParticipantes();


    } catch (erro) {

        console.error(
            "Erro na confirmação:",
            erro
        );


        resultadoParticipante.textContent =
            erro.message;
    }
}

async function registrarPresenca(
    participante,
    status
) {

    try {

        const resposta = await fetch(
            "/api/reunioes/" +
            reuniaoSelecionadaId +
            "/participantes/" +
            participante.membro_id +
            "/presenca",
            {
                method: "PUT",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    status_presenca:
                        status
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


        resultadoParticipante.textContent =
            dados.mensagem;


        await carregarParticipantes();


    } catch (erro) {

        console.error(
            "Erro ao registrar presença:",
            erro
        );


        resultadoParticipante.textContent =
            erro.message;
    }
}

async function salvarReuniaoRecorrente(
    titulo,
    objetivo,
    local
) {

    const tipoRecorrencia =
        document
            .getElementById(
                "tipoRecorrencia"
            )
            .value;


    const diaSemana =
        Number(
            document
                .getElementById(
                    "diaSemanaRecorrencia"
                )
                .value
        );


    const hora =
        document
            .getElementById(
                "horaRecorrencia"
            )
            .value;


    const dataInicio =
        document
            .getElementById(
                "dataInicioRecorrencia"
            )
            .value;


    const dataFim =
        document
            .getElementById(
                "dataFimRecorrencia"
            )
            .value;


    const quantidade =
        Number(
            document
                .getElementById(
                    "quantidadeRecorrencia"
                )
                .value
        );


    let ordemMes = null;


    if (
        tipoRecorrencia
        === "MENSAL_DIA_SEMANA"
    ) {

        ordemMes =
            Number(
                document
                    .getElementById(
                        "ordemMesRecorrencia"
                    )
                    .value
            );
    }


    if (
        hora === ""
        || dataInicio === ""
    ) {

        resultadoReuniao.textContent =
            "Hora e data inicial são obrigatórias.";

        return;
    }


    const serie = {

        titulo: titulo,
        objetivo: objetivo,
        local: local,

        tipo_recorrencia:
            tipoRecorrencia,

        dia_semana:
            diaSemana,

        ordem_mes:
            ordemMes,

        hora: hora,

        data_inicio:
            dataInicio,

        data_fim:
            dataFim,

        quantidade:
            quantidade
    };


    try {

        const resposta = await fetch(
            "/api/series-reunioes",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify(
                    serie
                )
            }
        );


        const dados =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                dados.mensagem
            );
        }


        resultadoReuniao.textContent =
            dados.mensagem +
            " - " +
            dados.ocorrencias_criadas.length +
            " reuniões criadas.";


        formReuniao.reset();


        atualizarTipoReuniao();

        atualizarTipoRecorrencia();


        await carregarReunioes();


    } catch (erro) {

        console.error(
            "Erro ao criar recorrência:",
            erro
        );


        resultadoReuniao.textContent =
            erro.message;
    }
}

function atualizarTipoReuniao() {

    const tipo =
        document.querySelector(
            'input[name="tipoReuniao"]:checked'
        ).value;


    const camposUnica =
        document.getElementById(
            "camposReuniaoUnica"
        );


    const camposRecorrente =
        document.getElementById(
            "camposReuniaoRecorrente"
        );


    if (tipo === "UNICA") {

        camposUnica.style.display =
            "block";

        camposRecorrente.style.display =
            "none";

    } else {

        camposUnica.style.display =
            "none";

        camposRecorrente.style.display =
            "block";
    }
}

function atualizarTipoRecorrencia() {

    const tipoRecorrencia =
        document
            .getElementById(
                "tipoRecorrencia"
            )
            .value;


    const campoOrdem =
        document.getElementById(
            "campoOrdemMes"
        );


    if (
        tipoRecorrencia
        === "MENSAL_DIA_SEMANA"
    ) {

        campoOrdem.style.display =
            "block";

    } else {

        campoOrdem.style.display =
            "none";
    }
}

document
    .querySelectorAll(
        'input[name="tipoReuniao"]'
    )
    .forEach(
        function(radio) {

            radio.addEventListener(
                "change",
                atualizarTipoReuniao
            );
        }
    );


document
    .getElementById(
        "tipoRecorrencia"
    )
    .addEventListener(
        "change",
        atualizarTipoRecorrencia
    );


atualizarTipoReuniao();

atualizarTipoRecorrencia();

// =========================================================
// SÉRIES RECORRENTES
// =========================================================

const btnAtualizarSeries =
    document.getElementById(
        "btnAtualizarSeries"
    );

const listaSeries =
    document.getElementById(
        "listaSeries"
    );

const areaParticipantesSerie =
    document.getElementById(
        "areaParticipantesSerie"
    );

const tituloParticipantesSerie =
    document.getElementById(
        "tituloParticipantesSerie"
    );

const selectMembroSerie =
    document.getElementById(
        "selectMembroSerie"
    );

const btnAdicionarParticipanteSerie =
    document.getElementById(
        "btnAdicionarParticipanteSerie"
    );

const resultadoParticipanteSerie =
    document.getElementById(
        "resultadoParticipanteSerie"
    );

const listaParticipantesSerie =
    document.getElementById(
        "listaParticipantesSerie"
    );


let serieSelecionadaId = null;


btnAtualizarSeries.addEventListener(
    "click",
    carregarSeries
);


btnAdicionarParticipanteSerie.addEventListener(
    "click",
    adicionarParticipanteSerie
);


carregarSeries();

async function carregarSeries() {

    try {

        const resposta =
            await fetch(
                "/api/series-reunioes"
            );


        const dados =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                "Erro ao carregar séries"
            );
        }


        listaSeries.innerHTML = "";


        dados.series.forEach(
            function(serie) {

                const bloco =
                    document.createElement(
                        "div"
                    );


                const titulo =
                    document.createElement(
                        "h4"
                    );


                titulo.textContent =
                    serie.titulo;


                const tipo =
                    document.createElement(
                        "p"
                    );


                tipo.textContent =
                    "Recorrência: " +
                    serie.tipo_recorrencia;


                const inicio =
                    document.createElement(
                        "p"
                    );


                inicio.textContent =
                    "Início: " +
                    serie.data_inicio;


                const hora =
                    document.createElement(
                        "p"
                    );


                hora.textContent =
                    "Hora: " +
                    serie.hora;


                const botao =
                    document.createElement(
                        "button"
                    );


                botao.textContent =
                    "Participantes da série";


                botao.addEventListener(
                    "click",
                    function() {

                        abrirParticipantesSerie(
                            serie
                        );

                    }
                );


                bloco.appendChild(
                    titulo
                );

                bloco.appendChild(
                    tipo
                );

                bloco.appendChild(
                    inicio
                );

                bloco.appendChild(
                    hora
                );

                bloco.appendChild(
                    botao
                );


                listaSeries.appendChild(
                    bloco
                );
            }
        );


    } catch (erro) {

        console.error(
            "Erro ao carregar séries:",
            erro
        );
    }
}

async function abrirParticipantesSerie(
    serie
) {

    serieSelecionadaId =
        serie.id;


    tituloParticipantesSerie.textContent =
        "Participantes - " +
        serie.titulo;


    areaParticipantesSerie.style.display =
        "block";


    resultadoParticipanteSerie.textContent =
        "";


    await carregarMembrosParaSerie();

    await carregarParticipantesSerie();
}

async function carregarMembrosParaSerie() {

    try {

        const resposta =
            await fetch(
                "/api/membros"
            );


        const dados =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                "Erro ao carregar membros"
            );
        }


        selectMembroSerie.innerHTML =
            '<option value="">Selecione...</option>';


        dados.membros.forEach(
            function(membro) {

                const opcao =
                    document.createElement(
                        "option"
                    );


                opcao.value =
                    membro.id;


                opcao.textContent =
                    membro.nome;


                selectMembroSerie.appendChild(
                    opcao
                );
            }
        );


    } catch (erro) {

        console.error(
            "Erro ao carregar membros da série:",
            erro
        );
    }
}

async function adicionarParticipanteSerie() {

    if (serieSelecionadaId === null) {

        return;
    }


    const membroId =
        selectMembroSerie.value;


    if (membroId === "") {

        resultadoParticipanteSerie.textContent =
            "Selecione um membro.";

        return;
    }


    try {

        const resposta = await fetch(
            "/api/series-reunioes/" +
            serieSelecionadaId +
            "/participantes",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    membro_id:
                        Number(membroId)
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


        resultadoParticipanteSerie.textContent =
            dados.mensagem +
            " - " +
            dados.reunioes_atualizadas +
            " reuniões atualizadas.";


        selectMembroSerie.value =
            "";


        await carregarParticipantesSerie();


    } catch (erro) {

        console.error(
            "Erro ao adicionar participante à série:",
            erro
        );


        resultadoParticipanteSerie.textContent =
            erro.message;
    }
}

async function carregarParticipantesSerie() {

    if (serieSelecionadaId === null) {

        return;
    }


    try {

        const resposta = await fetch(
            "/api/series-reunioes/" +
            serieSelecionadaId +
            "/participantes"
        );


        const dados =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                "Erro ao carregar participantes da série"
            );
        }


        listaParticipantesSerie.innerHTML =
            "";


        if (
            dados.participantes.length === 0
        ) {

            listaParticipantesSerie.textContent =
                "Nenhum participante vinculado.";

            return;
        }


        dados.participantes.forEach(
            function(participante) {

                const bloco =
                    document.createElement(
                        "div"
                    );


                const nome =
                    document.createElement(
                        "strong"
                    );


                nome.textContent =
                    participante.nome;


                bloco.appendChild(
                    nome
                );


                listaParticipantesSerie.appendChild(
                    bloco
                );
            }
        );


    } catch (erro) {

        console.error(
            "Erro ao carregar participantes da série:",
            erro
        );
    }
}

// =========================================================
// CONVITES DAS REUNIÕES
// =========================================================

const selectReuniaoConvites =
    document.getElementById(
        "selectReuniaoConvites"
    );

const btnGerarConvites =
    document.getElementById(
        "btnGerarConvites"
    );

const resultadoConvites =
    document.getElementById(
        "resultadoConvites"
    );

const listaConvites =
    document.getElementById(
        "listaConvites"
    );


btnGerarConvites.addEventListener(
    "click",
    gerarVisualizarConvites
);


carregarReunioesParaConvites();
async function carregarReunioesParaConvites() {

    try {

        const resposta =
            await fetch(
                "/api/reunioes"
            );


        const dados =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                "Erro ao carregar reuniões"
            );
        }


        selectReuniaoConvites.innerHTML =
            '<option value="">Selecione uma reunião...</option>';


        dados.reunioes.forEach(
            function (reuniao) {

                const opcao =
                    document.createElement(
                        "option"
                    );


                opcao.value =
                    reuniao.id;


                const dataObjeto =
                    new Date(
                        reuniao.data_hora
                    );


                opcao.textContent =
                    reuniao.titulo +
                    " - " +
                    dataObjeto.toLocaleString(
                        "pt-BR"
                    );


                selectReuniaoConvites.appendChild(
                    opcao
                );
            }
        );


    } catch (erro) {

        console.error(
            "Erro ao carregar reuniões para convites:",
            erro
        );


        resultadoConvites.textContent =
            erro.message;
    }
}

async function gerarVisualizarConvites() {

    const reuniaoId =
        selectReuniaoConvites.value;


    if (reuniaoId === "") {

        resultadoConvites.textContent =
            "Selecione uma reunião.";

        return;
    }


    resultadoConvites.textContent =
        "Gerando convites...";


    listaConvites.innerHTML =
        "";


    try {

        const resposta = await fetch(
            "/api/reunioes/" +
            reuniaoId +
            "/gerar-links-confirmacao",
            {
                method: "POST"
            }
        );


        const dados =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                dados.mensagem
            );
        }


        if (dados.links.length === 0) {

            resultadoConvites.textContent =
                "Esta reunião ainda não possui participantes.";

            return;
        }


        resultadoConvites.textContent =
            dados.links.length +
            " convite(s) disponível(is).";


        mostrarConvites(
            dados.links
        );


    } catch (erro) {

        console.error(
            "Erro ao gerar convites:",
            erro
        );


        resultadoConvites.textContent =
            erro.message;
    }
}

function mostrarConvites(
    convites
) {

    listaConvites.innerHTML =
        "";


    convites.forEach(
        function (convite) {

            const bloco =
                document.createElement(
                    "div"
                );


            bloco.style.marginBottom =
                "20px";


            const nome =
                document.createElement(
                    "h4"
                );


            nome.textContent =
                convite.nome;


            const linkCompleto =
                window.location.origin +
                convite.link;


            const campoLink =
                document.createElement(
                    "input"
                );


            campoLink.type =
                "text";


            campoLink.value =
                linkCompleto;


            campoLink.readOnly =
                true;


            campoLink.style.width =
                "70%";


            const botaoCopiar =
                document.createElement(
                    "button"
                );


            botaoCopiar.type =
                "button";


            botaoCopiar.textContent =
                "Copiar link";


            botaoCopiar.addEventListener(
                "click",
                async function () {

                    await copiarLinkConvite(
                        linkCompleto,
                        botaoCopiar
                    );
                }
            );


            const botaoAbrir =
                document.createElement(
                    "button"
                );


            botaoAbrir.type =
                "button";


            botaoAbrir.textContent =
                "Abrir convite";


            botaoAbrir.addEventListener(
                "click",
                function () {

                    window.open(
                        linkCompleto,
                        "_blank"
                    );
                }
            );


            bloco.appendChild(
                nome
            );

            bloco.appendChild(
                campoLink
            );

            bloco.appendChild(
                botaoCopiar
            );

            bloco.appendChild(
                botaoAbrir
            );


            listaConvites.appendChild(
                bloco
            );
        }
    );
}

async function copiarLinkConvite(
    link,
    botao
) {

    try {

        await navigator.clipboard.writeText(
            link
        );


        const textoAnterior =
            botao.textContent;


        botao.textContent =
            "Copiado!";


        setTimeout(
            function () {

                botao.textContent =
                    textoAnterior;
            },
            1500
        );


    } catch (erro) {

        console.error(
            "Erro ao copiar link:",
            erro
        );


        resultadoConvites.textContent =
            "Não foi possível copiar automaticamente. " +
            "Selecione o endereço e copie manualmente.";
    }
}

// =========================================================
// PAINEL DE NOTIFICAÇÕES
// =========================================================

const totalNotificacoesPendentes =
    document.getElementById(
        "totalNotificacoesPendentes"
    );

const totalNotificacoesEnviadas =
    document.getElementById(
        "totalNotificacoesEnviadas"
    );

const totalNotificacoesErro =
    document.getElementById(
        "totalNotificacoesErro"
    );

const totalNotificacoesSemDestinatario =
    document.getElementById(
        "totalNotificacoesSemDestinatario"
    );

const btnAtualizarNotificacoes =
    document.getElementById(
        "btnAtualizarNotificacoes"
    );

const btnProcessarFila =
    document.getElementById(
        "btnProcessarFila"
    );

const resultadoProcessamentoFila =
    document.getElementById(
        "resultadoProcessamentoFila"
    );

const listaNotificacoes =
    document.getElementById(
        "listaNotificacoes"
    );


btnAtualizarNotificacoes.addEventListener(
    "click",
    carregarNotificacoes
);


btnProcessarFila.addEventListener(
    "click",
    processarFilaNotificacoes
);

async function carregarNotificacoes() {

    try {

        const resposta =
            await fetch(
                "/api/notificacoes"
            );


        const dados =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                dados.mensagem
                || "Erro ao carregar notificações"
            );
        }


        mostrarNotificacoes(
            dados.notificacoes
        );


    } catch (erro) {

        console.error(
            "Erro ao carregar notificações:",
            erro
        );


        listaNotificacoes.textContent =
            "Não foi possível carregar as notificações.";
    }
}

function mostrarNotificacoes(
    notificacoes
) {

    listaNotificacoes.innerHTML =
        "";


    let pendentes = 0;
    let enviadas = 0;
    let erros = 0;
    let semDestinatario = 0;


    notificacoes.forEach(
        function (notificacao) {

            if (
                notificacao.status
                === "PENDENTE"
            ) {

                pendentes += 1;
            }


            if (
                notificacao.status
                === "ENVIADO"
            ) {

                enviadas += 1;
            }


            if (
                notificacao.status
                === "ERRO"
            ) {

                erros += 1;
            }


            if (
                !notificacao.destinatario
            ) {

                semDestinatario += 1;
            }


            const bloco =
                document.createElement(
                    "div"
                );


            bloco.style.marginBottom =
                "20px";


            const titulo =
                document.createElement(
                    "h4"
                );


            titulo.textContent =
                notificacao.membro
                || "Membro não identificado";


            const reuniao =
                document.createElement(
                    "p"
                );


            reuniao.textContent =
                "Reunião: " +
                (
                    notificacao.reuniao
                    || "Não informada"
                );


            const tipo =
                document.createElement(
                    "p"
                );


            tipo.textContent =
                "Tipo: " +
                notificacao.tipo +
                " | Canal: " +
                notificacao.canal;


            const destinatario =
                document.createElement(
                    "p"
                );


            destinatario.textContent =
                "Destinatário: " +
                (
                    notificacao.destinatario
                    || "Sem e-mail"
                );


            const status =
                document.createElement(
                    "strong"
                );


            status.textContent =
                "Status: " +
                notificacao.status;


            const tentativas =
                document.createElement(
                    "p"
                );


            tentativas.textContent =
                "Tentativas: " +
                notificacao.tentativas;


            bloco.appendChild(
                titulo
            );

            bloco.appendChild(
                reuniao
            );

            bloco.appendChild(
                tipo
            );

            bloco.appendChild(
                destinatario
            );

            bloco.appendChild(
                status
            );

            bloco.appendChild(
                tentativas
            );


            if (notificacao.erro) {

                const erro =
                    document.createElement(
                        "p"
                    );


                erro.textContent =
                    "Erro: " +
                    notificacao.erro;


                bloco.appendChild(
                    erro
                );
            }


            listaNotificacoes.appendChild(
                bloco
            );
        }
    );


    totalNotificacoesPendentes.textContent =
        pendentes;

    totalNotificacoesEnviadas.textContent =
        enviadas;

    totalNotificacoesErro.textContent =
        erros;

    totalNotificacoesSemDestinatario.textContent =
        semDestinatario;


    if (
        notificacoes.length === 0
    ) {

        listaNotificacoes.textContent =
            "Nenhuma notificação cadastrada.";
    }
}

async function processarFilaNotificacoes() {

    const confirmar =
        window.confirm(
            "Deseja processar as notificações pendentes?"
        );


    if (!confirmar) {
        return;
    }


    btnProcessarFila.disabled =
        true;


    resultadoProcessamentoFila.textContent =
        "Processando fila...";


    try {

        const resposta = await fetch(
            "/api/notificacoes/processar-fila",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    limite: 10
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


        resultadoProcessamentoFila.textContent =
            "Processamento concluído. " +
            "Selecionadas: " +
            dados.selecionadas +
            " | Enviadas: " +
            dados.enviadas +
            " | Erros: " +
            dados.erros +
            " | Sem destinatário: " +
            dados.pendentes_sem_destinatario;


        await carregarNotificacoes();


    } catch (erro) {

        console.error(
            "Erro ao processar fila:",
            erro
        );


        resultadoProcessamentoFila.textContent =
            erro.message;


    } finally {

        btnProcessarFila.disabled =
            false;
    }
}
carregarNotificacoes();

const btnExecutarCicloAutomatico =
    document.getElementById(
        "btnExecutarCicloAutomatico"
    );

    btnExecutarCicloAutomatico.addEventListener(
    "click",
    executarCicloAutomatico
);

async function executarCicloAutomatico() {

    const confirmar =
        window.confirm(
            "Deseja verificar lembretes e processar a fila?"
        );


    if (!confirmar) {
        return;
    }


    btnExecutarCicloAutomatico.disabled =
        true;


    resultadoProcessamentoFila.textContent =
        "Executando ciclo automático...";


    try {

        // =============================================
        // 1. GERAR LEMBRETES DE 24 HORAS
        // =============================================

        const respostaLembretes =
            await fetch(
                "/api/notificacoes/lembretes/gerar",
                {
                    method: "POST"
                }
            );


        const dadosLembretes =
            await respostaLembretes.json();


        if (!respostaLembretes.ok) {

            throw new Error(
                dadosLembretes.mensagem
                || "Erro ao gerar lembretes"
            );
        }


        // =============================================
        // 2. PROCESSAR FILA
        // =============================================

        const respostaFila =
            await fetch(
                "/api/notificacoes/processar-fila",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        limite: 10
                    })
                }
            );


        const dadosFila =
            await respostaFila.json();


        if (!respostaFila.ok) {

            throw new Error(
                dadosFila.mensagem
                || "Erro ao processar fila"
            );
        }


        // =============================================
        // 3. RESULTADO DO CICLO
        // =============================================

        resultadoProcessamentoFila.textContent =
            "Ciclo concluído. " +
            "Participantes avaliados: " +
            dadosLembretes.participantes_avaliados +
            " | Novos lembretes: " +
            dadosLembretes.lembretes_criados +
            " | Selecionadas para envio: " +
            dadosFila.selecionadas +
            " | Enviadas: " +
            dadosFila.enviadas +
            " | Erros: " +
            dadosFila.erros +
            " | Sem destinatário: " +
            dadosFila.pendentes_sem_destinatario;


        // =============================================
        // 4. ATUALIZAR PAINEL
        // =============================================

        await carregarNotificacoes();


    } catch (erro) {

        console.error(
            "Erro no ciclo automático:",
            erro
        );


        resultadoProcessamentoFila.textContent =
            erro.message;


    } finally {

        btnExecutarCicloAutomatico.disabled =
            false;
    }
}

// =====================================================
// CONFIGURAÇÕES DE LEMBRETES
// =====================================================


async function carregarConfiguracoesLembrete() {

    const container =
        document.getElementById(
            "listaConfiguracoesLembrete"
        );


    const resultado =
        document.getElementById(
            "resultadoConfiguracoesLembrete"
        );


    if (!container || !resultado) {
        return;
    }


    resultado.textContent =
        "Carregando configurações...";


    try {

        const resposta =
            await fetch(
                "/api/configuracoes-lembrete"
            );


        const dados =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                dados.mensagem
                || "Erro ao carregar configurações"
            );
        }


        mostrarConfiguracoesLembrete(
            dados.configuracoes
        );


        resultado.textContent =
            "Configurações carregadas.";


    } catch (erro) {

        console.error(
            "Erro ao carregar configurações:",
            erro
        );


        resultado.textContent =
            erro.message;
    }
}

function mostrarConfiguracoesLembrete(
    configuracoes
) {

    const container =
        document.getElementById(
            "listaConfiguracoesLembrete"
        );


    container.innerHTML = "";


    for (const configuracao of configuracoes) {

        const item =
            document.createElement(
                "div"
            );


        item.className =
            "config-lembrete-item";


        const info =
            document.createElement(
                "div"
            );


        info.className =
            "config-lembrete-info";


        const nome =
            document.createElement(
                "span"
            );


        nome.className =
            "config-lembrete-nome";


        nome.textContent =
            configuracao.nome;


        const codigo =
            document.createElement(
                "span"
            );


        codigo.className =
            "config-lembrete-codigo";


        codigo.textContent =
            "Regra: "
            + configuracao.codigo;


        const toggle =
            document.createElement(
                "input"
            );


        toggle.type =
            "checkbox";


        toggle.className =
            "config-lembrete-toggle";


        toggle.checked =
            Boolean(
                configuracao.ativo
            );


        toggle.addEventListener(
            "change",
            async function () {

                await atualizarConfiguracaoLembrete(
                    configuracao.id,
                    toggle.checked,
                    toggle
                );
            }
        );


        info.appendChild(
            nome
        );


        info.appendChild(
            codigo
        );


        item.appendChild(
            info
        );


        item.appendChild(
            toggle
        );


        container.appendChild(
            item
        );
    }
}

async function atualizarConfiguracaoLembrete(
    configuracaoId,
    ativo,
    controle
) {

    const resultado =
        document.getElementById(
            "resultadoConfiguracoesLembrete"
        );


    controle.disabled =
        true;


    resultado.textContent =
        "Salvando configuração...";


    try {

        const url =
            "/api/configuracoes-lembrete/"
            + String(configuracaoId);


        const resposta =
            await fetch(
                url,
                {
                    method: "PUT",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        ativo: ativo
                    })
                }
            );


        const dados =
            await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                dados.mensagem
                || "Erro ao salvar configuração"
            );
        }


        const estado =
            ativo
                ? "ATIVADA"
                : "DESATIVADA";


        resultado.textContent =
            dados.configuracao.nome
            + " — "
            + estado;


    } catch (erro) {

        console.error(
            "Erro ao atualizar configuração:",
            erro
        );


        controle.checked =
            !ativo;


        resultado.textContent =
            erro.message;


    } finally {

        controle.disabled =
            false;
    }
}

document.addEventListener(
    "DOMContentLoaded",
    function () {

        carregarConfiguracoesLembrete();
    }
);