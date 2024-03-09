from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse

# Send Email
def send_mail(to, template, context):
    html_content = render_to_string(f'accounts/emails/{template}.html', context)
    text_content = render_to_string(f'accounts/emails/{template}.txt', context)

    msg = EmailMultiAlternatives(context['subject'], text_content, settings.DEFAULT_FROM_EMAIL, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

# Send Activation Email
def send_activation_email(request, email, code):
    context = {
        'subject' : 'Activate your account',
        'uri' : request.build_absolute_uri(reverse('accounts:activate', kwargs={'code': code})),
    }
    send_mail(email, 'activate_profile', context)