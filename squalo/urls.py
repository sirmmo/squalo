from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'squalo_core.views.index', name='index'),

    url(r'^add$', 'squalo_core.views.add_database', name='user'),
    url(r'^update/(?P<user>\w+)/(?P<db>\w+)$', 'squalo_core.views.update', name='db'),

    url(r'^data/(?P<user>\w+)$', 'squalo_core.views.user', name='user'),
    url(r'^data/(?P<user>\w+)/(?P<db>(\s|\w)+)$', 'squalo_core.views.database', name='db'),
    url(r'^data/(?P<user>\w+)/(?P<db>(\s|\w)+)/(?P<model>\w+)$', 'squalo_core.views.model', name='model'),
    
    url(r'^api/(?P<user>\w+)$', 'squalo_core.views.user_api', name='user_api'),
    url(r'^api/(?P<user>\w+)/(?P<db>\s|\w+)$', 'squalo_core.views.database_api', name='db_api'),
    url(r'^api/(?P<user>\w+)/(?P<db>\s|\w+)/(?P<model>\w+)$', 'squalo_core.views.query', name='model_api'),
    
    url(r'^accounts/profile', 'squalo_core.views.profile'),
    url(r'^logout', 'squalo_core.views.logout'),

    url(r'^admin/', include(admin.site.urls)),
    url('', include('social.apps.django_app.urls', namespace='social'))
)
