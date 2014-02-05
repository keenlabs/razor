import logging
import sendgrid
from sendgrid.exceptions import SGServiceException
from sendgrid.message import Message

__author__ = 'dkador'


class Emailer(object):
    # set by lib
    username = ""
    password = ""

    @classmethod
    def send_email(cls, addr_from="alerts+razor@keen.io", addr_to="", subject="", addr_cc=None,
                   addr_bcc=None, text=None, html=None, categories=None, from_name=None):
        """

        Sends an email with the given parameters.

        :param addr_from: string, the from address
        :param addr_to: string, the to address
        :param subject: string, the subject
        :param addr_cc: list, a list of strings of addresses
        :param addr_bcc: list, a list of strings of addresses
        :param text: string, the email body to send for text-only recipients
        :param html: string, the email body, html-formatted,
        for html-capable recipients.
        :param categories: list, a list of strings of the sendgrid categories of the email

        If text is provided but html is not then we'll replace all new-lines
        with <br> tags. Hooray.

        """

        if text and not html:
            html = text.replace("\n", "<br/>")
            html = html.replace("\\n", "<br/>")

        sendgrid_client = sendgrid.Sendgrid(cls.username, cls.password)
        message = Message(addr_from, subject, text=text, html=html)
        message.to = addr_to
        message.cc = addr_cc
        message.bcc = addr_bcc
        message.from_name = from_name
        if categories:
            for category in categories:
                message.add_category(category)
        try:
            sendgrid_client.web.send(message)
        except SGServiceException, e:
            logging.getLogger("emailer").error("Error when sending email: {}".format(e), "email_error")
            raise