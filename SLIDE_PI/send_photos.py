#!/usr/bin/env python
# -*- coding: utf-8
"""
Waits for incomming mails, checks title, sends mail with attachment
"""

import os
import time
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from zipfile import ZipFile


USER = 'user@mail.server'
PASSWORD = 'MyTotallySecurePassword'
IMAPSERVER = 'mail.server-imap.url:port'  # :993 Std Value
SMTPSERVER = 'mail.server-smtp.url:port'  # :587 in my case


def check_mails():
    """checks for new mails, returns (isnewmails, messages)"""
    imapserver = imaplib.IMAP4_SSL(IMAPSERVER)
    imapserver.login(USER, PASSWORD)
    imapserver.select('Inbox', readonly=False)
    messagesids = imapserver.search(None, '(UNSEEN)')[1]
    isnewmails = messagesids[0]
    rawmessages = []
    if isnewmails:
        for msgid in messagesids[0].split(' '):
            rawmessages.append(imapserver.fetch(msgid, '(RFC822)')[1])
    imapserver.logout()
    return isnewmails, rawmessages


def get_sender_and_subject(rawmsg):
    """get the mail msgid, parse, return info"""
    msg = email.message_from_string(rawmsg[0][1])
    return msg['Return-Path'][1:-1], msg['Subject']


def is_four_digit_number(strnumber):
    """Checks if the number as string has four digits"""
    if len(strnumber) == 4:
        try:
            int(strnumber)
            return True
        except ValueError:
            return False
    else:
        return False


def is_number_available(strnumber):
    """Checks if .zip with that number is in 'kept_pics' in home folder"""
    path = os.path.join('/home', 'pi', 'kept_pics', strnumber + '.zip')
    return os.path.isfile(path)


def open_close_smtp_send_mail(reciever, mailcontent):
    """Opens Std SMTP server and sends 'mailcontent' to 'reciever'"""
    smtpserver = smtplib.SMTP(SMTPSERVER)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.login(USER, PASSWORD)
    smtpserver.sendmail(USER, reciever, mailcontent)
    smtpserver.close()


def send_photo_mail(reciever, zipnumber):
    """Sends mail with photos as .zip in attachment"""
    subject = u'Partykulär Photobooth Bilder %s' % zipnumber
    zipfile = ZipFile(os.path.join('/home', 'pi', 'kept_pics',
                                   zipnumber + '.zip'), 'r')
    pic1 = zipfile.open('pic1.jpg')
    pic2 = zipfile.open('pic2.jpg')
    pic3 = zipfile.open('pic3.jpg')
    pic4 = zipfile.open('pic4.jpg')
    pic5 = zipfile.open('assembly.jpg')
    text = u"""Hallo Partykulär Photobooth Nutzer!

Im Anhang deine/eure Bilder, viel Spaß damit.

LG Dein Partykulär Team (Steffen, Jürgen, Tobby, Günthi)"""
    mailtext = MIMEText(text, 'plain', _charset='utf-8')
    attachment1 = MIMEApplication(pic1.read(), _subtype='jpg')
    attachment1.add_header('Content-Disposition',
                           'attachment; filename=pic1.jpg')
    attachment2 = MIMEApplication(pic2.read(), _subtype='jpg')
    attachment2.add_header('Content-Disposition',
                           'attachment; filename=pic2.jpg')
    attachment3 = MIMEApplication(pic3.read(), _subtype='jpg')
    attachment3.add_header('Content-Disposition',
                           'attachment; filename=pic3.jpg')
    attachment4 = MIMEApplication(pic4.read(), _subtype='jpg')
    attachment4.add_header('Content-Disposition',
                           'attachment; filename=pic4.jpg')
    attachment5 = MIMEApplication(pic5.read(), _subtype='jpg')
    attachment5.add_header('Content-Disposition',
                           'attachment; filename=assembly.jpg')
    zipfile.close()
    mail = MIMEMultipart('mixed')
    mail.attach(mailtext)
    mail.attach(attachment1)
    mail.attach(attachment2)
    mail.attach(attachment3)
    mail.attach(attachment4)
    mail.attach(attachment5)
    mail['Subject'] = subject
    mail['From'] = USER
    mail['To'] = reciever
    mailcontent = mail.as_string('utf-8')
    open_close_smtp_send_mail(reciever, mailcontent)


def send_number_not_found_mail(reciever, strnumber):
    """Sends mail that the number is not present as pictures"""
    subject = u'Partykulär Photobooth Bilder %s' % strnumber
    text = u"""Hallo Partykulär Photobooth Nutzer!

Leider haben wir keine Bilder zu der entsprechenden Nummer gefunden.
Hast du dich vertippt? Wenn nicht, versuche es in ein paar Minuten
noch einmal. Wenn es dann immernoch nicht klappt, sprich einen von
uns an.

LG Dein Partykulär Team (Steffen, Jürgen, Tobby, Günthi)"""
    mailtext = MIMEText(text, 'plain', _charset='utf-8')
    mail = MIMEMultipart('mixed')
    mail.attach(mailtext)
    mail['Subject'] = subject
    mail['From'] = USER
    mail['To'] = reciever
    mailcontent = mail.as_string('utf-8')
    open_close_smtp_send_mail(reciever, mailcontent)


def send_incorrect_subject_mail(reciever, subjectstr):
    """Sends mail that subject is not parsable"""
    subject = u'Partykulär Photobooth Bilder: %s' % subjectstr
    text = u"""Hallo Partykulär Photobooth Nutzer!

Leider stimmt das Format deines Betreffs nicht, dieser muss aus
exakt vier Ziffern bestehen, und darf keine Anführungszeichen,
Leerzeichen oder anderen Text beinhalten. Sprich einen von uns an,
wenn du Probleme hast, deine Bilder zu bekommen.

LG Dein Partykulär Team (Steffen, Jürgen, Tobby, Günthi)"""
    mailtext = MIMEText(text, 'plain', _charset='utf-8')
    mail = MIMEMultipart('mixed')
    mail.attach(mailtext)
    mail['Subject'] = subject
    mail['From'] = USER
    mail['To'] = reciever
    mailcontent = mail.as_string('utf-8')
    open_close_smtp_send_mail(reciever, mailcontent)


def send_photos(msg):
    """Parse message, send photos if successfull, error mail if not"""
    sender, subject = get_sender_and_subject(msg)
    if is_four_digit_number(subject):
        if is_number_available(subject):
            send_photo_mail(sender, subject)
	    print 'send'
        else:
            send_number_not_found_mail(sender, subject)
	    print 'not found'
    else:
        send_incorrect_subject_mail(sender, subject)
        print 'wrong subject'


def main():
    """Open Mail server, check for mails, parse mails, send photos"""
    # import ipdb; ipdb.set_trace()
    while True:
	time.sleep(10)
        try:
            isnewmails, msgs = check_mails()
	    print 'pull'
            if isnewmails:
                for msg in msgs:
                    send_photos(msg)
                    time.sleep(2)
            time.sleep(10)
        except:
            time.sleep(300)

if __name__ == '__main__':
    main()
