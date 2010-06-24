#!/usr/bin/env python

# Akvo RSR is covered by the GNU Affero General Public License.
# See more details in the license.txt file located at the root folder of the Akvo RSR module. 
# For additional details on the GNU license please see < http://www.gnu.org/licenses/agpl.html >.

import os, sys

from ci_cleanup import *
from ci_environment import *


if len(sys.argv) <= 1:
    print 'Usage: ci_wrapper <virtualenv_path>'
    sys.exit(1)

os.chdir(os.path.realpath(os.path.dirname(__file__)))
os.system("bash ../testing/run_django_tests %s ci_mode" % (sys.argv[1]))
remove_project_links_to_prevent_subsequent_build_failure()

setup_acceptance_test_environment()
os.system("bash ../testing/run_acceptance_tests")
