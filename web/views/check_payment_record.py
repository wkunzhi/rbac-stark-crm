# by 362416272@qq.com  
# 财务审核缴费

from django.conf.urls import url
from stark.service.v1 import StarkHandler, get_choice_text
from .base import PermissionHandler  # 粒度控制


class CheckPaymentRecordHandler(PermissionHandler, StarkHandler):
    # 排序显示
    order_list = ['-id', 'confirm_status']

    list_display = [StarkHandler.display_checkbox, 'customer', get_choice_text('缴费类型', 'pay_type'), 'paid_fee', 'class_list', 'apply_date',
                    get_choice_text('状态', 'confirm_status'), 'consultant']  # 自定义显示

    def get_list_display(self, request, *args, **kwargs):
        """
        重写该方法，因为缴费记录不需要修改和删除按钮，所以删除掉
        :return:
        """
        value = []
        if self.list_display:
            value.extend(self.list_display)
        return value

    def get_add_btn(self, request, *args, **kwargs):
        """重构不显示 添加按钮"""
        return None

    def get_urls(self):
        """重构url ，只需要列表功能"""
        patterns = [
            url(r'^list/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    def action_multi_confirm(self, request, *args, **kwargs):
        """添加批量确认action"""
        pk_list = request.POST.getlist('pk')
        # 修改三张表记录： 缴费记录表、客户表、学生表
        for pk in pk_list:
            payment_object = self.model_class.objects.filter(id=pk, confirm_status=1).first()
            if not payment_object:
                continue
            # 缴费记录表
            payment_object.confirm_status = 2
            payment_object.save()
            # 客户表更新
            payment_object.customer.status = 1
            payment_object.customer.save()
            # 学生表更新
            payment_object.customer.student.student_status = 2
            payment_object.customer.student.save()

    """添加action"""
    action_multi_confirm.text = '批量确认'

    def action_multi_cancel(self, request, *args, **kwargs):
        """添加批量驳回action"""
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list, confirm_status=1).update(confirm_status=3)

    """添加action"""
    action_multi_cancel.text = '批量驳回'

    action_list = [action_multi_confirm, action_multi_cancel]

