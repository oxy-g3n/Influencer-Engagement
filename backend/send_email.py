import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(receiver_email, subject, html_content, sender_password="zwwz scee hhmk zsuf", sender_email="unstopabledestroyer77@gmail.com"):
    try:
        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject

        # Add HTML content to email
        message.attach(MIMEText(html_content, "html"))

        # Create SMTP session for Gmail
        smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
        smtp_server.starttls()  # Enable encryption

        # Login to Gmail
        smtp_server.login(sender_email, sender_password)

        # Send email
        smtp_server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")

    except Exception as e:
        print(f"Error sending email: {e}")

    finally:
        # Close SMTP connection
        smtp_server.quit()

