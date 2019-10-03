# by 362416272@qq.com

from stark.service.v1 import StarkHandler, get_choice_text, StarkModelForm, get_m2m_text, Option
from django.conf.urls import url
from django.shortcuts import reverse  # 反向生成url
from django.utils.safestring import mark_safe
from web import models
from .base import PermissionHandler  # 粒度控制


class StudentModelForm(StarkModelForm):
    """自定义显示指定字段"""
    class Meta:
        model = models.Student
        fields = ['qq', 'mobile', 'emergency_contract', 'memo']


class StudentHandler(PermissionHandler, StarkHandler):
    model_form_class = StudentModelForm

    def display_score(self, obj=None, is_header=None, *args, **kwargs):
        """新加一列"""
        if is_header:
            return '积分管理'
        # 反向取url
        record_url = reverse('stark:web_scorerecord_list', kwargs={'student_id': obj.pk})

        return mark_safe('<a target="_blank" href="%s">%s</a>' % (record_url, obj.score))

    list_display = ['customer', 'qq', 'mobile', 'emergency_contract', get_m2m_text('已报名班级', 'class_list'), display_score, get_choice_text('状态', 'student_status')]  # 自定义显示

    def get_add_btn(self, request, *args, **kwargs):
        """重构隐藏， 添加按钮"""
        return None

    def get_list_display(self, request, *args, **kwargs):
        """重构：只需要修改按钮"""
        value = []
        if self.list_display:
            value.extend(self.list_display)
            value.append(type(self).display_edit)
        return value

    def get_urls(self):
        """重构url ，值需要列表功能"""
        patterns = [
            url(r'^list/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            url(r'^change/(?P<pk>\d+)/$', self.wrapper(self.change_view), name=self.get_change_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    # 模糊搜索
    search_list = ['customer__name', 'qq', 'mobile', ]
    # 组合搜索
    search_group = [
        Option('class_list', text_func=lambda x: '%s-%s' % (x.school.title, str(x)))  # 利用text_func添加一个lambda函数处理显示字符串
    ]

