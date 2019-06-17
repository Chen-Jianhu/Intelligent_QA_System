from django.contrib import admin
from .models import *
# Register your models here.


# 自定义管理界面
class UserInfoAdmin(admin.ModelAdmin):
    # 列表页属性==========================
    # 显示字段，可以点击列头进行排序
    list_display = ['pk', 'name', 'pwd']
    # 过滤字段，过滤框会出现在右侧
    # list_filter = ['btitle']
    # 搜索字段，搜索框会出现在上侧
    search_fields = ['name']
    # 分页，分页框会出现在下侧
    list_per_page = 10

admin.site.register(UserInfo, UserInfoAdmin)
