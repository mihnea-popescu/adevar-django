from users.models import User
from django.conf import settings
from django.core.mail import send_mail

# @shared_task
def send_reset_password_email(user_id: int, token: str):
    user = User.objects.filter(id=user_id).first()

    if not user:
        return

    url = f"{settings.BACKEND_URL}/users/auth/reset-password/{token}?email={user.email}"

    html_message = f"""
    <p>You have requested a password reset.</p><br/>
    <p>You may reset your account by clicking <a href="{url}">here</a>.</p><br/>
    <p>This reset link is valid for 60 minutes.</p></br>
    <p>If you haven't registered an account, ignore this email.</p>
    <p>adevarapp.com</p>
    """

    send_mail(
        "Adevar - Password Reset",
        "",
        "noreply@adevarapp.com",
        [user.email],
        fail_silently=False,
        html_message=html_message,
    )

    return True