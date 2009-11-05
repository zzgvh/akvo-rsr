from django.conf import settings
from django.db.models.signals import post_syncdb
from django.utils.translation import ugettext_noop as _
 
if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
 
    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type(
            "phone_added",
            _("Phone number added"),
            _("Your mobile phone has been added to your user profile")
        )
        notification.create_notice_type(
            "phone_confirmed",
            _("Phone confirmed"),
            _("Your mobile phone number has been confirmed for use in updating RSR projects")
        )
        notification.create_notice_type(
            "sms_updating_enabled",
            _("SMS updates enabled for project"),
            _("You can now send SMS-updates to an RSR project")
        )
        notification.create_notice_type(
            "sms_updating_cancelled",
            _("SMS updates cancelled"),
            _("SMS-updates to an RSR project has been cancelled")
        )
 
    post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"