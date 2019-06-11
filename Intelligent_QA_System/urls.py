from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'Intelligent_QA_System.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('user.urls', namespace='user')),
    url(r'^manager/', include('manager.urls', namespace='manager')),
]
