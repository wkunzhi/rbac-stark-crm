# by 362416272@qq.com  
# by 362416272@qq.com

from django.utils.safestring import mark_safe
from django.shortcuts import reverse  # 反向生成url
from stark.service.v1 import StarkHandler, get_datetime_text, get_m2m_text, StarkModelForm, Option
from web import models
from stark.forms.widgets import DateTimePickerInput  # 时间样式forms需要引入自己写的部分
from .base import PermissionHandler  # 粒度控制


class ClassListModelForm(StarkModelForm):
    # 修改需要datetime样式的地方
    class Meta:
        model = models.ClassList
        fields = '__all__'
        widgets = {
            'start_date': DateTimePickerInput,
            'graduate_date': DateTimePickerInput,
        }


# 校区表
class ClassListHandler(PermissionHandler, StarkHandler):

    def display_course(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '班级'
        return '%s (%s)期' % (obj.course.name, obj.semester,)

    def display_course_record(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '上课记录'
        record_url = reverse('stark:web_courserecord_list', kwargs={'class_id': obj.pk})  # 带上id 反向生成别名
        return mark_safe('<a target="_blank" href="%s">上课记录</a>' % record_url)

    list_display = ['school',
                    display_course,
                    get_datetime_text('开班日期', 'start_date'),
                    'class_teacher',
                    get_m2m_text('老师', 'tech_teacher'),
                    display_course_record,
                    ]  # 自定义显示

    model_form_class = ClassListModelForm  # 自定义的样式（时间格式）

    # 加上组合搜索
    search_group = [
        Option(field='school'),
        Option(field='course'),
    ]

# 解决ManyToMany时get_m2m_text
# 解决时间显示样式get_datetime_text


