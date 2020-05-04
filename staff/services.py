from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


class StaffService:
    def send_registration_otp(self, otp):
        from_email = settings.FROM_EMAIL
        to = otp.user.email
        subject = "CABABAへの仮登録通知"
        context = {'otp': otp, 'host_name': settings.HOST_NAME}
        msg_plain = render_to_string('staff/email/register.txt', context)
        msg_html = render_to_string('staff/email/register.html', context)
        send_mail(subject, msg_plain, from_email, [to], html_message=msg_html)