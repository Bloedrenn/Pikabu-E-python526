from django.core.mail import send_mail
from django.conf import settings


def send_mail_custom(
    subject: str,
    html_message: str,
    recipient_list: list[str],
    message: str = "",
    from_email: str = settings.DEFAULT_FROM_EMAIL
) -> None:
    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        html_message=html_message,  
    )
