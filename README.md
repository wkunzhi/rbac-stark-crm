# CRM后台管理系统
> 基于Django：包含可拆卸 权限组件rbac 与 stark插件 可以单独取出代码并运用到任意后端开发项目中。 该套CRM系统就是用rbac组件+stark组件开发的《全国连锁烘焙学校管理系统》业务



**权限菜单**
![image](https://static.666.cq.cn/%E7%A7%81%E4%BA%BA/%E6%9D%83%E9%99%90%E5%88%9B%E5%BB%BA.png)

**权限分配**
![image](https://static.666.cq.cn/%E7%A7%81%E4%BA%BA/%E6%9D%83%E9%99%90%E5%88%86%E9%85%8D.png)

**批量创建权限菜单**
![image](https://static.666.cq.cn/%E7%A7%81%E4%BA%BA/%E6%89%B9%E9%87%8F%E5%88%9B%E5%BB%BA%E6%9D%83%E9%99%90%E8%8F%9C%E5%8D%95.png)

**用户管理**
![image](https://static.666.cq.cn/%E7%A7%81%E4%BA%BA/%E7%94%A8%E6%88%B7%E8%A1%A8.png)

# 环境
- Django 2.1.5
- Python 3.5
- Bootstrap v3

# 包含
- Rbac 权限组件
- Stark 路由与数据库操作组件
- crm 业务板块

# 项目背景
> 以教育机构为背景的crm项目，系统主要给销售部、运营部、教职部提供平台，对他们的工作进行量化。
- 销售部：
    1. 公户：公共用户
    2. 私户：我的客户 <=150 控制人数 + 跟进记录 + 入班申请（财物审核）
- 运营部：
    1. 客户信息录入（公户），等待转化
- 教质部
    1. 考勤
    2. 学员访谈记录
    3. 积分管理
    4. 转班申请
    
# 开发概述
1. **基础业务处理**
    - 校区管理
    - 部门管理
    - 用户管理
    - 课程管理
    - 开班管理

2. **客户管理**
    - 公户
    - 私户

3. **学员管理**
    - 考勤
    - 谈话记录
    - 积分
    
4. **应用rbac组件**


# 准备流程
> 流程:先通过stark组件完成业务开发，再套上rbac权限（stark放在rbac的app上）因为2个组件都有样式！可分离

> 准备：创建项目>数据库迁移

# 开发
1. 校区管理
2. 部门管理
3. 用户管理
    - 用户基本操作
    - 添加页面 增加确认密码字段并未密码形式，编辑页面删除密码字段
    - 重置密码
4. 课程管理
5. 班级管理
    - 对关联的forkey 或者m2m进行筛选  limit_choice_to
    - datetime时间插件拓展 示例：/web/views/class_list.py
    - 自定义Models 渲染
6. 客户管理

    - 公户
        - 公户基本管理： 公户列表、录入客户
        - 查看跟进记录
        - 申请到私户
    - 私户
        - 公户的账号申请到私户
        - 私户中剔除到公户
        - 跟进记录的管理
            - 查看  
            - 添加
            - 编辑
            - 删除
        - 缴费|报名
            - 学员缴费
            - 课程顾问：提交缴费申请
            - 财物：审核（状态更新、成功进班）
        - 学员管理
            - 学生管理
            - 积分管理
            - 考勤管理
                - 上课记录
                - 考勤记录
                    - 批量生成考勤记录
                    - 批量设置考勤记录
    - 权限组件应用
        - 应用
        - 粒度控制
        
