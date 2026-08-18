import calendar
import json
import os
import secrets
import smtplib
import ssl
from datetime import date, datetime, time, timedelta
from email.message import EmailMessage

import psycopg
from flask import Flask, request, send_from_directory

app = Flask(__name__)


# =========================================================
# CONEXÃO COM POSTGRESQL
# =========================================================

def conectar_banco():
    return psycopg.connect(
        dbname="priorado146"
    )


def gerar_token_confirmacao():
    return secrets.token_urlsafe(32)

def enviar_email(
    destinatario,
    assunto,
    corpo,
):

    smtp_host = os.getenv(
        "SMTP_HOST"
    )

    smtp_port = os.getenv(
        "SMTP_PORT"
    )

    smtp_user = os.getenv(
        "SMTP_USER"
    )

    smtp_password = os.getenv(
        "SMTP_PASSWORD"
    )


    if not smtp_host:
        raise RuntimeError(
            "SMTP_HOST não configurado"
        )

    if not smtp_port:
        raise RuntimeError(
            "SMTP_PORT não configurado"
        )

    if not smtp_user:
        raise RuntimeError(
            "SMTP_USER não configurado"
        )

    if not smtp_password:
        raise RuntimeError(
            "SMTP_PASSWORD não configurado"
        )

    if not destinatario:
        raise RuntimeError(
            "Destinatário não informado"
        )


    mensagem = EmailMessage()

    mensagem["From"] = smtp_user
    mensagem["To"] = destinatario
    mensagem["Subject"] = assunto

    mensagem.set_content(
        corpo
    )


    contexto_ssl = (
        ssl.create_default_context()
    )


    with smtplib.SMTP(
        smtp_host,
        int(smtp_port),
        timeout=30,
    ) as servidor:

        servidor.ehlo()

        servidor.starttls(
            context=contexto_ssl
        )

        servidor.ehlo()

        servidor.login(
            smtp_user,
            smtp_password
        )

        servidor.send_message(
            mensagem
        )

        def normalizar_json_execucao(valor):

            if valor is None or valor == "":
             return {}


            if isinstance(valor, dict):
                return valor


            if isinstance(valor, str):

                try:

                    return json.loads(
                        valor
                    )

                except json.JSONDecodeError:

                    return {}


            return {}

def obter_configuracao_sistema(
    chave,
    valor_padrao=None,
):

            with (
                conectar_banco() as conexao,
                conexao.cursor() as cursor,
            ):

                cursor.execute(
                    """
                    SELECT
                        valor,
                        tipo

                    FROM configuracoes_sistema

                    WHERE chave = %s
                    """,
                    (
                        chave,
                    ),
                )

                registro = cursor.fetchone()


            if registro is None:

                return valor_padrao


            valor = registro[0]

            tipo = registro[1]


            try:

                if tipo == "INTEGER":

                    return int(valor)


                if tipo == "BOOLEAN":

                    return (
                        valor.strip().lower()
                        in (
                            "true",
                            "1",
                            "sim",
                            "yes",
                            "on",
                        )
                    )


                return valor


            except (
                TypeError,
                ValueError,
            ):

                return valor_padrao

    # =========================================================
# FUNÇÕES DE RECORRÊNCIA
# =========================================================


def primeira_data_semanal(data_inicio, dia_semana):

    diferenca = (
        dia_semana - data_inicio.weekday()
    ) % 7

    return data_inicio + timedelta(
        days=diferenca
    )


def calcular_dia_do_mes(
    ano,
    mes,
    dia_semana,
    ordem_mes
):

    calendario = calendar.Calendar()

    dias = []


    for dia in calendario.itermonthdates(
        ano,
        mes
    ):

        if (
            dia.month == mes
            and dia.weekday() == dia_semana
        ):

            dias.append(dia)


    if not dias:
        return None


    if ordem_mes == -1:
        return dias[-1]


    indice = ordem_mes - 1


    if indice >= len(dias):
        return None


    return dias[indice]


def gerar_datas_recorrencia(
    tipo_recorrencia,
    dia_semana,
    ordem_mes,
    data_inicio,
    data_fim,
    quantidade
):

    datas = []


    # =====================================================
    # SEMANAL OU QUINZENAL
    # =====================================================

    if tipo_recorrencia in {
        "SEMANAL",
        "QUINZENAL"
    }:

        atual = primeira_data_semanal(
            data_inicio,
            dia_semana
        )


        if tipo_recorrencia == "SEMANAL":
            intervalo_dias = 7

        else:
            intervalo_dias = 14


        while len(datas) < quantidade:

            if (
                data_fim is not None
                and atual > data_fim
            ):
                break


            datas.append(atual)


            atual += timedelta(
                days=intervalo_dias
            )


        return datas


    # =====================================================
    # MENSAL POR DIA DA SEMANA
    # =====================================================

    ano = data_inicio.year
    mes = data_inicio.month


    while len(datas) < quantidade:

        atual = calcular_dia_do_mes(
            ano,
            mes,
            dia_semana,
            ordem_mes
        )


        if (
            atual is not None
            and atual >= data_inicio
        ):

            if (
                data_fim is not None
                and atual > data_fim
            ):
                break


            datas.append(atual)


        mes += 1


        if mes == 13:
            mes = 1
            ano += 1


    return datas

# =========================================================
# FRONTEND
# =========================================================

@app.route("/")
def pagina_inicial():
    return send_from_directory(
        ".",
        "index.html"
    )


@app.route("/script.js")
def javascript():
    return send_from_directory(
        ".",
        "script.js"
    )


@app.route("/styles.css")
def estilos():
    return send_from_directory(
        ".",
        "styles.css"
    )


# =========================================================
# API DE MEMBROS
# =========================================================

@app.route("/api/membros", methods=["GET", "POST"])
def api_membros():

    print(">>> MÉTODO RECEBIDO:", request.method)
    print(">>> ROTA RECEBIDA:", request.path)


    # =====================================================
    # GET - LISTAR MEMBROS
    # =====================================================

    if request.method == "GET":

        with conectar_banco() as conexao, conexao.cursor() as cursor:

            cursor.execute(
                 """
                SELECT
                    id,
                    nome,
                    email,
                    criado_em
                    FROM membros
                    ORDER BY nome
                    """
)

            registros = cursor.fetchall()


            membros = []


        for registro in registros:

            membro = {
                "id": registro[0],
                "nome": registro[1],
                "email": registro[2],
                "criado_em": (
                    registro[3].isoformat()
                    if registro[3]
                    else None
                ),
            }

            membros.append(membro)


        return {
            "status": "ok",
            "membros": membros,
        }, 200

    # =====================================================
    # POST - CRIAR MEMBRO
    # =====================================================

    dados = request.get_json(
        silent=True
    )

    if dados is None:

        return {
            "status": "erro",
            "mensagem": "JSON não recebido",
        }, 400


    nome = str(
        dados.get(
            "nome",
            ""
        )
    ).strip()


    email = str(
        dados.get(
            "email",
            ""
        )
    ).strip().lower()


    if email == "":
        email = None


    if nome == "":

        return {
            "status": "erro",
            "mensagem": "O nome é obrigatório",
        }, 400


    with (
        conectar_banco() as conexao,
        conexao.cursor() as cursor,
    ):

        # ---------------------------------------------
        # EVITAR E-MAIL DUPLICADO
        # ---------------------------------------------

        if email is not None:

            cursor.execute(
                """
                SELECT id
                FROM membros
                WHERE LOWER(email) = LOWER(%s)
                """,
                (email,),
            )

            membro_email_existente = (
                cursor.fetchone()
            )

            if membro_email_existente is not None:

                return {
                    "status": "erro",
                    "mensagem": (
                        "Já existe um membro "
                        "com este e-mail"
                    ),
                }, 409


        # ---------------------------------------------
        # CRIAR MEMBRO
        # ---------------------------------------------

        cursor.execute(
            """
            INSERT INTO membros (
                nome,
                email
            )
            VALUES (
                %s,
                %s
            )
            RETURNING
                id,
                nome,
                email,
                criado_em
            """,
            (
                nome,
                email,
            ),
        )

        registro = cursor.fetchone()


    if registro is None:

        return {
            "status": "erro",
            "mensagem": (
                "Não foi possível criar o membro"
            ),
        }, 500


    return {
        "status": "ok",
        "mensagem": "Membro criado com sucesso",
        "membro": {
            "id": registro[0],
            "nome": registro[1],
            "email": registro[2],
            "criado_em": (
                registro[3].isoformat()
                if registro[3]
                else None
            ),
        },
    }, 201

# =========================================================
# API DE UM MEMBRO ESPECÍFICO
# PUT    -> EDITAR
# DELETE -> EXCLUIR
# =========================================================

