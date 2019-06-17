# -*- coding: utf-8 -*-
# @File 	: urls.py
# @Author 	: jianhuChen
# @Date 	: 2019-02-24 14:11:08
# @License 	: Copyright(C), USTC
# @Last Modified by  : jianhuChen
# @Last Modified time: 2019-02-24 14:13:35

from django.conf.urls import url
from . import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'Intelligent_QA_System.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.index, name='index'),
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^upload_file/', views.upload_file, name='upload_file'),
    url(r'^delete_file/', views.delete_file, name='delete_file'),
    url(r'^qa_generation/(?P<index>[0-9]*)', views.qa_generation, name='qa_generation'),
    url(r'^qa_management/(?P<index>[0-9]*)', views.qa_management, name='qa_management'),
    url(r'^qa_generate/', views.qa_generate, name='qa_generate'),
    url(r'^qa_create/', views.qa_create, name='qa_create'),
    url(r'^qa_delete/', views.qa_delete, name='qa_delete'),
    url(r'^qa_update/pk=(?P<pk>[0-9]*)', views.qa_update, name='qa_update'),
    url(r'^qa_search/(?P<index>[0-9]*)', views.qa_search, name='qa_search'),
    url(r'^user_management/(?P<index>[0-9]*)', views.user_management, name='user_management'),
    url(r'^user_delete/', views.user_delete, name='user_delete'),
    url(r'^user_update/', views.user_update, name='user_update'),
    url(r'^user_create/', views.user_create, name='user_create'),
]