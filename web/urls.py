from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'web.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'stacksync.views.index'),
    url(r'^focus/(?P<file_id>.+)$', 'stacksync.views.index_focus'),
    url(r'^delete/(?P<file_id>.+)$', 'stacksync.views.delete_file'),
    url(r'^delete_folder/(?P<folder_id>.+)$', 'stacksync.views.delete_folder'),
    url(r'^download/(?P<file_id>.+)$', 'stacksync.views.download_file'),
    url(r'^newfolder/(?P<folder_name>.+)$', 'stacksync.views.new_folder'),
    url(r'^rename_folder/(?P<folder_id>.+)/(?P<folder_name>.+)$', 'stacksync.views.rename_folder'),
    url(r'^rename_file/(?P<file_id>.+)/(?P<file_name>.+)$', 'stacksync.views.rename_file'),
    url(r'^media/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.MEDIA_ROOT,}),
    url(r'^contact/$','stacksync.views.contact'),
    url(r'^thanks/$','stacksync.views.thanks'),
    url(r'^log_in/$','stacksync.views.log_in'),
    url(r'^log_out/$', 'stacksync.views.log_out'),
    url(r'^pdf/(?P<file_id>.+)$', 'stacksync.views.pdf'),
    url(r'^img/(?P<file_id>.+)$', 'stacksync.views.img'),
    url(r'^move/(?P<file_id>.+)$', 'stacksync.views.popup_move'),
)
