from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.conf import settings


def send_email(
    email_address: str,
    subject: str,
    context: dict,
    template_name: str,
    html_template_name: str = None,
) -> int:
    text_content = loader.render_to_string(template_name, context, using=None)
    html_content = (
        loader.render_to_string(html_template_name, context, using=None)
        if html_template_name
        else None
    )
    return send_email_body(email_address, subject, text_content, html_content)


def send_email_body(
    email_address: str, subject: str, text_content: str, html_content: str = None
) -> int:
    msg = EmailMultiAlternatives(
        from_email=settings.DEFAULT_FROM_EMAIL,
        subject=subject,
        body=text_content,
        to=[email_address],
    )
    if settings.DEFAULT_REPLYTO_EMAIL:
        msg.reply_to = [settings.DEFAULT_REPLYTO_EMAIL]
    if html_content:
        msg.attach_alternative(html_content, "text/html")
    return msg.send()
