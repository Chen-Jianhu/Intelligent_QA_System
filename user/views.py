from django.shortcuts import render
from django.http import HttpResponse

from .models import *
from py.QASearch import *
from py.ChatRobot import *

import time

# Create your views here.
def index(request):
    uname = request.session.get('uname', '未登录')
    context = {
        'page_title': '主页',
        'name': uname,
    }
    return render(request, 'user/index.html', context)


def login(request):
    uname = request.session.get('uname', '未登录')
    if uname == '未登录':
        is_handle_login = request.POST.get('is_handle_login', False)
        if is_handle_login:
            account = {
                'name': request.POST.get('name', None),
                'pwd': request.POST.get('pwd', None)
            }
            try:
                user = UserInfo.manager.filter(name=account['name'])[0]
            except IndexError:
                login_result = False
                login_info = '无此用户，请检查用户名是否输入错误！'
            else:
                if user.pwd == account['pwd']:
                    login_result = True
                    login_info = '登陆成功！'
                    request.session['uname'] = account['name']
                    request.session.set_expiry(0)
                else:
                    login_result = False
                    login_info = '密码输入错误！'
            context = {
                'page_title': '登录',
                'name': request.session.get('mname', '未登录'),
                'login_result': login_result,
                'login_info': login_info,
                'is_handle_login': is_handle_login,
            }
        else:
            context = {
                'page_title': '登录',
                'name': uname,
                'is_handle_login': is_handle_login,
            }
    else:
        login_info = '您已登录，请勿重复登录！'
        context = {
            'page_title': '登录',
            'name': uname,
            'login_result': True,
            'login_info': login_info,
            'is_handle_login': True,
        }
    return render(request, 'user/login.html', context)


def register(request):
    uname = request.session.get('uname', '未登录')
    context = {
        'page_title': '注册',
        'name': uname,
    }
    return render(request, 'user/register.html', context)


def logout(request):
    uname = request.session.get('uname', '未登录')
    if uname == '未登录':
        logout_info = '退出失败，您还未登陆！'
    else:
        del request.session['uname']
        logout_info = '退出成功！'
    context = {
        'page_title': '退出',
        'name': '未登录',
        'logout_info': logout_info,
    }
    return render(request, 'user/logout.html', context)


def get_answer(request):
    uname = request.session.get('uname', '未登录')
    question = request.POST.get('user_question', '你叫什么名字？')
    if uname == '未登录':
        answer = '您还未登陆！请先登录再向小科提问哦～<a href="/login" style="color:orange">点这里登录</a>'
    else:
        # 调用es search
        es = QASearch(index="qa_pairs")
        # es.insert_from_file('./QA_pairs_compute.json')
        try:
            result, url = es.search_data(question)
            # answer = result.replace('\n', '<br>') + '<br>答案链接：' + '<a target="_blank" style="color:#FFFFFF" href=' + url + '>' + url
            answer = result
            if url:
                answer += '<br>答案链接：' + '<a target="_blank" style="color:#FFFFFF" href=' + url + '>' + url + '</a>'
            print('[{}]调用es search'.format(time.ctime()))
        except:
            # 调用图灵机器人
            R = ChatRobot()
            answer = R.chat_with_tulin(uname, question)
            if answer != 'Error':
                print('[{}]调用图灵机器人器人'.format(time.ctime()))
            else:
                # 调用青云客机器人
                answer = R.chat_with_qyk(question)
                print('[{}]调用青云客机器人'.format(time.ctime()))
    return HttpResponse(answer)


def chat(request):
    uname = request.session.get('uname', '未登录')
    if uname == '未登录':
        answer = '您还未登陆！请先登录再向小科提问哦～<a href="/login" style="color:orange">点这里登录</a>'
    else:
        answer = '小科：您好' + uname + '，快问我一些问题吧~'
    context = {
        'page_title': '聊天',
        'name': uname,
        'answer': answer,
    }
    return render(request, 'user/chat.html', context)