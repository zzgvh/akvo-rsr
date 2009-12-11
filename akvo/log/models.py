# -*- coding: utf-8 -*-

# Akvo RSR is covered by the GNU Affero General Public License.
# See more details in the license.txt file located at the root folder of the Akvo RSR module. 
# For additional details on the GNU license please see < http://www.gnu.org/licenses/agpl.html >.

# The log app is based on http://blog.stiod.com/2009/11/03/python-logging-em-django/

from django.db import models
from django.contrib import admin
import logging
 
class Log(models.Model):
    level = models.IntegerField(db_index=True)
    file = models.CharField(max_length=512, db_index=True)
    lineno = models.IntegerField()
    date = models.DateTimeField(db_index=True)
    message = models.TextField()
 
    def _get_level_name(self):
        return logging.getLevelName(self.level)
    levelName = property(fget=_get_level_name)
 
    def _get_message_summary(self):
        if len(self.message) > 100:
            return '%s...'%(self.message[:100])
        else:
            return self.message
    messageSummary = property(fget=_get_message_summary)
 
    def _get_file_summary(self):
        if len(self.file) > 30:
            return '...%s'%(self.file[-30:])
        return self.file
    fileSummary = property(fget=_get_file_summary)


class LogAdmin(admin.ModelAdmin):
   date_hierarchy = 'date'
   list_display = ('level', 'levelName', 'date', 'messageSummary', 'fileSummary', 'lineno')
   list_filter = ('level',)
   search_fields = ('message', 'file')
 
admin.site.register(Log, LogAdmin)
 