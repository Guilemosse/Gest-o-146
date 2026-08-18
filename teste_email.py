import os
import smtplib
import ssl
from email.message import EmailMessage

smtp_host = os.getenv("SMTP_HOST")
smtp_port = os.getenv("SMTP_PORT")
smtp_user = os.getenv("SMTP_USER")
smtp_password = os.getenv("SMTP_PASSWORD")
smtp_to = os.getenv("SMTP_TO")


if not smtp_host:
    raise RuntimeError("SMTP_HOST não configurado")

if not smtp_port:
    raise RuntimeError("SMTP_PORT não configurado")

if not smtp_user:
    raise RuntimeError("SMTP_USER não configurado")

if not smtp_password:
    raise RuntimeError("SMTP_PASSWORD não configurado")

if not smtp_to:
    raise RuntimeError("SMTP_TO não configurado")


mensagem = EmailMessage()

mensagem["From"] = smtp_user
mensagem["To"] = smtp_to
mensagem["Subject"] = "Teste de envio - Priorado 146"

mensagem.set_content(
    """
Olá.

Este é o primeiro e-mail enviado
automaticamente pelo sistema Priorado 146.

Se você recebeu esta mensagem,
o SMTP está funcionando corretamente.

Priorado 146
"""
)


contexto_ssl = ssl.create_default_context()


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


print("EMAIL_ENVIADO=SIM")