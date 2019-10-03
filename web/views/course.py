# by 362416272@qq.com  

from stark.service.v1 import StarkHandler


class CourseHandler(StarkHandler):
    list_display = ['name', ]  # 自定义显示