@app.route(
    "/api/membros/<int:membro_id>",
    methods=["PUT", "DELETE"]
)
def membro_por_id(membro_id):

    print(">>> MÉTODO RECEBIDO:", request.method)
    print(">>> MEMBRO ID:", membro_id)


    # =====================================================
    # PUT - EDITAR MEMBRO
    # =====================================================

    if request.method == "PUT":

        dados = request.get_json(
            silent=True
        )

        if dados is None:

            return {
                "status": "erro",
                "mensagem": "JSON não recebido",
            }, 400


        nome = str(
            dados.get(
                "nome",
                ""
            )
        ).strip()


        email = str(
            dados.get(
                "email",
                ""
            )
        ).strip().lower()


        if email == "":
            email = None


        if nome == "":

            return {
                "status": "erro",
                "mensagem": "O nome é obrigatório",
            }, 400


        with (
            conectar_banco() as conexao,
            conexao.cursor() as cursor,
        ):

            # Verificar se o membro existe

            cursor.execute(
                """
                SELECT id
                FROM membros
                WHERE id = %s
                """,
                (membro_id,),
            )

            membro_existente = (
                cursor.fetchone()
            )


            if membro_existente is None:

                return {
                    "status": "erro",
                    "mensagem": "Membro não encontrado",
                }, 404


            # Impedir e-mail repetido em outro membro

            if email is not None:

                cursor.execute(
                    """
                    SELECT id
                    FROM membros

                    WHERE
                        LOWER(email) = LOWER(%s)
                        AND id <> %s
                    """,
                    (
                        email,
                        membro_id,
                    ),
                )

                membro_email_existente = (
                    cursor.fetchone()
                )


                if membro_email_existente is not None:

                    return {
                        "status": "erro",
                        "mensagem": (
                            "Já existe outro membro "
                            "com este e-mail"
                        ),
                    }, 409


            # Atualizar membro

            cursor.execute(
                """
                UPDATE membros

                SET
                    nome = %s,
                    email = %s

                WHERE id = %s

                RETURNING
                    id,
                    nome,
                    email,
                    criado_em
                """,
                (
                    nome,
                    email,
                    membro_id,
                ),
            )

            registro = cursor.fetchone()

                    # =================================================
        # SINCRONIZAR E-MAIL COM NOTIFICAÇÕES PENDENTES
        # =================================================

        if email is not None:

            cursor.execute(
                """
                UPDATE notificacoes

                SET
                    destinatario = %s,

                    status = CASE

                        WHEN
                            status = 'ERRO'
                            AND erro =
                                'Destinatário não informado'

                        THEN 'PENDENTE'

                        ELSE status

                    END,

                    erro = CASE

                        WHEN
                            status = 'ERRO'
                            AND erro =
                                'Destinatário não informado'

                        THEN NULL

                        ELSE erro

                    END

                WHERE
                    membro_id = %s

                    AND status IN (
                        'PENDENTE',
                        'ERRO'
                    )
                """,
                (
                    email,
                    membro_id,
                ),
            )

        else:

            cursor.execute(
                """
                UPDATE notificacoes

                SET destinatario = NULL

                WHERE
                    membro_id = %s
                    AND status = 'PENDENTE'
                """,
                (membro_id,),
            )


        if registro is None:

            return {
                "status": "erro",
                "mensagem": "Membro não encontrado",
            }, 404


        return {
            "status": "ok",
            "mensagem": "Membro atualizado com sucesso",
            "membro": {
                "id": registro[0],
                "nome": registro[1],
                "email": registro[2],
                "criado_em": (
                    registro[3].isoformat()
                    if registro[3]
                    else None
                ),
            },
        }, 200

    # =====================================================
    # DELETE - EXCLUIR MEMBRO
    # =====================================================

    if request.method == "DELETE":

        with (
            conectar_banco() as conexao,
            conexao.cursor() as cursor,
        ):

            cursor.execute(
                """
                DELETE FROM membros
                WHERE id = %s
                RETURNING
                    id,
                    nome
                """,
                (membro_id,)
            )

            registro = cursor.fetchone()


        if registro is None:

            return {
                "status": "erro",
                "mensagem": "Membro não encontrado"
            }, 404


        membro = {
            "id": registro[0],
            "nome": registro[1]
        }


        print(">>> MEMBRO EXCLUÍDO:")
        print(membro)


        return {
            "status": "ok",
            "mensagem": "Membro excluído com sucesso",
            "membro": membro
        }, 200

        # =========================================================
# API DE REUNIÕES
# GET  -> LISTAR
# POST -> CRIAR
# =========================================================

@app.route("/api/reunioes", methods=["GET", "POST"])
def api_reunioes():

    # =====================================================
    # GET - LISTAR REUNIÕES
    # =====================================================

    if request.method == "GET":

        with (
            conectar_banco() as conexao,
            conexao.cursor() as cursor,
        ):

            cursor.execute(
                """
                SELECT
                    id,
                    titulo,
                    objetivo,
                    data_hora,
                    local,
                    status,
                    criado_em
                FROM reunioes
                ORDER BY data_hora
                """
            )

            registros = cursor.fetchall()


        reunioes = []


        for registro in registros:

            reuniao = {
                "id": registro[0],
                "titulo": registro[1],
                "objetivo": registro[2],
                "data_hora": registro[3].isoformat(),
                "local": registro[4],
                "status": registro[5],
                "criado_em": registro[6].isoformat()
            }

            reunioes.append(reuniao)


        return {
            "status": "ok",
            "reunioes": reunioes
        }, 200


    # =====================================================
    # POST - CRIAR REUNIÃO
    # =====================================================

    dados = request.get_json(
        silent=True
    )


    if dados is None:

        return {
            "status": "erro",
            "mensagem": "JSON não recebido"
        }, 400


    titulo = dados.get(
        "titulo",
        ""
    ).strip()


    objetivo = dados.get(
        "objetivo",
        ""
    ).strip()


    data_hora = dados.get(
        "data_hora",
        ""
    ).strip()


    local = dados.get(
        "local",
        ""
    ).strip()


    if titulo == "":

        return {
            "status": "erro",
            "mensagem": "O título é obrigatório"
        }, 400


    if data_hora == "":

        return {
            "status": "erro",
            "mensagem": "A data e hora são obrigatórias"
        }, 400


    with (
        conectar_banco() as conexao,
        conexao.cursor() as cursor,
    ):

        cursor.execute(
            """
            INSERT INTO reunioes (
                titulo,
                objetivo,
                data_hora,
                local
            )
            VALUES (
                %s,
                %s,
                %s,
                %s
            )
            RETURNING
                id,
                titulo,
                objetivo,
                data_hora,
                local,
                status,
                criado_em
            """,
            (
                titulo,
                objetivo,
                data_hora,
                local
            )
        )

        registro = cursor.fetchone()


    reuniao = {
        "id": registro[0],
        "titulo": registro[1],
        "objetivo": registro[2],
        "data_hora": registro[3].isoformat(),
        "local": registro[4],
        "status": registro[5],
        "criado_em": registro[6].isoformat()
    }


    print(">>> REUNIÃO CADASTRADA:")
    print(reuniao)


    return {
        "status": "ok",
        "mensagem": "Reunião cadastrada com sucesso",
        "reuniao": reuniao
    }, 201

# =========================================================
# PARTICIPANTES DA REUNIÃO
# GET  -> LISTAR PARTICIPANTES
# POST -> ADICIONAR PARTICIPANTE
# =========================================================

@app.route(
    "/api/reunioes/<int:reuniao_id>/participantes",
    methods=["GET", "POST"]
)
def api_reuniao_participantes(reuniao_id):


    # =====================================================
    # GET - LISTAR PARTICIPANTES
    # =====================================================

    if request.method == "GET":

        with (
            conectar_banco() as conexao,
            conexao.cursor() as cursor,
        ):

            cursor.execute(
                """
                SELECT
                    rp.id,
                    m.id,
                    m.nome,
                    rp.status_confirmacao,
                    rp.justificativa,
                    rp.status_presenca,
                    rp.respondido_em
                FROM reuniao_participantes rp

                JOIN membros m
                    ON m.id = rp.membro_id

                WHERE rp.reuniao_id = %s

                ORDER BY m.nome
                """,
                (reuniao_id,)
            )

            registros = cursor.fetchall()


        participantes = []


        for registro in registros:

            participante = {
                "id": registro[0],
                "membro_id": registro[1],
                "nome": registro[2],
                "status_confirmacao": registro[3],
                "justificativa": registro[4],
                "status_presenca": registro[5],
                "respondido_em": (
                    registro[6].isoformat()
                    if registro[6]
                    else None
                )
            }

            participantes.append(
                participante
            )


        return {
            "status": "ok",
            "participantes": participantes
        }, 200


    # =====================================================
    # POST - ADICIONAR PARTICIPANTE
    # =====================================================

    dados = request.get_json(
        silent=True
    )


    if dados is None:

        return {
            "status": "erro",
            "mensagem": "JSON não recebido"
        }, 400


    membro_id = dados.get(
        "membro_id"
    )


    if membro_id is None:

        return {
            "status": "erro",
            "mensagem": "O membro é obrigatório"
        }, 400


    with (
        conectar_banco() as conexao,
        conexao.cursor() as cursor,
    ):

        cursor.execute(
            """
            INSERT INTO reuniao_participantes (
                reuniao_id,
                membro_id
            )
            VALUES (
                %s,
                %s
            )

            ON CONFLICT (
                reuniao_id,
                membro_id
            )

            DO NOTHING

            RETURNING id
            """,
            (
                reuniao_id,
                membro_id
            )
        )

        registro = cursor.fetchone()


    if registro is None:

        return {
            "status": "erro",
            "mensagem": "Este membro já participa desta reunião"
        }, 409


    return {
        "status": "ok",
        "mensagem": "Participante adicionado com sucesso"
    }, 201

    # =========================================================
# CONFIRMAÇÃO DO PARTICIPANTE
# =========================================================

@app.route(
    "/api/reunioes/<int:reuniao_id>/participantes/"
    "<int:membro_id>/confirmacao",
    methods=["PUT"]
)
def atualizar_confirmacao(reuniao_id, membro_id):

    dados = request.get_json(
        silent=True
    )


    if dados is None:

        return {
            "status": "erro",
            "mensagem": "JSON não recebido"
        }, 400


    status_confirmacao = str(
        dados.get(
            "status_confirmacao",
            ""
        )
    ).strip().upper()


    justificativa = str(
        dados.get(
            "justificativa",
            ""
        )
    ).strip()


    status_permitidos = {
        "CONFIRMADO",
        "RECUSADO"
    }


    if status_confirmacao not in status_permitidos:

        return {
            "status": "erro",
            "mensagem": "Status de confirmação inválido"
        }, 400


    if (
        status_confirmacao == "RECUSADO"
        and justificativa == ""
    ):

        return {
            "status": "erro",
            "mensagem": (
                "A justificativa é obrigatória "
                "para ausência"
            )
        }, 400


    if status_confirmacao == "CONFIRMADO":
        justificativa = None


    with (
        conectar_banco() as conexao,
        conexao.cursor() as cursor,
    ):

        cursor.execute(
            """
            UPDATE reuniao_participantes

            SET
                status_confirmacao = %s,
                justificativa = %s,
                respondido_em = CURRENT_TIMESTAMP

            WHERE
                reuniao_id = %s
                AND membro_id = %s

            RETURNING
                id,
                status_confirmacao,
                justificativa,
                respondido_em
            """,
            (
                status_confirmacao,
                justificativa,
                reuniao_id,
                membro_id
            )
        )

        registro = cursor.fetchone()


    if registro is None:

        return {
            "status": "erro",
            "mensagem": "Participante não encontrado"
        }, 404


    return {
        "status": "ok",
        "mensagem": "Resposta registrada com sucesso",
        "confirmacao": {
            "id": registro[0],
            "status_confirmacao": registro[1],
            "justificativa": registro[2],
            "respondido_em": (
                registro[3].isoformat()
                if registro[3]
                else None
            )
        }
    }, 200

    # =========================================================
