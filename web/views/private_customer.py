# by 362416272@qq.com  
from django.utils.safestring import mark_safe
from django.shortcuts import reverse  # 反向生成url
from stark.service.v1 import StarkHandler, get_choice_text, get_m2m_text, StarkModelForm
from web import models
from .base import PermissionHandler  # 粒度控制


# 自定义剔除课程顾问这一项,直接默认当前登录对象
class PrivateCustomerModelForm(StarkModelForm):
    class Meta:
        model = models.Customer
        exclude = ['consultant', ]


class PrivateCustomerHandler(PermissionHandler, StarkHandler):
    def display_record(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '跟进记录'

        # 直接用 reverse，不用加原搜索条件保留
        record_url = reverse('stark:web_consultrecord_list', kwargs={'customer_id': obj.pk})  # 带上id 反向生成别名
        return mark_safe('<a target="_blank" href="%s">查看跟进</a>' % record_url)

    def display_pay_record(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '缴费记录'

        # 直接用 reverse，不用加原搜索条件保留
        record_url = reverse('stark:web_paymentrecord_list', kwargs={'customer_id': obj.pk})  # 带上id 反向生成别名
        return mark_safe('<a target="_blank" href="%s">缴费</a>' % record_url)

    list_display = [StarkHandler.display_checkbox, 'name', 'qq',
                    get_m2m_text('咨询课程', 'course'), get_choice_text('状态', 'status'), display_record,
                    display_pay_record]  # 自定义显示

    def get_queryset(self, request, *args, **kwargs):
        current_user_id = request.session['user_info']['id']
        return self.model_class.objects.filter(consultant_id=current_user_id)  # 课程顾问为指定id的

    def save(self, request, form, is_update, *args, **kwargs):  # 重写模块中的方法
        """当在销售顾问登录的情况下，可以添加咨询客户，默认就是添加给自己"""
        # 默认添加学员是给当前id的销售顾问
        if not is_update:  # 增加  否则是 更新
            current_user_id = request.session['user_info']['id']
            form.instance.consultant_id = current_user_id
        form.save()  # 保存

    # 自定义函数,stark组件里有案例
    def action_multi_remove(self, request, *args, **kwargs):
        """批量移除到公户，自定义函数"""
        current_user_id = request.session['user_info']['id']
        pk_list = request.POST.getlist('pk')  # 选中客户id列表

        # 校验 id__in=pk_list  过滤 id 是否在 pk_list这个列表中
        self.model_class.objects.filter(id__in=pk_list, consultant_id=current_user_id).update(consultant=None)

    # 自定义函数必须引入action_list
    action_multi_remove.text = '批量剔除到公户'
    action_list = [action_multi_remove, ]
    model_form_class = PrivateCustomerModelForm
