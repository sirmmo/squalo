from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'squalo_core.views.index'),

    url(r'^add$', 'squalo_core.views.add_database'),
    url(r'^update/(?P<user>(\d|\w)+)/(?P<db>(\s|\w)+)/$', 'squalo_core.views.update'),
    url(r'^delete/(?P<user>(\d|\w)+)/(?P<db>(\s|\w)+)/$', 'squalo_core.views.delete'),

    url(r'^data/(?P<user>(\d|\w)+)$', 'squalo_core.views.user'),
    url(r'^data/(?P<user>(\d|\w)+)/(?P<db>(\s|\w)+)$', 'squalo_core.views.database'),
    url(r'^data/(?P<user>(\d|\w)+)/(?P<db>(\s|\w)+)/apidoc$', 'squalo_core.views.apidoc'),
    url(r'^data/(?P<user>(\d|\w)+)/(?P<db>(\s|\w)+)/(?P<model>\w+)$', 'squalo_core.views.model'),
    url(r'^data/(?P<user>(\d|\w)+)/(?P<db>(\s|\w)+)/(?P<model>\w+)/toggle$', 'squalo_core.views.model'),
    
    url(r'^api/(?P<user>(\d|\w)+)$', 'squalo_core.views.user_api'),
    url(r'^api/(?P<user>(\d|\w)+)/(?P<db>\s|\w+)$', 'squalo_core.views.database_api'),
    url(r'^api/(?P<user>(\d|\w)+)/(?P<db>\s|\w+)/(?P<model>\w+)$', 'squalo_core.views.query'),
    url(r'^api/(?P<user>(\d|\w)+)/(?P<db>\s|\w+)/(?P<model>\w+)\.schema$', 'squalo_core.views.schema_api'),
    
    
    url(r'^accounts/profile', 'squalo_core.views.profile'),
    url(r'^logout', 'squalo_core.views.logout'),

    url(r'^admin/', include(admin.site.urls)),
    url('', include('social.apps.django_app.urls', namespace='social')),
    #url(r"^payments/", include("payments.urls")),

)