# PRESENÇA REAL
# =========================================================

@app.route(
    "/api/reunioes/<int:reuniao_id>/participantes/"
    "<int:membro_id>/presenca",
    methods=["PUT"]
)
def atualizar_presenca(reuniao_id, membro_id):

    dados = request.get_json(
        silent=True
    )


    if dados is None:

        return {
            "status": "erro",
            "mensagem": "JSON não recebido"
        }, 400


    status_presenca = str(
        dados.get(
            "status_presenca",
            ""
        )
    ).strip().upper()


    status_permitidos = {
        "PRESENTE",
        "AUSENTE",
        "NAO_REGISTRADA"
    }


    if status_presenca not in status_permitidos:

        return {
            "status": "erro",
            "mensagem": "Status de presença inválido"
        }, 400


    with (
        conectar_banco() as conexao,
        conexao.cursor() as cursor,
    ):

        cursor.execute(
            """
            UPDATE reuniao_participantes

            SET
                status_presenca = %s

            WHERE
                reuniao_id = %s
                AND membro_id = %s

            RETURNING
                id,
                status_presenca
            """,
            (
                status_presenca,
                reuniao_id,
                membro_id
            )
        )

        registro = cursor.fetchone()


    if registro is None:

        return {
            "status": "erro",
            "mensagem": "Participante não encontrado"
        }, 404


    return {
        "status": "ok",
        "mensagem": "Presença registrada com sucesso",
        "presenca": {
            "id": registro[0],
            "status_presenca": registro[1]
        }
    }, 200

    # =========================================================
# DASHBOARD DE FREQUÊNCIA
# =========================================================

@app.route("/api/frequencia", methods=["GET"])
def api_frequencia():

    with (
        conectar_banco() as conexao,
        conexao.cursor() as cursor,
    ):

        cursor.execute(
            """
            SELECT
                m.id,
                m.nome,

                COUNT(rp.id) AS total_convocacoes,

                COUNT(rp.id)
                    FILTER (
                        WHERE rp.status_presenca = 'PRESENTE'
                    ) AS total_presencas,

                COUNT(rp.id)
                    FILTER (
                        WHERE rp.status_presenca = 'AUSENTE'
                    ) AS total_ausencias,

                COUNT(rp.id)
                    FILTER (
                        WHERE rp.status_presenca = 'NAO_REGISTRADA'
                    ) AS total_nao_registradas,

                COUNT(rp.id)
                    FILTER (
                        WHERE rp.status_confirmacao = 'CONFIRMADO'
                    ) AS total_confirmados,

                COUNT(rp.id)
                    FILTER (
                        WHERE rp.status_confirmacao = 'RECUSADO'
                    ) AS total_recusados

            FROM membros m

            LEFT JOIN reuniao_participantes rp
                ON rp.membro_id = m.id

            GROUP BY
                m.id,
                m.nome

            ORDER BY
                m.nome
            """
        )

        registros = cursor.fetchall()


    frequencias = []


    for registro in registros:

        membro_id = registro[0]
        nome = registro[1]

        total_convocacoes = registro[2]
        total_presencas = registro[3]
        total_ausencias = registro[4]
        total_nao_registradas = registro[5]
        total_confirmados = registro[6]
        total_recusados = registro[7]


        total_computado = (
            total_presencas +
            total_ausencias
        )


        if total_computado > 0:

            percentual_frequencia = round(
                (
                    total_presencas /
                    total_computado
                ) * 100,
                2
            )

        else:

            percentual_frequencia = 0


        frequencias.append(
            {
                "membro_id": membro_id,
                "nome": nome,
                "total_convocacoes": total_convocacoes,
                "total_presencas": total_presencas,
                "total_ausencias": total_ausencias,
                "total_nao_registradas": total_nao_registradas,
                "total_confirmados": total_confirmados,
                "total_recusados": total_recusados,
                "total_computado": total_computado,
                "percentual_frequencia": percentual_frequencia
            }
        )

    return {
        "status": "ok",
        "frequencias": frequencias
    }, 200

@app.route(
    "/api/series-reunioes",
    methods=["GET", "POST"]
)
def api_series_reunioes():

        # =====================================================
    # GET - LISTAR SÉRIES
    # =====================================================

    if request.method == "GET":

        with (
            conectar_banco() as conexao,
            conexao.cursor() as cursor,
        ):
            cursor.execute(
                """
                SELECT
                    id,
                    titulo,
                    objetivo,
                    local,
                    tipo_recorrencia,
                    dia_semana,
                    ordem_mes,
                    hora,
                    data_inicio,
                    data_fim,
                    ativo
                FROM series_reunioes
                ORDER BY id
                """
            )

            registros = cursor.fetchall()

        series = []

        for registro in registros:
            series.append(
                {
                    "id": registro[0],
                    "titulo": registro[1],
                    "objetivo": registro[2],
                    "local": registro[3],
                    "tipo_recorrencia": registro[4],
                    "dia_semana": registro[5],
                    "ordem_mes": registro[6],
                    "hora": str(registro[7]),
                    "data_inicio": registro[8].isoformat(),
                    "data_fim": (
                        registro[9].isoformat()
                        if registro[9]
                        else None
                    ),
                    "ativo": registro[10],
                }
            )

        return {
            "status": "ok",
            "series": series,
        }, 200


    # =====================================================
    # POST - CRIAR SÉRIE
    # =====================================================

    dados = request.get_json(silent=True)

    if dados is None:
        return {
            "status": "erro",
            "mensagem": "JSON não recebido",
        }, 400


    titulo = str(
        dados.get("titulo", "")
    ).strip()

    objetivo = str(
        dados.get("objetivo", "")
    ).strip()

    local = str(
        dados.get("local", "")
    ).strip()

    tipo_recorrencia = str(
        dados.get("tipo_recorrencia", "")
    ).strip().upper()

    dia_semana = dados.get("dia_semana")

    ordem_mes = dados.get("ordem_mes")

    hora_texto = str(
        dados.get("hora", "")
    ).strip()

    data_inicio_texto = str(
        dados.get("data_inicio", "")
    ).strip()

    data_fim_texto = str(
        dados.get("data_fim", "")
    ).strip()

    quantidade = dados.get(
        "quantidade",
        6
    )


    # =====================================================
    # VALIDAÇÕES
    # =====================================================

    if titulo == "":
        return {
            "status": "erro",
            "mensagem": "Título obrigatório",
        }, 400


    tipos_permitidos = {
        "SEMANAL",
        "QUINZENAL",
        "MENSAL_DIA_SEMANA",
    }


    if tipo_recorrencia not in tipos_permitidos:
        return {
            "status": "erro",
            "mensagem": "Tipo de recorrência inválido",
        }, 400

    try:

        dia_semana = int(
            dia_semana
        )

        quantidade = int(
            quantidade
        )

        hora = time.fromisoformat(
            hora_texto
        )

        data_inicio = date.fromisoformat(
            data_inicio_texto
        )

        if data_fim_texto:

            data_fim = date.fromisoformat(
                data_fim_texto
            )

        else:

            data_fim = None


        if tipo_recorrencia == "MENSAL_DIA_SEMANA":

            ordem_mes = int(
                ordem_mes
            )

        else:

            ordem_mes = None


    except (TypeError, ValueError):

        return {
            "status": "erro",
            "mensagem": "Dados da recorrência inválidos",
        }, 400


    if quantidade < 1 or quantidade > 60:

        return {
            "status": "erro",
            "mensagem": "Quantidade deve estar entre 1 e 60",
        }, 400


    if data_fim is not None and data_fim < data_inicio:

        return {
            "status": "erro",
            "mensagem": (
                "A data final não pode ser "
                "anterior à data inicial"
            ),
        }, 400

        if (
        tipo_recorrencia == "MENSAL_DIA_SEMANA"
        and ordem_mes not in {
            1,
            2,
            3,
            4,
            5,
            -1,
        }
    ):

            return {
            "status": "erro",
            "mensagem": "Ordem mensal inválida",
        }, 400


    # =====================================================
    # GERAR AS DATAS
    # =====================================================

    datas = gerar_datas_recorrencia(
        tipo_recorrencia,
        dia_semana,
        ordem_mes,
        data_inicio,
        data_fim,
        quantidade,
    )


    if not datas:

        return {
            "status": "erro",
            "mensagem": "Nenhuma ocorrência foi gerada",
        }, 400


    # =====================================================
    # GRAVAR NO POSTGRESQL
    # =====================================================

    with (
        conectar_banco() as conexao,
        conexao.cursor() as cursor,
    ):

        cursor.execute(
            """
            INSERT INTO series_reunioes (
                titulo,
                objetivo,
                local,
                tipo_recorrencia,
                dia_semana,
                ordem_mes,
                hora,
                data_inicio,
                data_fim
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            RETURNING id
            """,
            (
                titulo,
                objetivo,
                local,
                tipo_recorrencia,
                dia_semana,
                ordem_mes,
                hora,
                data_inicio,
                data_fim,
            ),
        )

        registro_serie = cursor.fetchone()

        if registro_serie is None:
            return {
                "status": "erro",
                "mensagem": "Não foi possível criar a série",
            }, 500

        serie_id = registro_serie[0]

        ocorrencias_criadas = []


        for data_ocorrencia in datas:

            data_hora = datetime.combine(
                data_ocorrencia,
                hora
            )

            cursor.execute(
                """
                INSERT INTO reunioes (
                    titulo,
                    objetivo,
                    data_hora,
                    local,
                    serie_id
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                ON CONFLICT DO NOTHING
                RETURNING
                    id,
                    data_hora
                """,
                (
                    titulo,
                    objetivo,
                    data_hora,
                    local,
                    serie_id,
                ),
            )

            registro_reuniao = cursor.fetchone()

            if registro_reuniao:

                ocorrencias_criadas.append(
                    {
                        "id": registro_reuniao[0],
                        "data_hora": (
                            registro_reuniao[1].isoformat()
                        ),
                    }
                )


    return {
        "status": "ok",
        "mensagem": "Série recorrente criada com sucesso",
        "serie_id": serie_id,
        "ocorrencias_criadas": ocorrencias_criadas,
    }, 201

    # =========================================================
