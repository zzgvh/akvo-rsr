# Akvo RSR is covered by the GNU Affero General Public License.
# See more details in the license.txt file located at the root folder of the Akvo RSR module. 
# For additional details on the GNU license please see < http://www.gnu.org/licenses/agpl.html >.


from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.contrib.auth import views as auth_views
from django.views.generic.simple import direct_to_template

from akvo.rsr.feeds import ProjectUpdates, AllProjectUpdates
from akvo.rsr.models import create_rsr_profile
from akvo.rsr.forms import RSR_PasswordResetForm, RSR_SetPasswordForm

# The next two lines enable the admin and load each admin.py file:
from django.contrib import admin
admin.autodiscover()

feeds = {
    'updates': ProjectUpdates,
    'all-updates': AllProjectUpdates,
}

urlpatterns = patterns('',
    #(r'^rsr/', include('akvo.rsr.urls')),

    # Payment engines
    url(r'^rsr/mollie/report/$', 'akvo.rsr.views.mollie_report', name='mollie_report'),
    url(r'^rsr/invoice/(?P<invoice_id>\d+)/(?P<action>\w+)/$', 'akvo.rsr.views.void_invoice', name='void_invoice'),
    url(r'^rsr/project/(?P<project_id>\d+)/donate/(?P<engine>\w+)/$',
        'akvo.rsr.views.donate', name='complete_donation'),
    url(r'^rsr/project/(?P<project_id>\d+)/donate/$', 'akvo.rsr.views.setup_donation', name='project_donate'),
    url(r'^rsr/donate/ideal/thanks/$', 'akvo.rsr.views.mollie_thanks', name='mollie_thanks'),
    url(r'^rsr/donate/paypal/thanks/$', 'akvo.rsr.views.paypal_thanks', name='paypal_thanks'), 
    url(r'^rsr/donate/500/$', direct_to_template, {'template': 'rsr/donate_500.html'}, name='donate_500'),
    url(r'^rsr/ipn/$', 'paypal.standard.ipn.views.ipn', name='paypal_ipn'),

    url(r'^$', 'akvo.rsr.views.index', name='index'),    
    (r'^rsr/$', 'akvo.rsr.views.oldindex', ),

    (r'^rsr/admin/(.*)', admin.site.root),
    #(r'^rsr/admin/', include('django.contrib.admin.urls')),
    
    url(r'^rsr/projects/$',
        'akvo.rsr.views.projectlist',
        name='project_list'),
    (r'^rsr/projects/(?P<org_id>\d+)/$', 'akvo.rsr.views.filteredprojectlist', ),
    #(r'^rsr/projects/all/$', 'akvo.rsr.views.projectlist', ),

    url(r'^rsr/project/(?P<project_id>\d+)/$',
        'akvo.rsr.views.projectmain', 
        name='project_main'),
    (r'^rsr/project/(?P<project_id>\d+)/update$', 'akvo.rsr.views.updateform', ),
    #(r'^rsr/project/(?P<project_id>\d+)/geo_update$', 'akvo.rsr.views.geo_updateform', ),
    (r'^rsr/geo_update/$', 'akvo.rsr.views.geo_updateform', ),
    (r'^rsr/project/(?P<project_id>\d+)/comment$', 'akvo.rsr.views.commentform', ),
    url(r'^rsr/project/(?P<project_id>\d+)/updates$', 'akvo.rsr.views.projectupdates', name='project_updates'),
    (r'^rsr/project/(?P<project_id>\d+)/comments$', 'akvo.rsr.views.projectcomments', ),
    (r'^rsr/project/(?P<project_id>\d+)/details$', 'akvo.rsr.views.projectdetails', ),
    (r'^rsr/project/(?P<project_id>\d+)/funding$', 'akvo.rsr.views.projectfunding', ),
    (r'^rsr/project/(?P<project_id>\d+)/get-a-widget$', 'akvo.rsr.views.getwidget', ),

    
    url(r'^rsr/fundingbar/$', 'akvo.rsr.views.fundingbarimg', name='fundingbar'),    

    #(r'^rsr/project/(?P<project_id>\d+)/ajax_tab_goals$', 'akvo.rsr.views.ajax_tab_goals', ),
    #(r'^rsr/project/(?P<project_id>\d+)/ajax_tab_sustainability$', 'akvo.rsr.views.ajax_tab_sustainability', ),
    #(r'^rsr/project/(?P<project_id>\d+)/ajax_tab_context$', 'akvo.rsr.views.ajax_tab_context', ),
    #(r'^rsr/projects/(?P<order_by>[_a-zA-Z]*)/$', 'akvo.rsr.views.projectlist', ),

    (r'^rsr/flashgallery.xml$', 'akvo.rsr.views.flashgallery', ),
    
    url(r'^rsr/organisation/(?P<org_id>\d+)/$', 'akvo.rsr.views.orgdetail', name="org_detail"),
    
    url(r'^rsr/organisations/$', 'akvo.rsr.views.orglist', name='rsr_org_list'),
    url(r'^rsr/organisations/(?P<org_type>[_a-zA-Z]+)/$', 'akvo.rsr.views.orglist', name='rsr_org_list_filtered'),
    url(r'^rsr/partners-widget/$', 'akvo.rsr.views.partners_widget', name='rsr_partners_widget'),


    (r'^rsr/setlowbandwidth/$', 'akvo.rsr.views.set_low_bandwidth', ),
    (r'^rsr/sethighbandwidth/$', 'akvo.rsr.views.set_high_bandwidth', ),
    (r'^rsr/settestcookie/$', 'akvo.rsr.views.set_test_cookie', ),

    #(r'^rsr/signin/$', 'akvo.rsr.views.login', {'template_name': 'rsr/sign_in.html'}),
    url(r'^rsr/signin/$',
                           'akvo.rsr.views.login',
                           {'template_name': 'rsr/sign_in.html'},
                           name='signin'),
    #(r'^rsr/signin/$', 'auth_views.login', {'template_name': 'rsr/sign_in.html'}),
    (r'^rsr/signout/$', 'akvo.rsr.views.signout', ),
    
    (r'^rsr/accounts/register1/$', 'akvo.rsr.views.register1', ),
    (r'^rsr/accounts/register2/$', 'akvo.rsr.views.register2', ),
    url(r'^rsr/accounts/activate/(?P<activation_key>\w+)/$', 'akvo.rsr.views.activate', name='registration_activate'),
    (r'^rsr/accounts/update/$', 'akvo.rsr.views.update_user_profile', ),
    (r'^rsr/accounts/password/change/$', 'akvo.rsr.views.password_change', ),
    url(r'^rsr/accounts/password/reset/$',
        auth_views.password_reset,
        {'password_reset_form': RSR_PasswordResetForm,
            'post_reset_redirect': '/rsr/accounts/password/reset/done/'},
        name='rsr_password_reset'
    ),
    url(r'^rsr/accounts/password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        {'set_password_form': RSR_SetPasswordForm},
        name='auth_password_reset_confirm'),
    (r'^rsr/accounts/update/complete/$', direct_to_template, {'template': 'registration/update_complete.html'} ),
    (r'^rsr/accounts/', include('registration.urls')),
	
	# Widgets
	url(r'^rsr/widget/one-from-organisation/(?P<org_id>\d+)/$', 'akvo.rsr.views.select_project_widget', name='select_project_widget', ),
	url(r'^rsr/widget/(?P<template>[\w-]+)/project/(?P<project_id>\d+)/$','akvo.rsr.views.project_widget', name='project_widget', ),
	url(r'^rsr/widget/(?P<template>[\w-]+)/$','akvo.rsr.views.project_widget', name='project_widget_default', ),
	
	#url(r'^rsr/widget/list-from-organisation/(?P<org_id>)\d+)$', 'akvo.rsr.views.select_list_widget', name='select_list_widget', ),
	#url(r'^rsr/widget/organisation/(?P<org_id>\d+)/(?P<template>[\w-]+)/$', 'akvo.rsr.views.project_list_widget', name='project_list_widget', ),
	url(r'^rsr/widget/(?P<template>[\w-]+)/all/$', 'akvo.rsr.views.project_list_widget', name='project_list_widget', ),
	url(r'^rsr/widget/(?P<template>[\w-]+)/organisation/(?P<org_id>\d+)/$', 'akvo.rsr.views.project_list_widget', name='project_list_widget', ),
	
    (r'^rsr/error/access_denied/$', direct_to_template, {'template': 'rsr/error_access_denied.html'}),
    
    url(r'^rsr/rss/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}, name='akvo_feeds'),

    (r'^rsr/mosms/$', 'akvo.rsr.views.sms_update', ),    
    (r'^rsr/momms/$', 'akvo.rsr.views.mms_update', ),
    
    #url(r'^rsr/liveearth/$', 'akvo.rsr.views.liveearth', name='live_earth_landing_page',),    
    
    #feedjack
    #(r'', include('feedjack.urls')),
    
    #template dev urls
    (r'^rsr/dev/(?P<template_name>[_a-zA-Z0-9]+)/$', 'akvo.rsr.views.templatedev', ),
    #(r'^rsr/dev/project_main/$', 'django.views.generic.simple.direct_to_template', {'template': 'dev/project_main.html'}),

    # serving media in the dev server environment TODO: set up real media serving
    #(r'^rsr/media/(?P<path>.*)$', 
    #    'django.views.static.serve', 
    #    {'document_root': '/var/dev/akvo/mediaroot/', 'show_indexes': True}),
)


from django.conf import settings
if settings.LIVE_EARTH_ENABLED:
    urlpatterns += patterns('',
        url(r'^rsr/liveearth/$', 'akvo.rsr.views.liveearth', name='live_earth_landing_page',),    
    )

if settings.WALKING_FOR_WATER_ENABLED:
    urlpatterns += patterns('',
        url(r'^rsr/walking-for-water/$', 'akvo.rsr.views.walking_for_water', name='wfw_landing_page',),
    )
    
handler500 = 'akvo.rsr.views.server_error'
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^500/$', 'akvo.rsr.views.server_error'),
    )

if settings.DEBUG:
    urlpatterns += patterns('',
		(r'^rsr/media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rsr/rosetta/', include('rosetta.urls')),
    )
