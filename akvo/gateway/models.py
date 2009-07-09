# -*- coding: utf-8 -*-

# Akvo RSR is covered by the GNU Affero General Public License.
# See more details in the license.txt file located at the root folder of the Akvo RSR module. 
# For additional details on the GNU license please see < http://www.gnu.org/licenses/agpl.html >.

from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _

from datetime import datetime

class Gateway(models.Model):
    """

    """
    name        = models.SlugField(
        _(u'gateway name'), max_length=30,
        help_text='''
            The name is used in the call back to determine the gateway used.
            For example if the name is "42it" the callback path will be /gateway/42it/
        '''
    )
    host_name   = models.CharField(_(u'host name'), max_length=255)
    send_path   = models.CharField(_(u'send message path'), max_length=255)

    sender      = models.CharField(_(u'sender'),    max_length=30)
    receiver    = models.CharField(_(u'receiver'),  max_length=30)
    message     = models.CharField(_(u'message'),   max_length=30)
    timestamp   = models.CharField(_(u'timestamp'), max_length=30)
    msg_id      = models.CharField(_(u'msg_id'),    max_length=30)

    def __unicode__(self):
        return self.name

    def numbers(self):
        return '<br />'.join([gw_number.number for gw_number in self.gatewaynumber_set.all()])
    numbers.allow_tags = True

class GatewayNumber(models.Model):
    gateway = models.ForeignKey(Gateway)     
    number  = models.CharField(_(u'gateway number'), max_length=30)
    
    def __unicode__(self):
        return '%s: %s' % (self.gateway, self.number)

    
#class GatewayCallbackApiField(models.Model):
#    FIELD_CHOICES = (
#        ('sender', 'sender'),
#        ('receiver', 'receiver'),
#        ('message', 'message'),
#        ('timestamp', 'getaway timestamp'),
#        ('msg_id', 'gateway message id'),
#    )
#    gateway = models.ForeignKey(Gateway)     
#    name    = models.CharField(_(u'field name'), choices=FIELD_CHOICES, max_length=20)
#    value   = models.CharField(_(u'api field'), max_length=20)
#    
#    class Meta:
#        unique_together = ('gateway', 'name', 'value',)
        
#gateways = {
#    '42it': {
#        'name'      : '42it',
#        'host_name' : 'server1.msgtoolbox.com',
#        'send_path' : '/api/current/send/message.php? ',
#        'api_map'   : {
#            'sender'            : 'sender',
#            'receiver'          : 'to',
#            'message'           : 'text',
#            'getaway_timestamp' : 'delivered',
#            'gateway_id'        : 'incsmsid',
#        }
#    },
#    'clickatell': {
#        'name'      : 'Clickatell',
#        'host_name' : 'api.clickatell.com',
#        'send_path' : '/http/sendmsg',
#        'api_map'   : {
#            'sender'            : 'from',
#            'receiver'          : 'to',
#            'message'           : 'text',
#            'getaway_timestamp' : 'timestamp',
#            'gateway_id'        : 'moMsgId',
#        }
#    },
#    'smsglobal': {
#        'name'      : 'SMSGlobal',
#        'host_name' : 'www.smsglobal.com.au',
#        'send_path' : '/http-api.php',
#        'api_map'   : {
#            'sender'            : 'from',
#            'receiver'          : 'to',
#            'message'           : 'msg',
#            'getaway_timestamp' : 'date',
#            'gateway_id'        : 'userfield',
#        }
#    }
#}

class MoSms(models.Model):
    """
    Generic storage of an incoming sms
    Attributes:
        sender: sender's telephone number
        receiver: phone number the message was received at
        message: the actual sms text
        timestamp: many gateways include a time when the message arrived at the gateway
        msg_id: many gateways include an id for each message
        saved_at: time when the message is saved
    """
    
    sender      = models.CharField(max_length=30)
    receiver    = models.CharField(max_length=30)
    message     = models.TextField(blank=True) #degenerate, but possible...
    timestamp   = models.CharField(max_length=50, blank=True)
    msg_id      = models.CharField(max_length=100, blank=True)
    saved_at    = models.DateTimeField()

    @classmethod
    def new_sms(self, request, gateway):
        request.encoding = 'iso-8859-1' #TODO: some GWs allow this to be set I think
        try:
            # if we find an mms already, do nuthin...
            sms, created = MoSms.objects.get(msg_id=request.GET.get(gateway.msg_id)), False
        except:
            raw = {}
            # loop over all field names and do lookup of the callback api name of
            # the field to get the incoming value
            for f in MoSms._meta.fields:
                value = request.GET.get(getattr(gateway, f.name, ''), False)
                if value:
                    raw[f.name] = value
            raw['saved_at'] = datetime.now()
            sms, created = MoSms.objects.create(**raw), True
        return sms, created











