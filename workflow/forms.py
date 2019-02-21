from django.contrib.auth.forms import PasswordResetForm


class CoreUserPasswordResetForm(PasswordResetForm):
    """
    Form for using built-in django logic for resetting password. Only send_mail method is overridden.
    """

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Sending of password reset message is overridden here.
        """
        # TODO: implement message sending here
        return
