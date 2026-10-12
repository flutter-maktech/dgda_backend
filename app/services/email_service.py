import resend
from app.core.config import settings

# Configure Resend with user API key
resend.api_key = settings.RESEND_API_KEY


def send_otp_email(to_email: str, otp_code: str, purpose: str = "VERIFICATION") -> bool:
    """
    Send a 6-digit OTP security code via Resend with professional DGDA styling.
    """
    try:
        is_password_reset = purpose == "PASSWORD_RESET"
        title_text = "Réinitialisation de mot de passe" if is_password_reset else "Vérification de compte"
        subtitle_text = "Votre code de sécurité pour réinitialiser votre mot de passe" if is_password_reset else "Votre code de sécurité pour valider votre compte DGDA"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7fa; margin: 0; padding: 20px; }}
            .container {{ max-width: 520px; margin: auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 14px rgba(0,0,0,0.06); border: 1px solid #e1e8ed; }}
            .header {{ background-color: #0B2545; color: #ffffff; padding: 28px 20px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 22px; font-weight: 700; letter-spacing: 0.5px; }}
            .header p {{ margin: 6px 0 0; font-size: 13px; color: #DAEBFB; opacity: 0.9; }}
            .body {{ padding: 30px 24px; color: #2D3748; line-height: 1.6; }}
            .greeting {{ font-size: 16px; font-weight: 600; margin-bottom: 12px; }}
            .otp-box {{ background-color: #F0F6FD; border: 2px dashed #0B2545; border-radius: 10px; padding: 18px; text-align: center; margin: 24px 0; }}
            .otp-code {{ font-size: 34px; font-weight: 800; letter-spacing: 8px; color: #0B2545; font-family: monospace; display: inline-block; }}
            .expiry {{ font-size: 13px; color: #718096; margin-top: 8px; }}
            .footer {{ background-color: #FAFCFE; padding: 18px 24px; border-top: 1px solid #EDF2F7; font-size: 12px; color: #A0AEC0; text-align: center; }}
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>DGDA RDC</h1>
              <p>Direction Générale des Douanes et Accises</p>
            </div>
            <div class="body">
              <div class="greeting">Bonjour,</div>
              <p>{subtitle_text} :</p>
              
              <div class="otp-box">
                <div class="otp-code">{otp_code}</div>
                <div class="expiry">Ce code expire dans {settings.OTP_EXPIRE_MINUTES} minutes.</div>
              </div>
              
              <p style="font-size: 13px; color: #4A5568;">
                Pour des raisons de sécurité, ne communiquez jamais ce code à un tiers. Les agents de la DGDA ne vous demanderont jamais votre code par téléphone.
              </p>
            </div>
            <div class="footer">
              Direction Générale des Douanes et Accises — République Démocratique du Congo<br/>
              Plateforme Numérique Officielle
            </div>
          </div>
        </body>
        </html>
        """

        params = {
            "from": settings.EMAILS_FROM,
            "to": [to_email],
            "subject": f"DGDA — Votre code de sécurité : {otp_code}",
            "html": html_content,
        }

        response = resend.Emails.send(params)
        print(f"Resend email dispatched successfully: {response}")
        return True
    except Exception as e:
        print(f"Failed to dispatch email via Resend: {e}")
        return False
