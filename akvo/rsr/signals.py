# -*- coding: utf-8 -*-

# Akvo RSR is covered by the GNU Affero General Public License.
# See more details in the license.txt file located at the root folder of the Akvo RSR module. 
# For additional details on the GNU license please see < http://www.gnu.org/licenses/agpl.html >.

import os
from datetime import datetime

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import get_model, ImageField

from sorl.thumbnail.fields import ImageWithThumbnailsField

from utils import setup_logging

logger = setup_logging('rsr.signals')


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
                if img and isinstance(img, InMemoryUploadedFile):
                    img.name = "%s_%s_%s_%s%s" % (
                        opts.object_name,
                        instance.pk or '',
                        f.name,
                        datetime.now().strftime("%Y-%m-%d_%H.%M.%S"),
                        os.path.splitext(img.name)[1],
                    )

def create_paypal_gateway(sender, **kwargs):
    """Called when a new project is saved so an associated PayPal gateway
    for the object is created
    """
    if kwargs.get('created', False):
        new_project = kwargs['instance']
        gateways = get_model('rsr', 'paypalgateway').objects
        default_gateway = gateways.get(pk=1)
        ppgs = get_model('rsr', 'paypalgatewayselector').objects
        ppgs.create(gateway=default_gateway, project=new_project)

def handle_incoming_sms(sender, **kwargs):
    """
    called when an sms callback is made
    we need to figureout what to do with the SMS depending on the WorkflowActivity
    associated with it (through the sender's phone number)
    """
    logger.debug("Entering: handle_incoming_sms()")
    if kwargs.get('created', False):
        new_sms = kwargs['instance']
        try:
            profile = get_model('rsr', 'UserProfile').objects.process_sms(new_sms)
        except Exception, e:
            logger.debug("handle_incoming_sms() exception: %s" % e.message)
    logger.debug("Exiting: handle_incoming_sms()")


def handle_sms_workflow(sender, **kwargs):
    up = kwargs['instance'] # we're getting a UserProfile to work with
    #u.objects.make_random_password(6).lower()
    if up.workflow_activity:
        pass # for now...here we should reset the wf for phone registration
    else:
        if up.phone_number:
            wa = up.create_sms_update_workflow()
