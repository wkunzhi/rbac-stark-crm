# by 362416272@qq.com  
# -*- coding:utf-8 -*-

from django.shortcuts import render, redirect
from web import models
from web.utils.MD5 import gen_md5
from rbac.service.init_permission import init_permission


def login(request):
    """
    用户登录
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'login.html')

    user = request.POST.get('user')
    pwd = gen_md5(request.POST.get('pwd', ''))

    # 根据用户名和密码去用户表中获取用户对象
    user = models.UserInfo.objects.filter(name=user, password=pwd).first()
    if not user:
        return render(request, 'login.html', {'msg': '用户名或密码错误'})
    request.session['user_info'] = {'id': user.id, 'nickname': user.nickname}

    '''利用rbac组件登录成功，初始化用户权限'''
    init_permission(user, request)
    return redirect('/index/')


def logout(request):
    """
    注销
    :param request:
    :return:
    """
    request.session.delete()

    return redirect('/login/')


def index(request):
    return render(request, 'index.html')
