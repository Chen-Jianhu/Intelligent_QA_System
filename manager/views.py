from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.core.paginator import Paginator # 分页
from .models import *
from user.models import *
from py import QAGeneration

from py.QASearch import QASearch
import os

# Create your views here.
def index(request):
    mname = request.session.get('mname', '未登录')
    context = {
        'page_title': '管理首页',
        'name': mname,
    }
    return render(request, 'manager/index.html', context)

def login(request):
    mname = request.session.get('mname', '未登录')
    if mname == '未登录':
        is_handle_login = request.POST.get('is_handle_login', False)
        if is_handle_login:
            account = {
                'name': request.POST.get('name', None),
                'pwd': request.POST.get('pwd', None)
            }
            try:
                user = ManagerInfo.objects.filter(name=account['name'])[0]
            except IndexError:
                login_result = False
                login_info = '无此管理员，请检查用户名是否输入错误！'
            else:
                if user.pwd == account['pwd']:
                    login_result = True
                    login_info = '登陆成功！'
                    request.session['mname'] = account['name']
                    request.session.set_expiry(0)
                else:
                    login_result = False
                    login_info = '管理员密码输入错误！'
            context = {
                'page_title': '管理员登录',
                'name': request.session.get('mname', '未登录'),
                'login_result': login_result,
                'login_info': login_info,
                'is_handle_login': is_handle_login,
            }
        else:
            context = {
                'page_title': '管理员登录',
                'name': mname,
                'is_handle_login': is_handle_login,
            }
    else:
        login_info = '您已登录，请勿重复登录！'
        context = {
            'page_title': '管理员登录',
            'name': mname,
            'login_result': True,
            'login_info': login_info,
            'is_handle_login': True,
        }
    return render(request, 'manager/login.html', context)

def logout(request):
    mname = request.session.get('mname', '未登录')
    if mname == '未登录':
        logout_info = '退出失败，您还未登陆！'
    else:
        del request.session['mname']
        logout_info = '退出成功！'
    context = {
        'page_title': '退出',
        'name': '未登录',
        'logout_info': logout_info,
    }
    return render(request, 'manager/logout.html', context)


def upload_file(request):
    mname = request.session.get('mname', '未登录')
    context = {
        'page_title': '文件上传',
        'name': mname,
    }
    if mname != '未登录':
        is_handle_upload = request.POST.get('is_handle_upload', False)
        context['is_handle_upload'] = is_handle_upload
        if is_handle_upload: # 处理上传
            if request.method == "POST":
                file = request.FILES['doc']
                file_path = '%s/%s' % (settings.UPLOAD_ROOT, file.name)
                with open(file_path, 'wb') as f:
                    for content in file.chunks():
                        f.write(content)
                upload_result = True
            else:
                upload_result = False
            context['upload_result'] = upload_result,
    return render(request, 'manager/upload_file.html', context)

def qa_generate(request, index):
    mname = request.session.get('mname', '未登录')
    context = {
        'page_title': 'QA对生成',
        'name': mname,
    }
    if mname != '未登录':
        # 获取上传文件列表
        files  = os.listdir('./static/manager/upload')
        file_list = [{i:file_name} for i, file_name in zip(range(1, len(files) + 1), files)]
        all_file = Paginator(file_list, 10)
        index_list = all_file.page_range # 页码列表
        if index == '' :
            index = '1'
        index = int(index)
        if index < index_list[0] or index > index_list[-1]: # 控制页码不超出范围
            index = 1
        this_page_list = all_file.page(index)
        context['index'] = index # 当前页码
        context['this_page_list'] = this_page_list # 当前页内容列表
        context['index_list'] = index_list  # 页码列表
    return render(request, 'manager/qa_generate.html', context)


def qa_management(request, index):
    mname = request.session.get('mname', '未登录')
    context = {
        'page_title': '知识库管理',
        'name': mname,
    }
    if mname != '未登录':
        # 调用es search
        es = QASearch(index="qa_pairs")
        qa_data = es.get_all_data()
        # 更改es默认的键值
        for i, qa in enumerate(qa_data):
            qa['id'] = i+1
            qa['e_id'] = qa.pop('_id')
            qa['source'] = qa.pop('_source')
            qa['question'] = qa['source']['question']
            qa['answer'] = qa['source']['answer']

        qa_all_page = Paginator(qa_data, 10)
        index_list = qa_all_page.page_range # 页码列表
        if index == '':
            index = '1'
        index = int(index)
        if index < index_list[0] or index > index_list[-1]: # 控制页码不超出范围
            index = 1
        this_page_list = qa_all_page.page(index)
        context['index'] = index # 当前页码
        context['this_page_list'] = this_page_list # 当前页内容列表
        context['index_list'] = index_list # 页码列表
    return render(request, 'manager/qa_management.html', context)


