from flask_mail import Message
from flask import render_template, current_app
from extensions import mail

class EmailService:
    """"
    Centralized Email Service Layer
    All outgoing emails must go through this class.
    """

    @staticmethod
    def send_email(subject, recipients, template_name, **context):
        """
        Generic email sender.
        
        :param subject: Subject of email
        :param recipients: List of recipient email addresses
        :param template_name: HTML template file name (inside templates/emails/)
        :param context: Variables passes to template
        """
        try:   
            msg = Message(
                subject=subject,
                recipients=recipients
            )

        #Render Html template
            msg.html = render_template(f"emails/{template_name}", **context)

            mail.send(msg)  #call SMTP server to send email
            return True
        
        except Exception as e :
            current_app.logger.error(f"Email sending failed: {str(e)}")
            return False