# PARTICIPANTES DE UMA SÉRIE RECORRENTE
# GET  -> LISTAR
# POST -> ADICIONAR E PROPAGAR PARA AS REUNIÕES
# =========================================================


@app.route(
    "/api/series-reunioes/<int:serie_id>/participantes",
    methods=["GET", "POST"],
)
def api_serie_participantes(serie_id):

    # =====================================================
    # GET
    # =====================================================

    if request.method == "GET":

        with (
            conectar_banco() as conexao,
            conexao.cursor() as cursor,
        ):

            cursor.execute(
                """
                SELECT
                    sp.id,
                    m.id,
                    m.nome,
                    sp.criado_em
                FROM serie_participantes sp

                JOIN membros m
                    ON m.id = sp.membro_id

                WHERE sp.serie_id = %s

                ORDER BY m.nome
                """,
                (serie_id,),
            )

            registros = cursor.fetchall()

        participantes = []

        for registro in registros:

            participantes.append(
                {
                    "id": registro[0],
                    "membro_id": registro[1],
                    "nome": registro[2],
                    "criado_em": registro[3].isoformat(),
                }
            )

        return {
            "status": "ok",
            "participantes": participantes,
        }, 200

    # =====================================================
    # POST
    # =====================================================

    dados = request.get_json(
        silent=True
    )

    if dados is None:

        return {
            "status": "erro",
            "mensagem": "JSON não recebido",
        }, 400

    membro_id = dados.get(
        "membro_id"
    )

    if membro_id is None:

        return {
            "status": "erro",
            "mensagem": "O membro é obrigatório",
        }, 400

    try:

        membro_id = int(
            membro_id
        )

    except (TypeError, ValueError):

        return {
            "status": "erro",
            "mensagem": "Membro inválido",
        }, 400

    with (
        conectar_banco() as conexao,
        conexao.cursor() as cursor,
    ):

        # Verifica se a série existe

        cursor.execute(
            """
            SELECT id
            FROM series_reunioes
            WHERE id = %s
            """,
            (serie_id,),
        )

        serie = cursor.fetchone()

        if serie is None:

            return {
                "status": "erro",
                "mensagem": "Série não encontrada",
            }, 404

        # Adiciona o membro à série

        cursor.execute(
            """
            INSERT INTO serie_participantes (
                serie_id,
                membro_id
            )
            VALUES (
                %s,
                %s
            )
            ON CONFLICT (
                serie_id,
                membro_id
            )
            DO NOTHING
            RETURNING id
            """,
            (
                serie_id,
                membro_id,
            ),
        )

        registro = cursor.fetchone()

        if registro is None:

            return {
                "status": "erro",
                "mensagem": (
                    "Este membro já participa desta série"
                ),
            }, 409

        # Propaga para todas as reuniões da série

        cursor.execute(
            """
            INSERT INTO reuniao_participantes (
                reuniao_id,
                membro_id
            )

            SELECT
                r.id,
                %s

            FROM reunioes r

            WHERE r.serie_id = %s

            ON CONFLICT (
                reuniao_id,
                membro_id
            )
            DO NOTHING

            RETURNING id
            """,
            (
                membro_id,
                serie_id,
            ),
        )

        registros_reuniao = (
            cursor.fetchall()
        )

    return {
        "status": "ok",
        "mensagem": (
            "Participante adicionado à série com sucesso"
        ),
        "reunioes_atualizadas": len(
            registros_reuniao
        ),
    }, 201

    # =========================================================
# GERAR LINKS DE CONFIRMAÇÃO
# =========================================================


@app.route(
    "/api/reunioes/<int:reuniao_id>/gerar-links-confirmacao",
    methods=["POST"],
)
def gerar_links_confirmacao(reuniao_id):

    with (
        conectar_banco() as conexao,
        conexao.cursor() as cursor,
    ):

        # -------------------------------------------------
        # VERIFICAR SE A REUNIÃO EXISTE
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                titulo,
                data_hora
            FROM reunioes
            WHERE id = %s
            """,
            (reuniao_id,),
        )

        reuniao = cursor.fetchone()

        if reuniao is None:

            return {
                "status": "erro",
                "mensagem": "Reunião não encontrada",
            }, 404


        # -------------------------------------------------
        # BUSCAR PARTICIPANTES DA REUNIÃO
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                rp.id,
                m.id,
                m.nome,
                rp.token_confirmacao
            FROM reuniao_participantes rp

            JOIN membros m
                ON m.id = rp.membro_id

            WHERE rp.reuniao_id = %s

            ORDER BY m.nome
            """,
            (reuniao_id,),
        )

        participantes = cursor.fetchall()


        links = []


        # -------------------------------------------------
        # GERAR UM TOKEN PARA CADA PARTICIPANTE
        # -------------------------------------------------

        for participante in participantes:

            participante_id = participante[0]
            membro_id = participante[1]
            nome = participante[2]
            token = participante[3]


            if token is None:

                token = gerar_token_confirmacao()


                cursor.execute(
                    """
                    UPDATE reuniao_participantes

                    SET
                        token_confirmacao = %s,
                        token_criado_em = CURRENT_TIMESTAMP,
                        token_expira_em = %s

                    WHERE id = %s
                    """,
                    (
                        token,
                        reuniao[2],
                        participante_id,
                    ),
                )


            links.append(
                {
                    "membro_id": membro_id,
                    "nome": nome,
                    "token": token,
                    "link": (
                        "/confirmar/"
                        + token
                    ),
                }
            )


    return {
        "status": "ok",
        "mensagem": "Links gerados com sucesso",
        "reuniao": {
            "id": reuniao[0],
            "titulo": reuniao[1],
            "data_hora": reuniao[2].isoformat(),
        },
        "links": links,
    }, 200

    # =========================================================
# CONFIRMAÇÃO PÚBLICA POR TOKEN
# GET -> CONSULTAR CONVOCAÇÃO
# PUT -> RESPONDER CONVOCAÇÃO
# =========================================================


@app.route(
    "/api/confirmar/<token>",
    methods=["GET", "PUT"],
)
def api_confirmar_token(token):

    # =====================================================
    # GET - CONSULTAR CONVOCAÇÃO
    # =====================================================

    if request.method == "GET":

        with (
            conectar_banco() as conexao,
            conexao.cursor() as cursor,
        ):

            cursor.execute(
                """
                SELECT
                    rp.id,
                    m.nome,
                    r.id,
                    r.titulo,
                    r.data_hora,
                    r.local,
                    rp.status_confirmacao,
                    rp.justificativa,
                    rp.respondido_em,
                    rp.token_expira_em,
                    (
                        rp.token_expira_em IS NOT NULL
                        AND rp.token_expira_em < CURRENT_TIMESTAMP
                    ) AS expirado

                FROM reuniao_participantes rp

                JOIN membros m
                    ON m.id = rp.membro_id

                JOIN reunioes r
                    ON r.id = rp.reuniao_id

                WHERE rp.token_confirmacao = %s
                """,
                (token,),
            )

            registro = cursor.fetchone()


        if registro is None:

            return {
                "status": "erro",
                "mensagem": "Token inválido",
            }, 404


        if registro[10]:

            return {
        "status": "erro",
        "mensagem": "Este link expirou",
    }, 410


        return {
            "status": "ok",
            "convocacao": {
                "nome": registro[1],
                "reuniao_id": registro[2],
                "titulo": registro[3],
                "data_hora": registro[4].isoformat(),
                "local": registro[5],
                "status_confirmacao": registro[6],
                "justificativa": registro[7],
                "respondido_em": (
                    registro[8].isoformat()
                    if registro[8]
                    else None
                ),
            },
        }, 200


    # =====================================================
    # PUT - RESPONDER CONVOCAÇÃO
    # =====================================================

    dados = request.get_json(
        silent=True
    )


    if dados is None:

        return {
            "status": "erro",
            "mensagem": "JSON não recebido",
        }, 400


    status_confirmacao = str(
        dados.get(
            "status_confirmacao",
            ""
        )
    ).strip().upper()


    justificativa = str(
        dados.get(
            "justificativa",
            ""
        )
    ).strip()


    if status_confirmacao not in {
        "CONFIRMADO",
        "RECUSADO",
    }:

        return {
            "status": "erro",
            "mensagem": "Resposta inválida",
        }, 400


    if (
        status_confirmacao == "RECUSADO"
        and justificativa == ""
    ):

        return {
            "status": "erro",
            "mensagem": (
                "A justificativa é obrigatória"
            ),
        }, 400


    if status_confirmacao == "CONFIRMADO":

        justificativa = None


    with (
        conectar_banco() as conexao,
        conexao.cursor() as cursor,
    ):

        cursor.execute(
            """
            UPDATE reuniao_participantes

            SET
                status_confirmacao = %s,
                justificativa = %s,
                respondido_em = CURRENT_TIMESTAMP

            WHERE
                token_confirmacao = %s
                AND (
                    token_expira_em IS NULL
                    OR token_expira_em
                        >= CURRENT_TIMESTAMP
                )

            RETURNING
                id,
                status_confirmacao,
                justificativa,
                respondido_em
            """,
            (
                status_confirmacao,
                justificativa,
                token,
            ),
        )

        registro = cursor.fetchone()


    if registro is None:

        return {
            "status": "erro",
            "mensagem": (
                "Token inválido ou expirado"
            ),
        }, 404


    return {
        "status": "ok",
        "mensagem": (
            "Resposta registrada com sucesso"
        ),
        "resposta": {
            "status_confirmacao":
                registro[1],
            "justificativa":
                registro[2],
            "respondido_em":
                registro[3].isoformat(),
        },
    }, 200

    # =========================================================
# PÁGINA PÚBLICA DE CONFIRMAÇÃO
# =========================================================


@app.route("/confirmar/<token>")
def pagina_confirmacao(token):

    print(
        "Token de confirmação acessado:",
        token
    )

    return send_from_directory(
        ".",
        "confirmar.html"
    )


@app.route("/confirmar.js")
def javascript_confirmacao():

    return send_from_directory(
        ".",
        "confirmar.js"
    )

    # =========================================================
# GERAR NOTIFICAÇÕES DE CONVITE
# =========================================================


