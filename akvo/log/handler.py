# -*- encoding: utf-8 -*-

# Akvo RSR is covered by the GNU Affero General Public License.
# See more details in the license.txt file located at the root folder of the Akvo RSR module. 
# For additional details on the GNU license please see < http://www.gnu.org/licenses/agpl.html >.

# The log app is based on http://blog.stiod.com/2009/11/03/python-logging-em-django/

import logging
import datetime
from akvo.log.  models import Log

# TODO: fix duplicates

def setup_logging(logger_name='', log_level=logging.DEBUG):    
    logger = logging.getLogger(logger_name)

    if not hasattr(logger, "set_up_done"):
        logger.set_up_done = False
        #print "set_up_done set to False for logger %s" % logger_name

    if logger.set_up_done:
        #print "exiting without adding handler for logger %s" % logger_name
        return logger
    
    logger.addHandler(DjangoHandler())
    logger.setLevel(log_level)
    
    #print "set_up_done: " + str(logger.set_up_done)

    logger.set_up_done=True

    return logger

 
class DjangoHandler(logging.Handler):
    '''Performs the handling of the log and inserts in the database'''
    def emit(self, record):
        log = Log()
        log.level = record.levelno
        log.file = record.pathname
        log.name = record.name
        log.lineno = record.lineno
        log.message = record.msg
        # TODO: Use record.created
        log.date = datetime.datetime.now()
        log.save()

