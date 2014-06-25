from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'proyecto.views.home', name='home'),
    # url(r'^proyecto/', include('proyecto.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'stacksyncapp.views.index'),
    url(r'^focus/(?P<file_id>.+)$', 'stacksyncapp.views.index_focus'),
    url(r'^delete/(?P<file_id>.+)$', 'stacksyncapp.views.delete_file'),
    url(r'^download/(?P<file_id>.+)$', 'stacksyncapp.views.download_file'),
    url(r'^newfolder/(?P<folder_name>.+)$', 'stacksyncapp.views.new_folder'),
    url(r'^media/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.MEDIA_ROOT,}),
    url(r'^contact/$','stacksyncapp.views.contact'),
    url(r'^thanks/$','stacksyncapp.views.thanks'),
    url(r'^log_in/$','stacksyncapp.views.log_in'),
    url(r'^log_out/$', 'stacksyncapp.views.log_out'),
    url(r'^pdf/(?P<file_id>.+)$', 'stacksyncapp.views.pdf'),
    url(r'^img/(?P<file_id>.+)$', 'stacksyncapp.views.img'),
    url(r'^move/(?P<file_id>.+)$', 'stacksyncapp.views.popup_move'),

)
