import os
import sys
import smtplib as smtp


MAIL_smtp = 'smtp.example.ro'
MAIL_port = 25
MAIL_user = 'user@example.ro'
Mail_pass = 'thiIsMyPassword'
MAIL_from = 'FromEmail@example.ro'
MAIL_to = 'ToEmail@example.ro'
MAIL_message = """From: <TEST>
To: <{}>
MIME-Version: 1.0
Subject: This is a test email, do not reply

This is a test
""".format(MAIL_to)


def SendMailSMTP():
        ConnectSMTP = smtp.SMTP(MAIL_smtp, MAIL_port)
        ConnectSMTP.set_debuglevel(1)
        ConnectSMTP.login(MAIL_user, Mail_pass)
        ConnectSMTP.sendmail(MAIL_from, MAIL_to, MAIL_message)
        ConnectSMTP.quit()

SendMailSMTP()
