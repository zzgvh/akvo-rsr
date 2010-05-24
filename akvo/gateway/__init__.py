# -*- coding: utf-8 -*-

# Akvo RSR is covered by the GNU Affero General Public License.
# See more details in the license.txt file located at the root folder of the Akvo RSR module. 
# For additional details on the GNU license please see < http://www.gnu.org/licenses/agpl.html >.

import logging

from akvo.log.handler import DjangoHandler, setup_logging
from utils import package_name

pn = package_name(__file__)

#django_handler = DjangoHandler()
#logging.getLogger(pn).addHandler(DjangoHandler())

logger = setup_logging('akvo.gateway')
