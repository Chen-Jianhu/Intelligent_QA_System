from HuaweiCloud import *
import os

H = HuaweiCloud()

H.parse_page(['./spider/计算/云容器实例 CCI/什么是云容器实例.html',], './spider/计算_contents.json')