@app.route(
    "/api/reunioes/<int:reuniao_id>/notificacoes/gerar",
    methods=["POST"],
)
def gerar_notificacoes_reuniao(reuniao_id):

    with (
        conectar_banco() as conexao,
        conexao.cursor() as cursor,
    ):

        # -------------------------------------------------
        # VERIFICAR REUNIÃO
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                rp.id,
                m.id,
                m.nome,
                m.email,
                rp.token_confirmacao
            FROM reuniao_participantes rp

            JOIN membros m
                ON m.id = rp.membro_id

            WHERE rp.reuniao_id = %s

            ORDER BY m.nome
            """,
            (reuniao_id,),
)
        reuniao = cursor.fetchone()


        if reuniao is None:

            return {
                "status": "erro",
                "mensagem": "Reunião não encontrada",
            }, 404


        if reuniao[4]:

            return {
                "status": "erro",
                "mensagem": (
                    "Não é possível gerar convites "
                    "para uma reunião com data passada"
                ),
            }, 409


        # -------------------------------------------------
        # BUSCAR PARTICIPANTES
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                rp.id,
                m.id,
                m.nome,
                rp.token_confirmacao
            FROM reuniao_participantes rp

            JOIN membros m
                ON m.id = rp.membro_id

            WHERE rp.reuniao_id = %s

            ORDER BY m.nome
            """,
            (reuniao_id,),
        )

        participantes = cursor.fetchall()


        if not participantes:

            return {
                "status": "erro",
                "mensagem": (
                    "Esta reunião não possui participantes"
                ),
            }, 409


        notificacoes_criadas = []


        # -------------------------------------------------
        # CRIAR UMA NOTIFICAÇÃO POR PARTICIPANTE
        # -------------------------------------------------

        for participante in participantes:

            participante_id = participante[0]
            membro_id = participante[1]
            nome = participante[2]
            email = participante[3]
            token = participante[4]


            # ---------------------------------------------
            # GERAR TOKEN CASO AINDA NÃO EXISTA
            # ---------------------------------------------

            if token is None:

                token = gerar_token_confirmacao()


                cursor.execute(
                    """
                    UPDATE reuniao_participantes

                    SET
                        token_confirmacao = %s,
                        token_criado_em =
                            LOCALTIMESTAMP,
                        token_expira_em = %s

                    WHERE id = %s
                    """,
                    (
                        token,
                        reuniao[2],
                        participante_id,
                    ),
                )


            link = (
                "/confirmar/"
                + token
            )


            assunto = (
                "Convite para "
                + reuniao[1]
            )


            mensagem = (
                "Olá, "
                + nome
                + ". Você foi convidado para "
                + reuniao[1]
                + "."
            )


            cursor.execute(
                """
                INSERT INTO notificacoes (
                reuniao_id,
                membro_id,
                tipo,
                canal,
                destinatario,
                assunto,
                mensagem,
                link,
                status
            )
                VALUES (
                    %s,
                    %s,
                    'CONVITE',
                    'EMAIL',
                    %s,
                    %s,
                    %s,
                    %s,
                    'PENDENTE'
                )

                ON CONFLICT DO NOTHING

                RETURNING id
                """,
                (
                    reuniao_id,
                    membro_id,
                    email,
                    assunto,
                    mensagem,
                    link,
                ),
            )


            registro_notificacao = (
                cursor.fetchone()
            )


            if registro_notificacao:

                notificacoes_criadas.append(
                    {
                        "id":
                            registro_notificacao[0],

                        "membro_id":
                            membro_id,

                        "nome":
                            nome,

                        "link":
                            link,
                    }
                )


    return {
        "status": "ok",
        "mensagem": (
            "Fila de notificações gerada"
        ),
        "reuniao_id": reuniao_id,
        "notificacoes_criadas":
            len(notificacoes_criadas),
        "notificacoes":
            notificacoes_criadas,
    }, 201

    # =========================================================
# LISTAR FILA DE NOTIFICAÇÕES
# =========================================================


@app.route(
    "/api/notificacoes",
    methods=["GET"],
)
def listar_notificacoes():

    with (
        conectar_banco() as conexao,
        conexao.cursor() as cursor,
    ):

        cursor.execute(
            """
            SELECT
                n.id,
                n.reuniao_id,
                r.titulo,
                n.membro_id,
                m.nome,
                n.tipo,
                n.canal,
                n.destinatario,
                n.assunto,
                n.mensagem,
                n.link,
                n.status,
                n.tentativas,
                n.erro,
                n.criado_em,
                n.processado_em,
                n.enviado_em

            FROM notificacoes n

            LEFT JOIN reunioes r
                ON r.id = n.reuniao_id

            LEFT JOIN membros m
                ON m.id = n.membro_id

            ORDER BY
                n.criado_em DESC,
                n.id DESC
            """
        )

        registros = cursor.fetchall()


    notificacoes = []


    for registro in registros:

        notificacoes.append(
            {
                "id": registro[0],
                "reuniao_id": registro[1],
                "reuniao": registro[2],
                "membro_id": registro[3],
                "membro": registro[4],
                "tipo": registro[5],
                "canal": registro[6],
                "destinatario": registro[7],
                "assunto": registro[8],
                "mensagem": registro[9],
                "link": registro[10],
                "status": registro[11],
                "tentativas": registro[12],
                "erro": registro[13],
                "criado_em": (
                    registro[14].isoformat()
                    if registro[14]
                    else None
                ),
                "processado_em": (
                    registro[15].isoformat()
                    if registro[15]
                    else None
                ),
                "enviado_em": (
                    registro[16].isoformat()
                    if registro[16]
                    else None
                ),
            }
        )


    return {
        "status": "ok",
        "total": len(
            notificacoes
        ),
        "notificacoes": notificacoes,
    }, 200

    # =========================================================
# ENVIAR UMA NOTIFICAÇÃO POR E-MAIL
# =========================================================


