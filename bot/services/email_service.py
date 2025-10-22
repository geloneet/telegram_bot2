import uuid

def send_sp_email(to_emails, base_subject, smtp_info):
    try:
        import smtplib, ssl, certifi
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        smtp_server = smtp_info["server"]
        smtp_port = smtp_info["port"]
        smtp_user = smtp_info["user"]
        smtp_password = smtp_info["password"]
        display_name = smtp_info["name"]

        # Configuración SSL/TLS dinámica según el puerto
        context = ssl.create_default_context(cafile=certifi.where())

        for to_email in to_emails:
            # Preparar correo
            subject = f"{base_subject} - {uuid.uuid4()}"  # Añadir un sufijo único al asunto
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{display_name} <{smtp_user}>"
            msg["To"] = to_email
            msg["Message-ID"] = f"<{uuid.uuid4()}@{smtp_server}>"  # Añadir Message-ID único

            html = f"""
            <html>
                <body>
                    <p>Hola,<br>
                    Este es un correo enviado de confirmación de compra.<br>
                    Asunto: <b>{subject}</b>
                    </p>
                </body>
            </html>
            """
            msg.attach(MIMEText(html, "html"))

            if smtp_port == 465:
                # Conexión SSL directa (ej. Gmail, PixelTec)
                with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                    server.login(smtp_user, smtp_password)
                    server.sendmail(smtp_user, to_email, msg.as_string())
            elif smtp_port == 587:
                # Conexión STARTTLS (ej. IONOS, Outlook)
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.login(smtp_user, smtp_password)
                    server.sendmail(smtp_user, to_email, msg.as_string())
            else:
                raise ValueError(f"Puerto SMTP no soportado: {smtp_port}")

        return True

    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False