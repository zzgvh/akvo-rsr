# -*- coding: utf-8 -*-

# Akvo RSR is covered by the GNU Affero General Public License.
# See more details in the license.txt file located at the root folder of the Akvo RSR module. 
# For additional details on the GNU license please see < http://www.gnu.org/licenses/agpl.html >.

import os
from datetime import datetime

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import get_model, ImageField

from sorl.thumbnail.fields import ImageWithThumbnailsField

from akvo.rsr import logger
from utils import send_donation_confirmation_emails, who_am_i

def create_publishing_status(sender, **kwargs):
    """
    called when a new project is saved so an associated published record for the
    project is created
    """
    if kwargs.get('created', False):
        new_project = kwargs['instance']
        ps = get_model('rsr', 'publishingstatus')(status='unpublished')
        ps.project = new_project
        ps.save()
        
def create_organisation_account(sender, **kwargs):
    """
    called when a new organisation is saved so an associated org account is
    created with the "free" level of access to widgets
    """
    if kwargs.get('created', False):
        new_org = kwargs['instance']
        OrganisationAccount = get_model('rsr', 'OrganisationAccount')
        try:
            #this should never work
            acc = OrganisationAccount.objects.get(organisation=new_org)
        except:
            #and when it doesn't we do this
            new_acc = OrganisationAccount(organisation=new_org, account_level='free')
            new_acc.save()

def change_name_of_file_on_create(sender, **kwargs):
    """
    call to create a filename when creating a new model instance with the pattern
    ModelName_instance.pk_FieldName_YYYY-MM-DD_HH.MM.SS.ext
    Since we cannot do this until the instance of the model has been saved
    we do it as a post_save signal callback
    """
    if kwargs['created']:
        instance = kwargs['instance']
        opts = instance._meta
        for f in opts.fields:
            # extend this list of fields if needed to catch other uploads
            if isinstance(f, (ImageField, ImageWithThumbnailsField)):
                # the actual image sits directly on the instance of the model
                img = getattr(instance, f.name)
                if img:
                    img_name = "%s_%s_%s_%s%s" % (
                        opts.object_name,
                        instance.pk or '',
                        f.name,
                        datetime.now().strftime("%Y-%m-%d_%H.%M.%S"),
                        os.path.splitext(img.name)[1],
                    )
                    img.save(img_name, img)


def change_name_of_file_on_change(sender, **kwargs):
    """
    call to create a filename when saving the changes of a model with the pattern
    ModelName_instance.pk_FieldName_YYYY-MM-DD_HH.MM.SS.ext
    this is done before saving the model
    """
    if not kwargs.get('created', False):
        instance = kwargs['instance']
        opts = instance._meta
        for f in opts.fields:
            # extend this list of fields if needed to catch other uploads
            if isinstance(f, (ImageField, ImageWithThumbnailsField)):
                img = getattr(instance, f.name)
                #if a new image is uploaded it resides in a InMemoryUploadedFile
                if img:
                    try:
                        if isinstance(img.file, InMemoryUploadedFile):
                            img.name = "%s_%s_%s_%s%s" % (
                                opts.object_name,
                                instance.pk or '',
                                f.name,
                                datetime.now().strftime("%Y-%m-%d_%H.%M.%S"),
                                os.path.splitext(img.name)[1],
                            )
                    except:
                        pass


def create_payment_gateway_selector(instance, created, **kwargs):
    """Associates a newly created project with the default PayPal
    and Mollie payment gateways
    """
    if created:
        project = instance
        gateway_selector = get_model('rsr', 'paymentgatewayselector').objects
        gateway_selector.create(project=project)


def donation_completed(instance, created, **kwargs):
    invoice = instance
    if not created and invoice.status == 3:
        send_donation_confirmation_emails(invoice.id)


def handle_incoming_sms(sender, **kwargs):
    """
    called through post_save.connect(handle_incoming_sms, sender=MoSms)
    """
    logger.debug("Entering: %s()" % who_am_i())
    if kwargs.get('created', False):
        new_sms = kwargs['instance']
        try:
            profile = get_model('rsr', 'UserProfile').objects.process_sms(new_sms)
        except Exception, e:
            logger.exception('%s Locals:\n %s\n\n' % (e.message, locals(), ))
    logger.debug("Exiting: %s()" % who_am_i())


def cleanup_reporters(profile, user):
    if not profile.validation == profile.VALIDATED:
        get_model('rsr', 'smsreporter').objects.filter(userprofile=profile).delete()


from django.contrib.admin.models import ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType

def act_on_log_entry(sender, **kwargs):
    """
    catch the LogEntry post_save to grab newly added Project instances and create
    a workflow for it
    we do this at this time to be able to work with a fully populated Project
    instance with all inline forms processed and their respective objects created
    """
    CRITERIA = [
        {'app': 'rsr', 'model': 'userprofile', 'action': CHANGE, 'call': cleanup_reporters}
    ]
    if kwargs.get('created', False):
        log_entry = kwargs['instance']
        content_type = ContentType.objects.get(pk=log_entry.content_type_id)
        if (
            content_type.app_label == CRITERIA[0]['app']
            and content_type.model == CRITERIA[0]['model']
            and log_entry.action_flag == CRITERIA[0]['action']
        ):
            user = User.objects.get(pk=log_entry.user_id)
            object = content_type.get_object_for_this_type(pk=log_entry.object_id)
            CRITERIA[0]['call'](object, user)