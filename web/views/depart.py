# by 362416272@qq.com

from stark.service.v1 import StarkHandler


# 部门表
class DepartHandler(StarkHandler):
    list_display = ['title']
