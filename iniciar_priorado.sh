#!/bin/zsh

PROJECT_DIR="$HOME/VS projects/Priorado146"

PYTHON="$PROJECT_DIR/.venv/bin/python"

LOG_DIR="$PROJECT_DIR/logs"


mkdir -p "$LOG_DIR"


export SMTP_HOST="smtp.gmail.com"

export SMTP_PORT="587"

export SMTP_USER="guilemos.se@gmail.com"

export APP_BASE_URL="http://127.0.0.1:5001"


SMTP_PASSWORD=$(
    /usr/bin/security \
        find-generic-password \
        -a "$USER" \
        -s "priorado146.smtp" \
        -w
)


if [ -z "$SMTP_PASSWORD" ]; then

    echo "ERRO: senha SMTP não encontrada no Keychain"

    exit 1
fi


export SMTP_PASSWORD


cd "$PROJECT_DIR" || exit 1


exec "$PYTHON" script2.py