@app.route(
    "/api/notificacoes/<int:notificacao_id>/enviar",
    methods=["POST"],
)
def enviar_notificacao(notificacao_id):

    with (
        conectar_banco() as conexao,
        conexao.cursor() as cursor,
    ):

        # -------------------------------------------------
        # LOCALIZAR NOTIFICAÇÃO
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                n.id,
                n.destinatario,
                n.assunto,
                n.mensagem,
                n.link,
                n.status,
                n.tentativas,
                m.nome,
                r.titulo,
                r.data_hora,
                r.local

            FROM notificacoes n

            LEFT JOIN membros m
                ON m.id = n.membro_id

            LEFT JOIN reunioes r
                ON r.id = n.reuniao_id

            WHERE n.id = %s
            """,
            (notificacao_id,),
        )

        registro = cursor.fetchone()


        if registro is None:

            return {
                "status": "erro",
                "mensagem": (
                    "Notificação não encontrada"
                ),
            }, 404


        destinatario = registro[1]
        assunto = registro[2]
        mensagem_base = registro[3]
        link = registro[4]
        status_atual = registro[5]
        nome = registro[7]
        titulo_reuniao = registro[8]
        data_hora = registro[9]
        local = registro[10]


        # -------------------------------------------------
        # NÃO REENVIAR ALGO JÁ ENVIADO
        # -------------------------------------------------

        if status_atual == "ENVIADO":

            return {
                "status": "erro",
                "mensagem": (
                    "Esta notificação já foi enviada"
                ),
            }, 409


        if status_atual == "CANCELADO":

            return {
                "status": "erro",
                "mensagem": (
                    "Esta notificação está cancelada"
                ),
            }, 409


        # -------------------------------------------------
        # VALIDAR DESTINATÁRIO
        # -------------------------------------------------

        if not destinatario:

            cursor.execute(
                """
                UPDATE notificacoes

                SET
                    status = 'ERRO',
                    tentativas = tentativas + 1,
                    erro = %s,
                    processado_em = LOCALTIMESTAMP

                WHERE id = %s
                """,
                (
                    "Destinatário não informado",
                    notificacao_id,
                ),
            )

            return {
                "status": "erro",
                "mensagem": (
                    "A notificação não possui destinatário"
                ),
            }, 409


        # -------------------------------------------------
        # MONTAR LINK COMPLETO
        # -------------------------------------------------

        app_base_url = os.getenv(
            "APP_BASE_URL",
            request.host_url.rstrip("/"),
        )


        if (
            link
            and not link.startswith(
                ("http://", "https://")
            )
        ):

            link_completo = (
                app_base_url.rstrip("/")
                + "/"
                + link.lstrip("/")
            )

        else:

            link_completo = link


        # -------------------------------------------------
        # CONSTRUIR CORPO DO E-MAIL
        # -------------------------------------------------

        linhas = [
            f"Olá, {nome or 'participante'}.",
            "",
            mensagem_base or (
                "Você possui um novo convite."
            ),
            "",
        ]


        if titulo_reuniao:

            linhas.append(
                f"Reunião: {titulo_reuniao}"
            )


        if data_hora:

            linhas.append(
                "Data e hora: "
                + data_hora.strftime(
                    "%d/%m/%Y às %H:%M"
                )
            )


        if local:

            linhas.append(
                f"Local: {local}"
            )


        if link_completo:

            linhas.extend(
                [
                    "",
                    "Confirme sua participação:",
                    link_completo,
                ]
            )


        linhas.extend(
            [
                "",
                "Priorado 146",
            ]
        )


        corpo_email = "\n".join(
            linhas
        )


        # -------------------------------------------------
        # MARCAR COMO PROCESSANDO
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE notificacoes

            SET
                status = 'PROCESSANDO',
                tentativas = tentativas + 1,
                erro = NULL,
                processado_em = LOCALTIMESTAMP

            WHERE id = %s
            """,
            (notificacao_id,),
        )


        # -------------------------------------------------
        # TENTAR ENVIO
        # -------------------------------------------------

        try:

            enviar_email(
                destinatario,
                assunto
                or "Convite - Priorado 146",
                corpo_email,
            )


        except (
            smtplib.SMTPException,
            OSError,
            RuntimeError,
        ) as erro_envio:

            cursor.execute(
                """
                UPDATE notificacoes

                SET
                    status = 'ERRO',
                    erro = %s

                WHERE id = %s
                """,
                (
                    str(erro_envio),
                    notificacao_id,
                ),
            )


            return {
                "status": "erro",
                "mensagem": (
                    "Falha ao enviar a notificação"
                ),
                "erro": str(
                    erro_envio
                ),
            }, 502


        # -------------------------------------------------
        # ENVIO BEM-SUCEDIDO
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE notificacoes

            SET
                status = 'ENVIADO',
                erro = NULL,
                enviado_em = LOCALTIMESTAMP

            WHERE id = %s
            """,
            (notificacao_id,),
        )


    return {
        "status": "ok",
        "mensagem": (
            "Notificação enviada com sucesso"
        ),
        "notificacao_id":
            notificacao_id,
        "destinatario":
            destinatario,
    }, 200

    # =========================================================
# PROCESSAR FILA DE NOTIFICAÇÕES
# =========================================================


@app.route(
    "/api/notificacoes/processar-fila",
    methods=["POST"],
)
def processar_fila_notificacoes():

    dados = request.get_json(
        silent=True
    ) or {}


    limite = dados.get(
        "limite",
        10
    )


    try:

        limite = int(
            limite
        )

    except (TypeError, ValueError):

        return {
            "status": "erro",
            "mensagem": "Limite inválido",
        }, 400


    if (
        limite < 1
        or limite > 50
    ):

        return {
            "status": "erro",
            "mensagem": (
                "O limite deve estar "
                "entre 1 e 50"
            ),
        }, 400


    # =====================================================
    # LOCALIZAR NOTIFICAÇÕES PENDENTES
    # =====================================================

    with (
        conectar_banco() as conexao,
        conexao.cursor() as cursor,
    ):

        cursor.execute(
            """
            SELECT id

            FROM notificacoes

            WHERE
                status = 'PENDENTE'
                AND canal = 'EMAIL'
                AND destinatario IS NOT NULL
                AND TRIM(destinatario) <> ''

            ORDER BY
                criado_em,
                id

            LIMIT %s
            """,
            (limite,),
        )


        registros = cursor.fetchall()


        notificacoes_ids = [
            registro[0]
            for registro in registros
        ]


        # Contar pendentes sem destinatário

        cursor.execute(
            """
            SELECT COUNT(*)

            FROM notificacoes

            WHERE
                status = 'PENDENTE'
                AND canal = 'EMAIL'
                AND (
                    destinatario IS NULL
                    OR TRIM(destinatario) = ''
                )
            """
        )


        registro_sem_destinatario = (
            cursor.fetchone()
        )


        if registro_sem_destinatario:

            sem_destinatario = (
                registro_sem_destinatario[0]
            )

        else:

            sem_destinatario = 0


    # =====================================================
    # PROCESSAR UMA POR UMA
    # =====================================================

    resultados = []

    enviados = 0
    erros = 0


    for notificacao_id in notificacoes_ids:

        resposta = enviar_notificacao(
            notificacao_id
        )


        corpo = resposta[0]
        codigo_http = resposta[1]


        if (
            codigo_http < 400
            and corpo.get("status") == "ok"
        ):

            enviados += 1

        else:

            erros += 1


        resultados.append(
            {
                "notificacao_id":
                    notificacao_id,

                "status":
                    corpo.get("status"),

                "mensagem":
                    corpo.get("mensagem"),

                "codigo_http":
                    codigo_http,
            }
        )


    return {
        "status": "ok",
        "mensagem": (
            "Processamento da fila concluído"
        ),
        "selecionadas": len(
            notificacoes_ids
        ),
        "enviadas": enviados,
        "erros": erros,
        "pendentes_sem_destinatario":
            sem_destinatario,
        "resultados":
            resultados,
    }, 200

    # =========================================================
# MOTOR GENÉRICO DE LEMBRETES
# =========================================================


@app.route(
    "/api/notificacoes/lembretes/gerar",
    methods=["POST"],
)
def gerar_lembretes_configurados():

    lembretes_criados = []
    participantes_avaliados = 0
    participantes_aplicaveis = 0
    ja_existentes = 0
    sem_destinatario = 0


    with (
        conectar_banco() as conexao,
        conexao.cursor() as cursor,
    ):

        # =================================================
        # 1. CARREGAR REGRAS ATIVAS
        # =================================================

        cursor.execute(
            """
            SELECT
                codigo,
                nome,
                antecedencia_minutos

            FROM configuracoes_lembrete

            WHERE ativo = TRUE

            ORDER BY
                antecedencia_minutos ASC
            """
        )

        registros_configuracoes = (
            cursor.fetchall()
        )


        configuracoes = []


        for registro in registros_configuracoes:

            configuracoes.append(
                {
                    "codigo": registro[0],
                    "nome": registro[1],
                    "antecedencia_minutos":
                        registro[2],
                }
            )


        if not configuracoes:

            return {
                "status": "ok",
                "mensagem": (
                    "Nenhuma regra de lembrete "
                    "está ativa"
                ),
                "participantes_avaliados": 0,
                "participantes_aplicaveis": 0,
                "lembretes_criados": 0,
                "ja_existentes": 0,
                "sem_destinatario": 0,
                "regras_ativas": [],
            }, 200


        # =================================================
        # 2. LOCALIZAR PARTICIPANTES PENDENTES
        # =================================================

        cursor.execute(
            """
            SELECT
                rp.id,
                r.id,
                r.titulo,
                r.data_hora,
                r.local,

                m.id,
                m.nome,
                m.email,

                rp.token_confirmacao,

                EXTRACT(
                    EPOCH FROM (
                        r.data_hora
                        - LOCALTIMESTAMP
                    )
                ) / 60.0
                    AS minutos_restantes

            FROM reuniao_participantes rp

            JOIN reunioes r
                ON r.id = rp.reuniao_id

            JOIN membros m
                ON m.id = rp.membro_id

            WHERE
                r.status = 'AGENDADA'

                AND r.data_hora
                    > LOCALTIMESTAMP

                AND rp.status_confirmacao
                    = 'PENDENTE'

            ORDER BY
                r.data_hora,
                m.nome
            """
        )

        participantes = cursor.fetchall()


        # =================================================
        # 3. AVALIAR CADA PARTICIPANTE
        # =================================================

        for participante in participantes:

            participantes_avaliados += 1


            participante_id = participante[0]

            reuniao_id = participante[1]

            titulo_reuniao = participante[2]

            data_hora = participante[3]

            local = participante[4]

            membro_id = participante[5]

            nome_membro = participante[6]

            email_membro = participante[7]

            token = participante[8]

            minutos_restantes = float(
                participante[9]
            )


            # =============================================
            # 4. IDENTIFICAR REGRA CORRETA
            # =============================================

            regra_atual = None


            for configuracao in configuracoes:

                if (
                    minutos_restantes
                    <= configuracao[
                        "antecedencia_minutos"
                    ]
                ):

                    regra_atual = configuracao

                    break


            # Reunião ainda está fora de todas
            # as janelas configuradas.
            if regra_atual is None:

                continue


            participantes_aplicaveis += 1


            # =============================================
            # 5. VERIFICAR SE JÁ EXISTE
            # =============================================

            cursor.execute(
                """
                SELECT id

                FROM notificacoes

                WHERE
                    reuniao_id = %s

                    AND membro_id = %s

                    AND tipo = 'LEMBRETE'

                    AND regra = %s

                LIMIT 1
                """,
                (
                    reuniao_id,
                    membro_id,
                    regra_atual["codigo"],
                ),
            )


            notificacao_existente = (
                cursor.fetchone()
            )


            if notificacao_existente is not None:

                ja_existentes += 1

                continue


            # =============================================
            # 6. GERAR TOKEN CASO NECESSÁRIO
            # =============================================

            if not token:

                token = (
                    gerar_token_confirmacao()
                )


                cursor.execute(
                    """
                    UPDATE reuniao_participantes

                    SET
                        token_confirmacao = %s,

                        token_criado_em =
                            LOCALTIMESTAMP,

                        token_expira_em = %s

                    WHERE id = %s
                    """,
                    (
                        token,
                        data_hora,
                        participante_id,
                    ),
                )


            # =============================================
            # 7. LINK DE CONFIRMAÇÃO
            # =============================================

            link = (
                "/confirmar/"
                + token
            )


            # =============================================
            # 8. MENSAGEM
            # =============================================

            mensagem = (
                "Lembrete de reunião - "
                + regra_atual["nome"]
                + ". "
                + "Reunião: "
                + titulo_reuniao
            )


            # =============================================
            # 9. CRIAR NOTIFICAÇÃO
            # =============================================

            cursor.execute(
                """
                INSERT INTO notificacoes (
                    reuniao_id,
                    membro_id,
                    tipo,
                    canal,
                    destinatario,
                    assunto,
                    mensagem,
                    link,
                    status,
                    regra
                )

                VALUES (
                    %s,
                    %s,
                    'LEMBRETE',
                    'EMAIL',
                    %s,
                    %s,
                    %s,
                    %s,
                    'PENDENTE',
                    %s
                )

                ON CONFLICT DO NOTHING

                RETURNING id
                """,
                (
                    reuniao_id,
                    membro_id,
                    email_membro,

                    (
                        "Lembrete - "
                        + titulo_reuniao
                    ),

                    mensagem,
                    link,
                    regra_atual["codigo"],
                ),
            )


            nova_notificacao = (
                cursor.fetchone()
            )


            if nova_notificacao is None:

                ja_existentes += 1

                continue


            if (
                email_membro is None
                or not email_membro.strip()
            ):

                sem_destinatario += 1


            lembretes_criados.append(
                {
                    "notificacao_id":
                        nova_notificacao[0],

                    "membro_id":
                        membro_id,

                    "membro":
                        nome_membro,

                    "reuniao_id":
                        reuniao_id,

                    "reuniao":
                        titulo_reuniao,

                    "regra":
                        regra_atual["codigo"],

                    "regra_nome":
                        regra_atual["nome"],

                    "minutos_restantes":
                        round(
                            minutos_restantes,
                            1,
                        ),

                    "destinatario":
                        email_membro,

                    "local":
                        local,
                }
            )


    return {
        "status": "ok",

        "mensagem":
            "Motor de lembretes executado",

        "participantes_avaliados":
            participantes_avaliados,

        "participantes_aplicaveis":
            participantes_aplicaveis,

        "lembretes_criados":
            len(lembretes_criados),

        "ja_existentes":
            ja_existentes,

        "sem_destinatario":
            sem_destinatario,

        "regras_ativas": [
            configuracao["codigo"]
            for configuracao
            in configuracoes
        ],

        "lembretes":
            lembretes_criados,
    }, 200

    # =========================================================
# GERAR LEMBRETES DE 24 HORAS
# =========================================================


@app.route(
    "/api/notificacoes/lembretes/gerar-24h",
    methods=["POST"],
)
def gerar_lembretes_24h():

    with (
        conectar_banco() as conexao,
        conexao.cursor() as cursor,
    ):

        # -------------------------------------------------
        # REUNIÕES NAS PRÓXIMAS 24H
        # COM PARTICIPANTES AINDA PENDENTES
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                rp.id,
                r.id,
                r.titulo,
                r.data_hora,
                r.local,
                m.id,
                m.nome,
                m.email,
                rp.token_confirmacao

            FROM reuniao_participantes rp

            JOIN reunioes r
                ON r.id = rp.reuniao_id

            JOIN membros m
                ON m.id = rp.membro_id

            WHERE
                r.status = 'AGENDADA'

                AND r.data_hora >
                    LOCALTIMESTAMP

                AND r.data_hora <=
                    LOCALTIMESTAMP
                    + INTERVAL '24 hours'

                AND rp.status_confirmacao =
                    'PENDENTE'

            ORDER BY
                r.data_hora,
                m.nome
            """
        )

        registros = cursor.fetchall()


        lembretes_criados = []


        for registro in registros:

            participante_id = registro[0]
            reuniao_id = registro[1]
            titulo = registro[2]
            data_hora = registro[3]
            local = registro[4]
            membro_id = registro[5]
            nome = registro[6]
            email = registro[7]
            token = registro[8]


            # ---------------------------------------------
            # GARANTIR TOKEN DE CONFIRMAÇÃO
            # ---------------------------------------------

            if token is None:

                token = gerar_token_confirmacao()


                cursor.execute(
                    """
                    UPDATE reuniao_participantes

                    SET
                        token_confirmacao = %s,
                        token_criado_em =
                            LOCALTIMESTAMP,
                        token_expira_em = %s

                    WHERE id = %s
                    """,
                    (
                        token,
                        data_hora,
                        participante_id,
                    ),
                )


            link = (
                "/confirmar/"
                + token
            )


            assunto = (
                "Lembrete - "
                + titulo
            )


            mensagem = (
                "Olá, "
                + nome
                + ". Lembramos que você ainda "
                + "não confirmou sua participação "
                + "na reunião "
                + titulo
                + "."
            )


            cursor.execute(
                """
                INSERT INTO notificacoes (
                    reuniao_id,
                    membro_id,
                    tipo,
                    canal,
                    destinatario,
                    assunto,
                    mensagem,
                    link,
                    status,
                    regra
                )

                VALUES (
                    %s,
                    %s,
                    'LEMBRETE',
                    'EMAIL',
                    %s,
                    %s,
                    %s,
                    %s,
                    'PENDENTE',
                    '24H'
                )

                ON CONFLICT DO NOTHING

                RETURNING id
                """,
                (
                    reuniao_id,
                    membro_id,
                    email,
                    assunto,
                    mensagem,
                    link,
                ),
            )


            notificacao = cursor.fetchone()


            if notificacao:

                lembretes_criados.append(
                    {
                        "id":
                            notificacao[0],

                        "reuniao_id":
                            reuniao_id,

                        "membro_id":
                            membro_id,

                        "nome":
                            nome,

                        "email":
                            email,

                        "titulo":
                            titulo,

                        "data_hora":
                            data_hora.isoformat(),

                        "local":
                            local,
                    }
                )


    return {
        "status": "ok",
        "mensagem": (
            "Geração de lembretes concluída"
        ),
        "participantes_encontrados":
            len(registros),
        "lembretes_criados":
            len(lembretes_criados),
        "lembretes":
            lembretes_criados,
    }, 200

    # =========================================================
