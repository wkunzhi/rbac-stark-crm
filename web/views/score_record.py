# by 362416272@qq.com
# 积分记录

from stark.service.v1 import StarkHandler, StarkModelForm
from django.conf.urls import url
from web import models
from .base import PermissionHandler  # 粒度控制


class ScoreModelForm(StarkModelForm):
    class Meta:
        model = models.ScoreRecord
        fields = ['content', 'score']


class ScoreHandler(PermissionHandler, StarkHandler):
    model_form_class = ScoreModelForm
    list_display = ['content', 'score', 'user', ]  # 自定义显示

    # 重构，url
    def get_urls(self):  # 重写url
        patterns = [
            url(r'^list/(?P<student_id>\d+)/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            url(r'^add/(?P<student_id>\d+)/$', self.wrapper(self.add_view), name=self.get_add_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    def get_list_display(self):
        """
        获取页面上应该显示的列，预留的自定义扩展，例如：以后根据用户的不同显示不同的列
        :return:
        """
        value = []
        # 默认展示 修改和 删除
        if self.list_display:
            value.extend(self.list_display)
        return value

    def get_queryset(self, request, *args, **kwargs):
        """筛选对应显示信息"""
        student_id = kwargs.get('student_id')
        return self.model_class.objects.filter(student_id=student_id)

    def save(self, request, form, is_update, *args, **kwargs):
        """保存分数"""
        student_id = kwargs.get('student_id')
        current_user_id = request.session['user_info']['id']
        form.instance.student_id = student_id
        form.instance.user_id = current_user_id

        form.save()  # 保存

        # 学生原来的积分  abs()取到绝对值
        score = form.instance.score
        print(score)
        if score > 0:
            form.instance.student.score += abs(score)
        else:
            form.instance.student.score -= abs(score)
        form.instance.student.save()
