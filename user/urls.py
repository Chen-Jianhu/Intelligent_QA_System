# -*- coding: utf-8 -*-
# @File 	: urls.py
# @Author 	: jianhuChen
# @Date 	: 2019-02-24 14:11:02
# @License 	: Copyright(C), USTC
# @Last Modified by  : jianhuChen
# @Last Modified time: 2019-02-24 14:13:39

from django.conf.urls import url
from . import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'Intelligent_QA_System.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.index, name='index'),
    url(r'^login/', views.login, name='login'),
    url(r'^register/', views.register, name='register'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^chat/', views.chat, name='chat'),
    url(r'^get_answer/', views.get_answer, name='get_answer'),
]
