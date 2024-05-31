'''
File Name: field
Create File Time: 2024/5/28 10:14
File Create By Author: Yang Guanqun
Email: yangguanqunit@outlook.com
'''
from enum import Enum


class SearchType(Enum):
    # 综合
    DEFAULT = "1"

    # 实时
    REAL_TIME = "61"

    # 热门
    POPULAR = "60"

    # 视频
    VIDEO = "64"