# CONFIGURAÇÕES DE LEMBRETES
# =========================================================


@app.route(
    "/api/configuracoes-lembrete",
    methods=["GET"],
)
def listar_configuracoes_lembrete():

    with (
        conectar_banco() as conexao,
        conexao.cursor() as cursor,
    ):

        cursor.execute(
            """
            SELECT
                id,
                codigo,
                nome,
                antecedencia_minutos,
                ativo,
                ordem

            FROM configuracoes_lembrete

            ORDER BY
                ordem,
                id
            """
        )

        registros = cursor.fetchall()


    configuracoes = []


    for registro in registros:

        configuracoes.append(
            {
                "id": registro[0],
                "codigo": registro[1],
                "nome": registro[2],
                "antecedencia_minutos":
                    registro[3],
                "ativo": registro[4],
                "ordem": registro[5],
            }
        )


    return {
        "status": "ok",
        "configuracoes": configuracoes,
    }, 200

@app.route(
    "/api/configuracoes-lembrete/<int:configuracao_id>",
    methods=["PUT"],
)
def atualizar_configuracao_lembrete(
    configuracao_id
):

    dados = request.get_json(
        silent=True
    )


    if dados is None:

        return {
            "status": "erro",
            "mensagem": "JSON não recebido",
        }, 400


    ativo = dados.get(
        "ativo"
    )


    if not isinstance(
        ativo,
        bool
    ):

        return {
            "status": "erro",
            "mensagem": (
                "O campo ativo deve ser "
                "true ou false"
            ),
        }, 400


    with (
        conectar_banco() as conexao,
        conexao.cursor() as cursor,
    ):

        cursor.execute(
            """
            UPDATE configuracoes_lembrete

            SET
                ativo = %s,
                atualizado_em =
                    LOCALTIMESTAMP

            WHERE id = %s

            RETURNING
                id,
                codigo,
                nome,
                antecedencia_minutos,
                ativo,
                ordem
            """,
            (
                ativo,
                configuracao_id,
            ),
        )

        registro = cursor.fetchone()


    if registro is None:

        return {
            "status": "erro",
            "mensagem": (
                "Configuração não encontrada"
            ),
        }, 404


    return {
        "status": "ok",
        "mensagem": (
            "Configuração atualizada"
        ),
        "configuracao": {
            "id": registro[0],
            "codigo": registro[1],
            "nome": registro[2],
            "antecedencia_minutos":
                registro[3],
            "ativo": registro[4],
            "ordem": registro[5],
        },
    }, 200

    # =========================================================
# HISTÓRICO DA AUTOMAÇÃO
# =========================================================


def normalizar_json_execucao(valor):

    if valor is None or valor == "":
        return {}

    if isinstance(valor, dict):
        return valor

    if isinstance(valor, str):

        try:

            return json.loads(valor)

        except json.JSONDecodeError:

            return {}

    return {}


# =========================================================
# REGISTRAR EXECUÇÃO
# =========================================================


@app.route(
    "/api/automacao/execucoes",
    methods=["POST"],
)
def registrar_execucao_automacao():

    dados = request.get_json(
        silent=True
    )

    if dados is None:

        dados = request.form.to_dict()


    origem = (
        dados.get("origem")
        or "NAO_INFORMADA"
    )


    status = (
        dados.get("status")
        or "FAILED"
    ).upper()


    if status not in (
        "SUCCESS",
        "FAILED",
    ):

        return {
            "status": "erro",
            "mensagem":
                "Status da execução inválido",
        }, 400


    lembretes = normalizar_json_execucao(
        dados.get("lembretes")
    )


    fila = normalizar_json_execucao(
        dados.get("fila")
    )


    mensagem_erro = (
        dados.get("erro")
        or None
    )


    participantes_avaliados = int(
        lembretes.get(
            "participantes_avaliados",
            0,
        )
        or 0
    )


    participantes_aplicaveis = int(
        lembretes.get(
            "participantes_aplicaveis",
            0,
        )
        or 0
    )


    lembretes_criados = int(
        lembretes.get(
            "lembretes_criados",
            0,
        )
        or 0
    )


    lembretes_existentes = int(
        lembretes.get(
            "ja_existentes",
            0,
        )
        or 0
    )


    fila_selecionadas = int(
        fila.get(
            "selecionadas",
            0,
        )
        or 0
    )


    emails_enviados = int(
        fila.get(
            "enviadas",
            0,
        )
        or 0
    )


    erros = int(
        fila.get(
            "erros",
            0,
        )
        or 0
    )


    sem_destinatario = int(
        fila.get(
            "pendentes_sem_destinatario",
            0,
        )
        or 0
    )


    with (
        conectar_banco() as conexao,
        conexao.cursor() as cursor,
    ):

        cursor.execute(
            """
            INSERT INTO execucoes_automacao (
                origem,
                status,
                participantes_avaliados,
                participantes_aplicaveis,
                lembretes_criados,
                lembretes_existentes,
                fila_selecionadas,
                emails_enviados,
                erros,
                sem_destinatario,
                detalhe_lembretes,
                detalhe_fila,
                mensagem_erro
            )

            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s::jsonb,
                %s::jsonb,
                %s
            )

            RETURNING
                id,
                executado_em
            """,
            (
                origem,
                status,
                participantes_avaliados,
                participantes_aplicaveis,
                lembretes_criados,
                lembretes_existentes,
                fila_selecionadas,
                emails_enviados,
                erros,
                sem_destinatario,
                json.dumps(lembretes),
                json.dumps(fila),
                mensagem_erro,
            ),
        )

        registro = cursor.fetchone()


    return {
        "status": "ok",
        "mensagem":
            "Execução registrada",
        "execucao_id":
            registro[0],
        "executado_em":
            registro[1].isoformat(),
    }, 201


# =========================================================
# CONSULTAR HISTÓRICO
# =========================================================


@app.route(
    "/api/automacao/execucoes",
    methods=["GET"],
)
def listar_execucoes_automacao():

    limite = request.args.get(
        "limite",
        default=20,
        type=int,
    )


    limite = max(
        1,
        min(
            limite,
            100,
        ),
    )


    with (
        conectar_banco() as conexao,
        conexao.cursor() as cursor,
    ):

        cursor.execute(
            """
            SELECT
                id,
                executado_em,
                origem,
                status,
                participantes_avaliados,
                participantes_aplicaveis,
                lembretes_criados,
                lembretes_existentes,
                fila_selecionadas,
                emails_enviados,
                erros,
                sem_destinatario,
                mensagem_erro

            FROM execucoes_automacao

            ORDER BY
                executado_em DESC,
                id DESC

            LIMIT %s
            """,
            (
                limite,
            ),
        )

        registros = cursor.fetchall()


    execucoes = []


    for registro in registros:

        execucoes.append(
            {
                "id":
                    registro[0],

                "executado_em":
                    registro[1].isoformat(),

                "origem":
                    registro[2],

                "status":
                    registro[3],

                "participantes_avaliados":
                    registro[4],

                "participantes_aplicaveis":
                    registro[5],

                "lembretes_criados":
                    registro[6],

                "lembretes_existentes":
                    registro[7],

                "fila_selecionadas":
                    registro[8],

                "emails_enviados":
                    registro[9],

                "erros":
                    registro[10],

                "sem_destinatario":
                    registro[11],

                "mensagem_erro":
                    registro[12],
            }
        )


    return {
        "status": "ok",

        "total_retornado":
            len(execucoes),

        "execucoes":
            execucoes,
    }, 200

    # =========================================================
