import os
import boto3
import flask_mail
import flask_mail_sendgrid
from abc import ABC, abstractmethod
from .content import mail_content


class Mailer(ABC):

    @abstractmethod
    def init_app(self, app):
        pass

    @abstractmethod
    def send(self, data=None):
        pass


class SendGridMailer(Mailer):

    def __init__(self):
        self.client = flask_mail_sendgrid.MailSendGrid()

    def init_app(self, app):
        self.client.init_app(app)

    def send(self, data=None):

        if not self.client:
            raise ValueError("Mailing client error.")

        if not isinstance(data, dict):
            raise ValueError("Data must be of type dict")

        recipient = data.get("email")
        if not recipient:
            raise ValueError("Recipient's email not provided")

        del data["email"]
        _content = mail_content(**data)

        message = flask_mail.Message(_content.get("subject"),
                                     recipients=[recipient])
        message.html = _content.get("body")

        self.client.send(message)
