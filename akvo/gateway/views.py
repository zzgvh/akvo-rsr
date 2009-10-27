# -*- coding: utf-8 -*-

# Akvo RSR is covered by the GNU Affero General Public License.
# See more details in the license.txt file located at the root folder of the Akvo RSR module. 
# For additional details on the GNU license please see < http://www.gnu.org/licenses/agpl.html >.

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect

from models import Gateway, MoSms
from utils import setup_logging

logger = setup_logging('gateway.views')

def receive_sms(request, gw_name):
    '''
    Handle a callback from a mobile message gateway
    '''
    #from dbgp.client import brk
    #brk(host="localhost", port=9000)            

    # see if message already has been recieved for some reason, if so ignore
    logger.debug("Entering: receive_sms()")
    try:
        gateway = Gateway.objects.get(name__iexact=gw_name)
        logger.debug("Found a gateway: %s" % gw_name)
    except:
        # general bork...bail out
        logger.exception("Exception trying to create a gateway instance. Locals:\n %s\n\n" % locals())
        return HttpResponse("OK") #return OK under all conditions
    sms, created = MoSms.new_sms(request, gateway)
    logger.debug("Exiting: receive_sms()")
    return HttpResponse("OK") #return OK under all conditions