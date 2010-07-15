# -*- coding: utf-8 -*-
#!/usr/bin/env python

# utility functions for RSR


from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models import get_model
from django.core.mail import send_mail, EmailMessage
from django.core.urlresolvers import reverse
from django.template import loader, Context
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext, get_language, activate

from notification.models import (
    Notice, NoticeType, get_notification_language, should_send,
    LanguageStoreNotAvailable, get_formatted_messages
)

import inspect
import logging
import os


RSR_LIMITED_CHANGE          = u'rsr_limited_change'
GROUP_RSR_PARTNER_ADMINS    = u'RSR partner admins'#can edit organisation info
GROUP_RSR_PARTNER_EDITORS   = u'RSR partner editors' #can edit an org's projects
GROUP_RSR_EDITORS           = u'RSR editors'
GROUP_RSR_USERS             = u'RSR users'

ROLE_SMS_UPDATER            = u'SMS Updater'

PAYPAL_INVOICE_STATUS_PENDING   = 1
PAYPAL_INVOICE_STATUS_VOID      = 2
PAYPAL_INVOICE_STATUS_COMPLETE  = 3
PAYPAL_INVOICE_STATUS_STALE     = 4

def package_name(file=__file__):
    '''
    return the packae name of the current file
    '''
    return str(os.path.split(os.path.realpath(file))[0].split(os.sep)[-1])

from log.handler import setup_logging
logger = setup_logging(package_name())

def who_am_i():
    "introspecting function returning the name of the function where who_am_i is called"
    return inspect.stack()[1][3]

def who_is_parent():
    """
    introspecting function returning the name of the caller of the function
    where who_is_parent is called
    """
    return inspect.stack()[2][3]

def groups_from_user(user):
    """
    Return a list with the groups the current user belongs to.
    """
    return [group.name for group in user.groups.all()]

        
#Modeled on Options method get_change_permission in django/db/models/options.py
def get_rsr_limited_change_permission(obj):
    return '%s_%s' % (RSR_LIMITED_CHANGE, obj.object_name.lower())


def rsr_image_path(instance, file_name, path_template='db/project/%s/%s'):
    """
    Use to set ImageField upload_to attribute.
    Create path for image storing. When a new object instance is created we save
    in MEDIA_ROOT/db/project/temp/img_name.ext first and then immediately call
    save on the ImageFieldFile when the object instance has been saved to the db,
    so the path changes to MEDIA_ROOT/db/project/org.pk/img_name.ext.
    Modify path by supplying a path_tempate string
    """
    if instance.pk:
        return path_template % (str(instance.pk), file_name)
    else:
        return path_template % ('temp', file_name)


def rsr_send_mail(to_list, subject='templates/email/test_subject.txt',
                  message='templates/email/test_message.txt', subject_context={}, msg_context={}):
    """
    Send template driven email.
        to_list is a list of email addresses
        subject and message are templates for use as email subject and message body
        subject_context and msg_context are dicts used when renedering the respective templates
    Site.objects.get_current() is added to both contexts as current_site
    """
    current_site = Site.objects.get_current()
    subject_context.update({'site': current_site})
    subject = loader.render_to_string(subject, subject_context)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    msg_context.update({'site': current_site})
    message = loader.render_to_string(message, msg_context)    
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, to_list)


def rsr_send_mail_to_users(users, subject='templates/email/test_subject.txt',
                  message='templates/email/test_message.txt', subject_context={}, msg_context={}):
    """
    Send mail to many users supllied through a queryset
    """
    to_list = [user.email for user in users if user.email]
    rsr_send_mail(to_list, subject, message, subject_context, msg_context)


def qs_column_sum(qs, col):
    "return sum of a queryset column"
    return sum(qs.values_list(col, flat=True))


def model_and_instance_based_filename(object_name, pk, field_name, img_name):
    """ Create a file name for an image based on the model name, the current object's pk,
    the field name of the model and the current date and time"""
    return "%s_%s_%s_%s%s" % (
        object_name,
        pk or '',
        field_name,
        datetime.now().strftime("%Y-%m-%d_%H.%M.%S"),
        splitext(img_name)[1],
    )