# SAÚDE OPERACIONAL
# =========================================================


@app.route(
    "/api/saude",
    methods=["GET"],
)
def consultar_saude():

    smtp_configurado = all(
        [
            os.getenv("SMTP_HOST"),
            os.getenv("SMTP_PORT"),
            os.getenv("SMTP_USER"),
            os.getenv("SMTP_PASSWORD"),
        ]
    )


    try:

        with (
            conectar_banco() as conexao,
            conexao.cursor() as cursor,
        ):

            # =============================================
            # BANCO
            # =============================================

            cursor.execute(
                """
                SELECT 1
                """
            )

            cursor.fetchone()


            # =============================================
            # ÚLTIMA EXECUÇÃO DA AUTOMAÇÃO
            # =============================================

            cursor.execute(
                """
                SELECT
                    id,
                    executado_em,
                    origem,
                    status,

                    EXTRACT(
                        EPOCH FROM (
                            LOCALTIMESTAMP
                            - executado_em
                        )
                    ) / 60.0
                        AS minutos_desde_execucao,

                    participantes_avaliados,
                    participantes_aplicaveis,
                    lembretes_criados,
                    emails_enviados,
                    erros,
                    sem_destinatario

                FROM execucoes_automacao

                ORDER BY
                    executado_em DESC,
                    id DESC

                LIMIT 1
                """
            )

            ultima_execucao = (
                cursor.fetchone()
            )


            # =============================================
            # FILA PENDENTE
            # =============================================

            cursor.execute(
                """
                SELECT COUNT(*)

                FROM notificacoes

                WHERE status = 'PENDENTE'
                """
            )

            fila_pendente = (
                cursor.fetchone()[0]
            )


            # =============================================
            # FILA COM ERRO
            # =============================================

            cursor.execute(
                """
                SELECT COUNT(*)

                FROM notificacoes

                WHERE status = 'ERRO'
                """
            )

            fila_erro = (
                cursor.fetchone()[0]
            )


            # =============================================
            # SEM DESTINATÁRIO
            # =============================================

            cursor.execute(
                """
                SELECT COUNT(*)

                FROM notificacoes

                WHERE
                    canal = 'EMAIL'

                    AND status IN (
                        'PENDENTE',
                        'ERRO'
                    )

                    AND (
                        destinatario IS NULL
                        OR TRIM(destinatario) = ''
                    )
                """
            )

            sem_destinatario = (
                cursor.fetchone()[0]
            )


            # =============================================
            # REGRAS ATIVAS
            # =============================================

            cursor.execute(
                """
                SELECT COUNT(*)

                FROM configuracoes_lembrete

                WHERE ativo = TRUE
                """
            )

            regras_ativas = (
                cursor.fetchone()[0]
            )


    except psycopg.Error as erro_banco:

        return {
            "sistema": "FALHA",

            "aplicacao": "OK",

            "banco": "ERRO",

            "automacao": "NAO_VERIFICADA",

            "smtp":
                (
                    "CONFIGURADO"
                    if smtp_configurado
                    else "NAO_CONFIGURADO"
                ),

            "mensagem":
                "Falha ao consultar PostgreSQL",

            "erro":
                str(erro_banco),
        }, 503

    tolerancia_automacao = (
        obter_configuracao_sistema(
            "AUTOMACAO_TOLERANCIA_MINUTOS",
            20,
        )
    )


    # =====================================================
    # AVALIAR AUTOMAÇÃO
    # =====================================================

    automacao = "SEM_HISTORICO"

    minutos_desde_execucao = None

    ultima_execucao_dados = None


    if ultima_execucao is not None:

        minutos_desde_execucao = float(
            ultima_execucao[4]
        )


        if ultima_execucao[3] == "FAILED":

            automacao = "ERRO"


        elif minutos_desde_execucao <= tolerancia_automacao:

            automacao = "OK"


        else:

            automacao = "ATRASADA"


        ultima_execucao_dados = {
            "id":
                ultima_execucao[0],

            "executado_em":
                ultima_execucao[1].isoformat(),

            "origem":
                ultima_execucao[2],

            "status":
                ultima_execucao[3],

            "minutos_desde_execucao":
                round(
                    minutos_desde_execucao,
                    1,
                ),

            "participantes_avaliados":
                ultima_execucao[5],

            "participantes_aplicaveis":
                ultima_execucao[6],

            "lembretes_criados":
                ultima_execucao[7],

            "emails_enviados":
                ultima_execucao[8],

            "erros":
                ultima_execucao[9],

            "sem_destinatario":
                ultima_execucao[10],
        }


    # =====================================================
    # STATUS GLOBAL
    # =====================================================

    sistema = "OPERACIONAL"


    if automacao == "ERRO":

        sistema = "FALHA"


    elif (
        automacao in (
            "ATRASADA",
            "SEM_HISTORICO",
        )
        or fila_erro > 0
        or sem_destinatario > 0
        or not smtp_configurado
    ):

        sistema = "ATENCAO"


    return {
        "sistema":
            sistema,

        "aplicacao":
            "OK",

        "banco":
            "OK",

        "automacao":
            automacao,

        "smtp":
            (
                "CONFIGURADO"
                if smtp_configurado
                else "NAO_CONFIGURADO"
            ),

        "regras_ativas":
            regras_ativas,

        "fila": {
            "pendentes":
                fila_pendente,

            "erros":
                fila_erro,

            "sem_destinatario":
                sem_destinatario,
        },

        "ultima_execucao":
            ultima_execucao_dados,

    }, 200

    # =========================================================
# CONFIGURAÇÕES DO SISTEMA
# =========================================================


@app.route(
    "/api/configuracoes-sistema",
    methods=["GET"],
)
def listar_configuracoes_sistema():

    with (
        conectar_banco() as conexao,
        conexao.cursor() as cursor,
    ):

        cursor.execute(
            """
            SELECT
                id,
                chave,
                valor,
                tipo,
                descricao,
                editavel,
                atualizado_em

            FROM configuracoes_sistema

            ORDER BY
                chave
            """
        )

        registros = cursor.fetchall()


    configuracoes = []


    for registro in registros:

        configuracoes.append(
            {
                "id":
                    registro[0],

                "chave":
                    registro[1],

                "valor":
                    registro[2],

                "tipo":
                    registro[3],

                "descricao":
                    registro[4],

                "editavel":
                    registro[5],

                "atualizado_em":
                    registro[6].isoformat(),
            }
        )


    return {
        "status": "ok",
        "configuracoes":
            configuracoes,
    }, 200

    @app.route(
    "/api/configuracoes-sistema/<string:chave>",
    methods=["PUT"],
)
    def atualizar_configuracao_sistema(
        chave
    ):

        dados = request.get_json(
            silent=True
        )


        if dados is None:

            return {
                "status": "erro",
                "mensagem":
                    "JSON não recebido",
            }, 400


        if "valor" not in dados:

            return {
                "status": "erro",
                "mensagem":
                    "Campo valor não informado",
            }, 400


        novo_valor = dados.get(
            "valor"
        )


        with (
            conectar_banco() as conexao,
            conexao.cursor() as cursor,
        ):

            cursor.execute(
                """
                SELECT
                    tipo,
                    editavel

                FROM configuracoes_sistema

                WHERE chave = %s
                """,
                (
                    chave,
                ),
            )


            configuracao = cursor.fetchone()


            if configuracao is None:

                return {
                    "status": "erro",
                    "mensagem":
                        "Configuração não encontrada",
                }, 404


            tipo = configuracao[0]

            editavel = configuracao[1]


            if not editavel:

                return {
                    "status": "erro",
                    "mensagem":
                        "Configuração não editável",
                }, 403


            # =============================================
            # VALIDAR VALOR
            # =============================================

            if tipo == "INTEGER":

                try:

                    valor_validado = int(
                        novo_valor
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    return {
                        "status": "erro",
                        "mensagem":
                            "Valor deve ser inteiro",
                    }, 400


                if valor_validado <= 0:

                    return {
                        "status": "erro",
                        "mensagem":
                            "Valor deve ser maior que zero",
                    }, 400


                if (
                    chave
                    == "FILA_LIMITE_PROCESSAMENTO"
                    and valor_validado > 50
                ):

                    return {
                        "status": "erro",
                        "mensagem":
                            "Limite máximo da fila é 50",
                    }, 400


                novo_valor = str(
                    valor_validado
                )


            elif tipo == "BOOLEAN":

                if not isinstance(
                    novo_valor,
                    bool,
                ):

                    return {
                        "status": "erro",
                        "mensagem":
                            "Valor deve ser true ou false",
                    }, 400


                novo_valor = (
                    "true"
                    if novo_valor
                    else "false"
                )


            else:

                novo_valor = str(
                    novo_valor
                ).strip()


            cursor.execute(
                """
                UPDATE configuracoes_sistema

                SET
                    valor = %s,
                    atualizado_em =
                        LOCALTIMESTAMP

                WHERE chave = %s

                RETURNING
                    id,
                    chave,
                    valor,
                    tipo,
                    descricao,
                    editavel,
                    atualizado_em
                """,
                (
                    novo_valor,
                    chave,
                ),
            )


            registro = cursor.fetchone()


        return {
            "status": "ok",

            "mensagem":
                "Configuração atualizada",

            "configuracao": {
                "id":
                    registro[0],

                "chave":
                    registro[1],

                "valor":
                    registro[2],

                "tipo":
                    registro[3],

                "descricao":
                    registro[4],

                "editavel":
                    registro[5],

                "atualizado_em":
                    registro[6].isoformat(),
            },
        }, 200


# =========================================================
# INICIAR FLASK
# =========================================================

if __name__ == "__main__":

    print(app.url_map)

    app.run(
        debug=True,
        port=5001
    )