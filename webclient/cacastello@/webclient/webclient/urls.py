from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf import settings
admin.autodiscover()

js_info_dict = {
    'packages': ('stacksync')
}

urlpatterns = patterns('',

    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^$', 'stacksync.views.index'),
    url(r'^index/(?P<file_id>.+)$', 'stacksync.views.index'),
    url(r'^delete/(?P<file_id>.+)$', 'stacksync.views.delete'),
    url(r'^download/(?P<file_id>.+)$', 'stacksync.views.download_file'),
    url(r'^newfolder/(?P<folder_name>.+)$', 'stacksync.views.new_folder'),
    url(r'^rename/(?P<ids>.+)/(?P<name>.+)/(?P<parent_id>.+)$', 'stacksync.views.rename'),
    url(r'^share/(?P<folder_id>.+)$', 'stacksync.views.share_folder'),
    url(r'^members/(?P<folder_id>.+)$', 'stacksync.views.get_members_of_folder'),
    url(r'^media/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.MEDIA_ROOT,}),
    url(r'^contact/$','stacksync.views.contact'),
    url(r'^thanks/$','stacksync.views.thanks'),
    url(r'^log_in/$','stacksync.views.log_in'),
    url(r'^forgotten/$','stacksync.views.forgotten'),
    url(r'^log_out/$', 'stacksync.views.log_out'),
    url(r'^pdf/(?P<file_id>.+)$', 'stacksync.views.pdf'),
    url(r'^img/(?P<file_id>.+)$', 'stacksync.views.img'),
    url(r'^move/(?P<file_id>.+)/(?P<file_name>.+)/(?P<parent_id>.+)$', 'stacksync.views.popup_move'),
    url(r'^move_element/(?P<element_id>.+)/(?P<element_name>.+)/(?P<parent_id>.+)$', 'stacksync.views.move_element'),
    url(r'^upload/$', 'stacksync.views.upload_file'),
    url(r'^jsi8n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    url(r'^restorepassword/(?P<user>.+)$','stacksync.keystone.restorepassword'),
    url(r'^encriptacion/$', 'stacksync.views.encriptacion'),
    url(r'^owncloud/$', 'stacksync.views.owncloud'),
    url(r'^pathlist/$', 'stacksync.views.pathlist'),
)