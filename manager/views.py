from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.core.paginator import Paginator  # 分页
from .models import *
from user.models import *
from py import QAGeneration

from py.QASearch import QASearch
from py.HuaweiCloud import HuaweiCloud
from py.QAGeneration import QAGeneration
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


def qa_generation(request, index):
    mname = request.session.get('mname', '未登录')
    context = {
        'page_title': 'QA对生成',
        'name': mname,
    }
    if mname != '未登录':
        # 获取上传文件列表
        files = os.listdir('./static/manager/upload')
        # 记录是否生成
        is_generation = []
        for f in files:
            is_g = f.startswith('(已生成)')
            is_generation.append(is_g)
        file_list = [{'i': i, 'file_name': file_name, 'is_generate': is_g} for i, file_name, is_g in zip(range(1, len(files) + 1), files, is_generation)]
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
    return render(request, 'manager/qa_generation.html', context)


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
            qa['es_id'] = qa.pop('_id')
            qa['source'] = qa.pop('_source')
            qa['source']['link'] = qa['source']['link'].split('//')[-1]
            # qa['question'] = qa['source']['question']
            # qa['answer'] = qa['source']['answer']

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


def qa_generate(request):
    mname = request.session.get('mname', '未登录')
    context = {
        'page_title': 'QA对生成',
        'name': mname,
    }
    if mname != '未登录':
        file_path = './static/manager/upload/' + request.POST.get('fname')
        print(file_path)
        # 调用华为云页面解析程序
        print('调用华为云页面解析程序')
        HW = HuaweiCloud()
        parse_data = HW.parse_page([file_path, ])
        print(parse_data)
        # 调用生成算法
        print('调用QA生成算法')
        QAG = QAGeneration()
        new_qa_pairs = QAG.run(parse_data)
        # 添加进ES中
        # 调用es search
        print('调用ES插入算法')
        es = QASearch(index="qa_pairs")
        if es.insert_from_mem(new_qa_pairs):
            result = '本次共生成{}条QA对！'.format(len(new_qa_pairs))
            # 生成成功后加上标识
            file_split = file_path.split('/')
            if not file_split[-1].startswith('(已生成)'):
                file_split[-1] = '(已生成)' + file_split[-1]
                new_name = '/'.join(file_split)
                os.rename(file_path, new_name)
        else:
            result = '生成QA对失败！'
    else:
        result = '后台管理操作需要先登录管理员账户！'
    return HttpResponse(result)


def qa_create(request):
    mname = request.session.get('mname', '未登录')
    context = {
        'page_title': '新增QA对',
        'name': mname,
    }
    if mname != '未登录':
        qa = {
            'question': request.POST.get('question', None),
            'answer': request.POST.get('answer', None),
            "link": request.POST.get('link', None),
            "subject": request.POST.get('subject', None),
        }
        if qa['question'] == '' or qa['answer'] == '':
            create_info = '添加记录失败,请确保问题和答案都不为空!'
        else:
            # 调用es search
            es = QASearch(index="qa_pairs")
            create_result = es.insert_one_data(data=qa)
            if create_result:
                create_info = '成功添加一条记录！'
            else:
                create_info = '添加记录失败！请重试~'
    return HttpResponse(create_info)


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


def qa_delete(request):
    mname = request.session.get('mname', '未登录')
    context = {
        'page_title': '删除QA对',
        'name': mname,
    }
    # 获取需要删除的QA对的es_id
    del_es_id = request.POST.get('del_es_id', None)
    if mname != '未登录':
        # 调用es search
        es = QASearch(index="qa_pairs")
        delete_result = es.delete_one_data(id=del_es_id)
        if not delete_result:
            delete_info = '删除失败,未找到此QA对!'
        else:
            delete_info = '删除成功!'
        context['delete_result'] = delete_result
        context['delete_info'] = delete_info
    return HttpResponse(delete_info)


def qa_search(request, index):
    mname = request.session.get('mname', '未登录')
    context = {
        'page_title': '搜索结果',
        'name': mname,
    }
    if mname != '未登录':
        # 存放搜索结果
        # 搜索方式
        q_type = request.POST.get('search_type', None)
        content = request.POST.get('search_content', None)
        # 调用es search
        es = QASearch(index="qa_pairs")
        print(q_type)
        if q_type == 'a':
            qa_data = es.search_datas_by_answer(content=content)
        else:
            qa_data = es.search_datas_by_question(content=content)

        # 更改es默认的键值
        for i, qa in enumerate(qa_data):
            qa['id'] = i + 1
            qa['es_id'] = qa.pop('_id')
            qa['source'] = qa.pop('_source')
            qa['question'] = qa['source']['question']
            qa['answer'] = qa['source']['answer']

        qa_all_page = Paginator(qa_data, 10)
        index_list = qa_all_page.page_range  # 页码列表
        if index == '':
            index = 1
        index = int(index)
        if index < index_list[0] or index > index_list[-1]:  # 控制页码不超出范围
            index = 1
        this_page_list = qa_all_page.page(index)
        context['index'] = index  # 当前页码
        context['this_page_list'] = this_page_list  # 当前页内容列表
        context['index_list'] = index_list  # 页码列表
    return render(request, 'manager/qa_search.html', context)


def user_delete(request):
    mname = request.session.get('mname', '未登录')
    context = {
        'page_title': '删除用户',
        'name': mname,
    }
    # 获取需要删除的QA对的es_id
    del_id = request.POST.get('id', None)
    if mname != '未登录':
        try:
            need_del_user = UserInfo.manager.get(pk=del_id)
        except:
            result = '删除失败,未找在数据库到此用户!'
        else:
            need_del_user.delete()
            result = '删除成功！'
    else:
        result = '后台管理操作需要先登录管理员账户！'
    return HttpResponse(result)


def user_update(request):
    mname = request.session.get('mname', '未登录')
    context = {
        'page_title': '修改用户资料',
        'name': mname,
    }
    if mname != '未登录':
        pass
    return HttpResponse('开发中')


def delete_file(request):
    mname = request.session.get('mname', '未登录')
    context = {
        'page_title': '删除文件',
        'name': mname,
    }
    if mname != '未登录':
        fname = request.POST.get('fname', None)
        file_path = './static/manager/upload/'+fname
        if fname and os.path.exists(file_path):
            os.remove(file_path)
            result = '删除成功！'
        else:
            result = '删除失败！'
    else:
        result = '后台管理操作需要先登录管理员账户！'
    return HttpResponse(result)


def user_create(request):
    mname = request.session.get('mname', '未登录')
    context = {
        'page_title': '新增用户',
        'name': mname,
    }
    if mname != '未登录':
        account = {
            'name': request.POST.get('name', None),
            'pwd': request.POST.get('pwd', None),
            'sex': request.POST.get('sex', None),
            'age': request.POST.get('age', None),
            'email': request.POST.get('email', None),
            'img_path': None,
        }
        try:
            UserInfo.manager.filter(name=account['name'])[0]
        except IndexError:
            # save user info to db
            try:
                new_user = UserInfo.manager.create(account)
                new_user.save()
                result = '新增用户成功！'
            except :
                result = '创建失败！'
        else:
            result = '错误：该用户名（{}）已存在！'.format(account['name'])
    else:
        result = '后台管理操作需要先登录管理员账户！'
    return HttpResponse(result)
