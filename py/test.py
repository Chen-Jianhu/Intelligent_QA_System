#coding=utf-8

import os
from HuaweiCloud import HuaweiCloud

H = HuaweiCloud()

# 获取菜单
# H.get_menu_items()

# 下载页面
# h1_list = ['网络']
# H.download_page(h1_list, './spider/menu_items.json')

# 解析页面
h1_list = ['网络']
heading_1_path = ['./spider/' + h1 +'/' for h1 in h1_list]
for h1, h1_path in zip(h1_list, heading_1_path):
    heading_2_list = os.listdir(h1_path)
    file_path = []
    for h2 in heading_2_list:
        html_files = os.listdir(os.path.join(h1_path, h2))
        file_path += [os.path.join(h1_path, h2, file_name) for file_name in html_files]
    H.parse_page(file_path[:], h1 +'_contents.json')
