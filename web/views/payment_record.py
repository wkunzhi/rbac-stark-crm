# by 362416272@qq.com
from stark.service.v1 import StarkHandler, StarkModelForm, get_choice_text
from django.conf.urls import url
from django import forms
from django.shortcuts import HttpResponse
from web import models
from .base import PermissionHandler  # 粒度控制


class PaymentRecordModelForm(StarkModelForm):
    class Meta:
        model = models.PaymentRecord
        fields = ['pay_type', 'paid_fee', 'class_list', 'note']


class StudentPaymentRecordModelForm(StarkModelForm):  # 包含学生信息的modelform
    qq = forms.CharField(label='QQ号', max_length=32)
    mobile = forms.CharField(label='手机号', max_length=32)
    emergency_contract = forms.CharField(label='紧急联系人电话', max_length=32)

    class Meta:
        model = models.PaymentRecord
        fields = ['pay_type', 'paid_fee', 'class_list', 'qq', 'mobile', 'emergency_contract', 'note']


class PaymentRecordHandler(PermissionHandler, StarkHandler):
    list_display = [get_choice_text('缴费类型', 'pay_type'), 'paid_fee', 'class_list', 'consultant',
                    get_choice_text('状态', 'confirm_status')]

    def get_list_display(self, request, *args, **kwargs):
        """
        重写该方法，因为缴费记录不需要修改和删除按钮，所以删除掉
        :return:
        """
        value = []
        if self.list_display:
            value.extend(self.list_display)
        return value

    # 重构，url ， 每个进记录都有一条url
    def get_urls(self):  # 重写url
        patterns = [
            url(r'^list/(?P<customer_id>\d+)/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            url(r'^add/(?P<customer_id>\d+)/$', self.wrapper(self.add_view), name=self.get_add_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    # 重写 获取对象的方法
    def get_queryset(self, request, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        current_user_id = request.session['user_info']['id']
        return self.model_class.objects.filter(customer_id=customer_id, customer__consultant_id=current_user_id)

    # modelform的钩子函数，可以判断使用哪个modelform
    def get_model_form_class(self, is_add, request, pk, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        student_exists = models.Student.objects.filter(customer_id=customer_id).exists()
        if student_exists:
            # 说明已经存在，就用 普通modelform
            return PaymentRecordModelForm

        return StudentPaymentRecordModelForm

    def save(self, request, form, is_update, *args, **kwargs):
        """因为样式隐藏了一些字段所以必须：自定义save同"""
        customer_id = kwargs.get('customer_id')
        current_user_id = request.session['user_info']['id']
        object_exists = models.Customer.objects.filter(id=customer_id,
                                                       consultant_id=current_user_id).exists()
        if not object_exists:
            return HttpResponse('非法操作')

        form.instance.customer_id = customer_id
        form.instance.consultant_id = current_user_id
        # 创建缴费记录信息
        form.save()

        # 额外要把学员信息的表创建也录入信息
        class_list = form.cleaned_data['class_list']
        fetch_student_obj = models.Student.objects.filter(customer_id=customer_id).first()
        if not fetch_student_obj:
            # 学员信息不存在才会增加
            qq = form.cleaned_data['qq']
            mobile = form.cleaned_data['mobile']
            emergency_contract = form.cleaned_data['emergency_contract']
            student_object = models.Student.objects.create(customer_id=customer_id, qq=qq, mobile=mobile,
                                                           emergency_contract=emergency_contract)
            student_object.class_list.add(class_list.id)  # 选中班级也添加进去 M2M操作
        else:
            # 已存在学员,也要加入m2m关系
            fetch_student_obj.class_list.add(class_list.id)  # 选中班级也添加进去 M2M操作