def send_donation_confirmation_emails(invoice_id):
    invoice = get_model('rsr', 'invoice').objects.get(pk=invoice_id)
    t = loader.get_template('rsr/donation_confirmation_email.html')
    c = Context({'invoice': invoice, 'domain_name': settings.DOMAIN_NAME})
    message_body = t.render(c)
    subject_field, from_field = _(u'Thank you from Akvo.org!'), settings.DEFAULT_FROM_EMAIL
    bcc_field = invoice.notification_email
    if invoice.user:
        to_field = invoice.user.email
    else:
        to_field = invoice.email
    msg = EmailMessage(subject_field, message_body, from_field, [to_field], [bcc_field])
    msg.content_subtype = "html"
    msg.send()

#if this gets updated, the create() method below needs to be as well...
NOTICE_MEDIA = (
    ("email", _("Email")),
    ("sms", _("SMS")),
)

# how spam-sensitive is the medium
NOTICE_MEDIA_DEFAULTS = {
    "email": 2,
    "sms": 2,
}

def send_now(users, label, extra_context=None, on_site=True, sender=None):
    """
    GvH: Modified version of notification.models.send_now
    
    Creates a new notice.

    This is intended to be how other apps create new notices.

    notification.send(user, 'friends_invite_sent', {
        'spam': 'eggs',
        'foo': 'bar',
    )
    
    You can pass in on_site=False to prevent the notice emitted from being
    displayed on the site.
    """
    logger.debug("Entering: %s()" % who_am_i())
    if extra_context is None:
        extra_context = {}
    
    notice_type = NoticeType.objects.get(label=label)

    protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
    current_site = Site.objects.get_current()
    
    notices_url = u"%s://%s%s" % (
        protocol,
        unicode(current_site),
        reverse("notification_notices"),
    )

    current_language = get_language()

    formats = (
        'short.txt',
        'full.txt',
        'sms.txt',
        'notice.html',
        'full.html',
    ) # TODO make formats configurable

    for user in users:
        recipients = []
        # get user language for user from language store defined in
        # NOTIFICATION_LANGUAGE_MODULE setting
        try:
            language = get_notification_language(user)
        except LanguageStoreNotAvailable:
            language = None

        if language is not None:
            # activate the user's language
            activate(language)

        # update context with user specific translations
        context = Context({
            "recipient": user,
            "sender": sender,
            "notice": ugettext(notice_type.display),
            "notices_url": notices_url,
            "current_site": current_site,
        })
        context.update(extra_context)

        # get prerendered format messages
        messages = get_formatted_messages(formats, label, context)

        # Strip newlines from subject
        subject = ''.join(render_to_string('notification/email_subject.txt', {
            'message': messages['short.txt'],
        }, context).splitlines())

        body = render_to_string('notification/email_body.txt', {
            'message': messages['full.txt'],
        }, context)

        notice = Notice.objects.create(recipient=user, message=messages['notice.html'],
            notice_type=notice_type, on_site=on_site, sender=sender)
        if user.is_active:
            if should_send(user, notice_type, "email") and user.email: # Email
                recipients.append(user.email)
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipients)
            if should_send(user, notice_type, "sms") and user.get_profile().phone_number: # SMS
                # strip newlines
                sms = ''.join(render_to_string('notification/email_subject.txt', {
                    'message': messages['sms.txt'],
                }, context).splitlines())
                #extra_context['gw_number'] holds a GatewayNumber object
                logger.info("Sending SMS notification of type %s to %s." % (notice_type, user, ))
                extra_context['gw_number'].send_sms(extra_context['phone_number'], sms)
                #print "sending sms from %s, to %s: %s" % (extra_context['gw_number'], extra_context['phone_number'], sms)

    # reset environment to original language
    activate(current_language)
    logger.debug("Exiting: %s()" % who_am_i())

# workflow helpers

from workflows.models import State
from workflows.utils import get_state

def state_equals(obj, state):
    if type(state) != type([]):
        state = [state] 
    return get_state(obj) in State.objects.filter(name__in=state)