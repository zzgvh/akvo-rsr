# -*- encoding: utf-8 -*-

# Akvo RSR is covered by the GNU Affero General Public License.
# See more details in the license.txt file located at the root folder of the Akvo RSR module. 
# For additional details on the GNU license please see < http://www.gnu.org/licenses/agpl.html >.

# The log app is based on http://blog.stiod.com/2009/11/03/python-logging-em-django/

import logging
import datetime
from akvo.log.models import Log
 
class DjangoHandler(logging.Handler):
    '''Performs the handling of the log and inserts in the database'''
    def emit(self, record):
        log = Log()
        log.level = record.levelno
        log.file = record.pathname
        log.lineno = record.lineno
        log.message = record.msg
        # TODO: Use record.created
        log.date = datetime.datetime.now()
        log.save()

