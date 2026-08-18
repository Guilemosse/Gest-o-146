#!/bin/zsh

# =========================================================
# LOCALE / UTF-8
# Necessário quando executado pelo macOS launchd
# =========================================================

export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"


BASE_URL="http://127.0.0.1:5001"

PROJECT_DIR="$HOME/VS projects/Priorado146"

LOG_DIR="$PROJECT_DIR/logs"

LOG_FILE="$LOG_DIR/automacao.log"


/bin/mkdir -p "$LOG_DIR"


# =========================================================
# IDENTIFICAR ORIGEM DA EXECUÇÃO
# =========================================================

if [ -t 1 ]; then

    ORIGEM="SCRIPT_MANUAL"

else

    ORIGEM="LAUNCHD"

fi


{
    echo "========================================"
    echo "CICLO PRIORADO146"
    echo "DATA: $(/bin/date '+%Y-%m-%d %H:%M:%S')"
    echo "ORIGEM: $ORIGEM"
    echo "========================================"

    echo
    echo "[1] Executando motor de lembretes..."


    LEMBRETES_JSON=$(
        /usr/bin/curl \
            --fail \
            --silent \
            --show-error \
            -X POST \
            "$BASE_URL/api/notificacoes/lembretes/gerar"
    )


    CODIGO_LEMBRETES=$?


    echo "$LEMBRETES_JSON"

    echo


    FILA_JSON='{}'

    STATUS_FINAL="SUCCESS"

    ERRO_FINAL=""


    # =====================================================
    # MOTOR DE LEMBRETES FALHOU
    # =====================================================

    if [ "$CODIGO_LEMBRETES" -ne 0 ]; then

        STATUS_FINAL="FAILED"

        ERRO_FINAL="Falha ao executar motor de lembretes"


    else

        # =================================================
        # PROCESSAR FILA
        # =================================================

        echo
        echo "[2] Processando fila de notificações..."


        FILA_JSON=$(
            /usr/bin/curl \
                --fail \
                --silent \
                --show-error \
                -X POST \
                "$BASE_URL/api/notificacoes/processar-fila" \
                -H "Content-Type: application/json" \
                -d '{
                    "limite": 10
                }'
        )


        CODIGO_FILA=$?


        echo "$FILA_JSON"

        echo


        if [ "$CODIGO_FILA" -ne 0 ]; then

            STATUS_FINAL="FAILED"

            ERRO_FINAL="Falha ao processar fila de notificações"

        fi

    fi


    # =====================================================
    # REGISTRAR EXECUÇÃO
    # =====================================================

    echo
    echo "[3] Registrando histórico da execução..."


    REGISTRO_JSON=$(
        /usr/bin/curl \
            --fail \
            --silent \
            --show-error \
            -X POST \
            "$BASE_URL/api/automacao/execucoes" \
            --data-urlencode \
            "origem=$ORIGEM" \
            --data-urlencode \
            "status=$STATUS_FINAL" \
            --data-urlencode \
            "lembretes=$LEMBRETES_JSON" \
            --data-urlencode \
            "fila=$FILA_JSON" \
            --data-urlencode \
            "erro=$ERRO_FINAL"
    )


    CODIGO_REGISTRO=$?


    echo "$REGISTRO_JSON"

    echo


    if [ "$CODIGO_REGISTRO" -ne 0 ]; then

        echo "ERRO: não foi possível registrar histórico."

        exit 1
    fi


    # =====================================================
    # RESULTADO FINAL
    # =====================================================

    if [ "$STATUS_FINAL" = "FAILED" ]; then

        echo "CICLO FINALIZADO COM ERRO"

        exit 1
    fi


    echo "CICLO FINALIZADO COM SUCESSO"

    echo


} >> "$LOG_FILE" 2>&1