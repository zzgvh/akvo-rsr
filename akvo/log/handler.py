# -*- encoding: utf-8 -*-

# Akvo RSR is covered by the GNU Affero General Public License.
# See more details in the license.txt file located at the root folder of the Akvo RSR module. 
# For additional details on the GNU license please see < http://www.gnu.org/licenses/agpl.html >.

# The log app is based on http://blog.stiod.com/2009/11/03/python-logging-em-django/

import logging
import datetime
from akvo.log.models import Log

if not hasattr(logging, "set_up_done"):
    logging.set_up_done = False

def setup_logging(logger_name='', log_level=logging.DEBUG):    
    logger = logging.getLogger(logger_name)

    if logging.set_up_done:
        return logger
    
    logger.addHandler(DjangoHandler())
    logger.setLevel(log_level)

    logging.set_up_done=True

    return logger

class Unique(logging.Filter):
    """
    From: http://code.activestate.com/recipes/412552-using-the-logging-module/
    
    Messages are allowed through just once.
    The 'message' includes substitutions, but is not formatted by the 
    handler. If it were, then practically all messages would be unique!
    """
    def __init__(self, name=""):
        logging.Filter.__init__(self, name)
        self.reset()
    def reset(self):
        """Act as if nothing has happened."""
        self.__logged = {}
    def filter(self, rec):
        """logging.Filter.filter performs an extra filter on the name."""
        return logging.Filter.filter(self, rec) and self.__is_first_time(rec)
    def __is_first_time(self, rec):
        """Emit a message only once."""
        msg = rec.msg %(rec.args)
        if msg in self.__logged:
            self.__logged[msg] += 1
            return False
        else:
            self.__logged[msg] = 1
            return True
 
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

