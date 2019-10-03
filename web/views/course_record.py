# by 362416272@qq.com
# 上课记录

from stark.service.v1 import StarkHandler, StarkModelForm
from django.conf.urls import url
from django.shortcuts import HttpResponse, reverse, render
from django.utils.safestring import mark_safe
from django.forms.models import modelformset_factory  # 批量
from web import models
from .base import PermissionHandler  # 粒度控制


class CourseRecordModelForm(StarkModelForm):
    class Meta:
        model = models.CourseRecord
        fields = ['day_num', 'teacher']


class StudyRecordModelForm(StarkModelForm):
    """修改考勤记录"""
    class Meta:
        model = models.StudyRecord
        fields = ['record']


class CourseRecordHandler(PermissionHandler, StarkHandler):
    model_form_class = CourseRecordModelForm

    # 重构自定制，操作按钮的url（带参）
    def display_attendance(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return "考勤"
        # 取别名
        name = "%s:%s" % (self.site.namespace, self.get_url_name('attendance'))
        attendance_url = reverse(name, kwargs={'course_record_id': obj.pk})
        tpl = '<a target="_blank" href="%s">考勤操作</a>' % attendance_url
        return mark_safe(tpl)

    list_display = [StarkHandler.display_checkbox, 'class_object', 'day_num', 'teacher', 'date', display_attendance]  # 自定义显示

    # 重构自定制，操作按钮的url（带参）
    def display_edit_del(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return "操作"
        class_id = kwargs.get('class_id')
        tpl = '<a href="%s">编辑</a> | <a href="%s">删除</a>' % (
            self.reverse_change_url(pk=obj.pk, class_id=class_id),
            self.reverse_delete_url(pk=obj.pk, class_id=class_id))
        return mark_safe(tpl)

    # 重构url
    def get_urls(self):
        patterns = [
            url(r'^list/(?P<class_id>\d+)/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            url(r'^add/(?P<class_id>\d+)/$', self.wrapper(self.add_view), name=self.get_add_url_name),
            url(r'^change/(?P<class_id>\d+)/(?P<pk>\d+)/$', self.wrapper(self.change_view),
                name=self.get_change_url_name),
            url(r'^delete/(?P<class_id>\d+)/(?P<pk>\d+)/$', self.wrapper(self.delete_view),
                name=self.get_delete_url_name),
            url(r'^attendance/(?P<course_record_id>\d+)/$', self.wrapper(self.attendance_view),
                name=self.get_url_name('attendance')),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    def get_queryset(self, request, *args, **kwargs):
        class_id = kwargs.get('class_id')
        return self.model_class.objects.filter(class_object_id=class_id)

    def save(self, request, form, is_update, *args, **kwargs):
        class_id = kwargs.get('class_id')
        if not is_update:
            form.instance.class_object_id = class_id
        form.save()

    def action_multi_init(self, request, *args, **kwargs):
        """添加批量操作action"""
        course_record_id_list = request.POST.getlist('pk')  # 班级所有课程
        class_id = kwargs.get('class_id')
        class_obj = models.ClassList.objects.filter(id=class_id).first()
        if not class_obj:
            return HttpResponse('班级不存在')
        student_obj_list = class_obj.student_set.all()  # 取班级的所有学生
        for course_record_id in course_record_id_list:
            course_record_obj = models.CourseRecord.objects.filter(id=course_record_id, class_object_id=class_id).first()
            if not course_record_obj:
                # 上课记录不存在
                continue

            study_record_exists = models.StudyRecord.objects.filter(course_record=course_record_obj).exists()
            if study_record_exists:
                # 课记录考勤记录已经存在
                continue

            # 为每个学生在该天创建考勤记录
            '''创建对象到内存'''
            study_record_object_list = [models.StudyRecord(student_id=stu.id, course_record_id=course_record_id) for stu
                                        in student_obj_list]
            '''提交到数据库'''
            models.StudyRecord.objects.bulk_create(study_record_object_list, batch_size=50)  # 一次提交50个

    action_multi_init.text = '批量初始化考勤'
    action_list = [action_multi_init, ]

    def attendance_view(self, request, course_record_id, *args, **kwargs):
        """考勤记录view"""
        study_record_object_list = models.StudyRecord.objects.filter(course_record_id=course_record_id)
        study_model_formset = modelformset_factory(models.StudyRecord, form=StudyRecordModelForm, extra=0)  # extra 显示行

        if request.method == 'POST':
            formset = study_model_formset(queryset=study_record_object_list, data=request.POST)
            if formset.is_valid():  # 验证
                # 批量更新
                formset.save()
            return render(request, 'attendance.html', {'formset': formset})

        formset = study_model_formset(queryset=study_record_object_list)
        return render(request, 'attendance.html', {'formset': formset})
