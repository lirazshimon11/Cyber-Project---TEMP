import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import global_use_for_server


def init_smtp_server():
    """
    This function's purpose is to set the smtp server and login the given email
    (from the global function - global_use_for_server)
    :return: Nothing.
    """
    try:
        global_use_for_server.SMTP_SERVER = smtplib.SMTP('smtp.gmail.com', 587)
        global_use_for_server.SMTP_SERVER.starttls()
        global_use_for_server.SMTP_SERVER.login(global_use_for_server.MAIL_SENDER, global_use_for_server.MAIL_PASSWORD)
        print(f"logged in!")
    except Exception as e:
        print(f"Error initializing sender: {e}")


def send_mail(code="000000", target_email='lirazshimonx@gmail.com'):
    """
    This function's purpose is to mail the given email with the given code.
    :param code: string. for identification.
    :param target_email: string.
    :return: boolean. True if successful, otherwise False.
    """
    print(f"Start - message {target_email}")
    # Create the email content
    subject = f'Email verification code: {code}'
    message = f"Dear {target_email.split('@')[0]},\n\nGreetings from Meet&Share!\n\nWe've received a request to login to your account. Please use the following code:\n\n{code}\n\nIf you didn't request this code, please ignore this email.\n\nBest regards,\nThe Meet&Share Team"

    msg = MIMEMultipart()
    msg['From'] = global_use_for_server.MAIL_SENDER
    msg['To'] = target_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    print(f"Mid1 - message {target_email}")

    # Send the email
    try:
        global_use_for_server.SMTP_SERVER.sendmail(global_use_for_server.MAIL_SENDER, target_email, msg.as_string())
        print(f"Mail sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False
