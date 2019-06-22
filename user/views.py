from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

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


def register_handle(request):
    uname = request.session.get('uname', '未登录')
    context = {
        'page_title': '用户注册',
        'name': uname,
    }
    result_img = ''
    try:
        UserInfo.manager.filter(name=request.POST.get('name', None))[0]
    except IndexError:
        # save user info to db
        try:
            # 接收头像
            file = request.FILES.get('img_file')
            # print('='*30+'\n'+file)
            file_name = request.POST.get('name', 'no_name') + '.' + file.name.split('.')[-1]
            save_path = '%s/%s' % (settings.USER_IMG_ROOT, file_name)
            with open(save_path, 'wb') as f:
                for content in file.chunks():
                    f.write(content)
        except:
            file_name = 'user.png'
            result_img = '(服务器接收头像失败，将使用默认用户头像！)'

        account = {
            'name': request.POST.get('name', None),
            'pwd': request.POST.get('pwd', None),
            'sex': eval(request.POST.get('sex')),
            'age': request.POST.get('age', None),
            'email': request.POST.get('email', None),
            'img_path': '/static/user/img/' + file_name,
        }
        try:
            new_user = UserInfo.manager.create(account)
            new_user.save()
            result = '注册成功！'
            request.session['uname'] = account['name']
        except:
            result = '注册失败！账号信息写入数据库错误！'
    else:
        result = '注册失败：该用户名（{}）已存在！'.format(request.POST.get('name', None))

    if result_img:
        result += result_img
    context['result'] = result
    return render(request, 'user/register_handle.html', context)


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
            result, url, subject = es.search_data(question)
            # answer = result.replace('\n', '<br>') + '<br>答案链接：' + '<a target="_blank" style="color:#FFFFFF" href=' + url + '>' + url
            answer = result
            if url:
                answer += '<br>答案链接：' + '<a target="_blank" style="color:#FFFFFF" href=' + url + '>' + url + '</a>'
            answer += '<br>主题：' + subject + '<br>'
            print('[{}]调用es search'.format(time.ctime()))
        except:
            # 调用图灵机器人
            Robot = ChatRobot()
            answer = Robot.chat_with_tulin(uname, question)
            if answer != 'Error':
                print('[{}]调用图灵机器人器人'.format(time.ctime()))
            else:
                # 调用青云客机器人
                answer = Robot.chat_with_qyk(question)
                print('[{}]调用青云客机器人'.format(time.ctime()))
    return HttpResponse(answer)


def chat(request):
    uname = request.session.get('uname', '未登录')
    user_img = '/static/user/img/user.png'
    if uname == '未登录':
        answer = '您还未登陆！请先登录再向小科提问哦～<a href="/login" style="color:orange">点这里登录</a>'
    else:
        answer = '小科：您好' + uname + '，快问我一些问题吧~'
        user = UserInfo.manager.get(name=uname)
        user_img = user.img_path
    context = {
        'page_title': '聊天',
        'name': uname,
        'answer': answer,
        'user_img': user_img,
    }
    return render(request, 'user/chat.html', context)


