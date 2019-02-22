from django.core.mail import EmailMultiAlternatives
from django.template import loader


def send_email(email_address: str, subject: str, context: dict, template_name: str,
               html_template_name: str = None) -> int:
    text_content = loader.render_to_string(template_name, context, using=None)
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        to=[email_address],
    )
    if html_template_name:
        html_content = loader.render_to_string(html_template_name, context, using=None)
        msg.attach_alternative(html_content, "text/html")
    return msg.send()