def user_management(request, index):
    mname = request.session.get('mname', '未登录')
    context = {
        'page_title': '用户管理',
        'name': mname,
    }
    if mname != '未登录':
        user_list = UserInfo.manager.all()
        user_all_page = Paginator(user_list, 10)
        index_list = user_all_page.page_range  # 页码列表
        if index == '':
            index = '1'
        index = int(index)
        if index < index_list[0] or index > index_list[-1]:  # 控制页码不超出范围
            index = 1
        this_page_list = user_all_page.page(index)
        context['index'] = index  # 当前页码
        context['this_page_list'] = this_page_list  # 当前页内容列表
        context['index_list'] = index_list  # 页码列表
    return render(request, 'manager/user_management.html', context)


def qa_create(request):
    mname = request.session.get('mname', '未登录')
    context = {
        'page_title': '新增QA对',
        'name': mname,
    }
    if mname != '未登录':
        is_handle_create = request.POST.get('is_handle_create', False)
        context['is_handle_create'] = is_handle_create
        if is_handle_create:
            qa = {
                'question': request.POST.get('question', None),
                'answer': request.POST.get('answer', None)
            }
            if qa['question'] == '' or qa['answer'] == '':
                create_result = False
                create_info = '添加记录失败,请确保问题和答案都不为空!'
            else:
                new_qa = QA.manager.create(qa)
                new_qa.save()
                create_result = True
                create_info = '成功添加一条记录！'
            context['create_result'] = create_result
            context['create_info'] = create_info
    return render(request, 'manager/qa_create.html', context)

def qa_update(request, pk):
    mname = request.session.get('mname', '未登录')
    context = {
        'page_title': '修改QA对',
        'name': mname,
    }
    if mname != '未登录':
        is_handle_update = request.POST.get('is_handle_update', False)
        context['is_handle_update'] = is_handle_update
        try:
            need_update_qa = QA.manager.get(pk=pk)
        except:
            update_result = False
            update_info = '修改失败,未找到此QA对!'
            context['update_result'] = update_result
            context['update_info'] = update_info
        else:
            if need_update_qa.is_delete == True: # 已经被逻辑删除
                update_result = False
                update_info = '修改失败,未找到此QA对!'
                context['update_result'] = update_result
                context['update_info'] = update_info
            else:
                if not is_handle_update: # 读取信息,返回前台
                    question_content =  need_update_qa.question
                    answer_content = need_update_qa.answer
                    context['question_content'] = question_content
                    context['answer_content'] = answer_content
                else: # 更新信息
                    qa = {
                        'question': request.POST.get('question', None),
                        'answer': request.POST.get('answer', None)
                    }
                    if qa['question'] == '' or qa['answer'] == '':
                        update_result = False
                        update_info = '修改失败,请确保<b>问题</b>和<b>答案</b>都不为空!'
                    else:
                        need_update_qa.question = qa['question']
                        need_update_qa.answer = qa['answer']
                        need_update_qa.save()
                        update_result = True
                        update_info = '修改成功！'
                    context['update_result'] = update_result
                    context['update_info'] = update_info
        context['pk'] = pk
    return render(request, 'manager/qa_update.html', context)

def qa_delete(request, pk):
    mname = request.session.get('mname', '未登录')
    context = {
        'page_title': '删除QA对',
        'name': mname,
    }
    if mname != '未登录':
        try:
            need_delete_qa = QA.manager.get(pk=pk)
        except:
            delete_result = False
            delete_info = '删除失败,未找到此QA对!'
        else:
            if need_delete_qa.is_delete: # 已经逻辑删除过了
                delete_result = False
                delete_info = '删除失败,未找到此QA对!'
            else:
                delete_result = True
                context['need_delete_qa'] = need_delete_qa
                need_delete_qa.is_delete = True # 逻辑删除
                delete_info = '删除成功!'
                need_delete_qa.save()
        context['delete_result'] = delete_result
        context['delete_info'] = delete_info
    return render(request, 'manager/qa_delete.html', context)

def qa_search(request):
    mname = request.session.get('mname', '未登录')
    context = {
        'page_title': '搜索结果',
        'name': mname,
    }
    if mname != '未登录':
        pass
    return HttpResponse('开发中')


def user_delete(request):
    mname = request.session.get('mname', '未登录')
    context = {
        'page_title': '删除用户',
        'name': mname,
    }
    if mname != '未登录':
        pass
    return HttpResponse('开发中')


def user_update(request):
    mname = request.session.get('mname', '未登录')
    context = {
        'page_title': '修改用户资料',
        'name': mname,
    }
    if mname != '未登录':
        pass
    return HttpResponse('开发中')

    