'''
File Name: exception
Create File Time: 2024/5/27 15:37
File Create By Author: Yang Guanqun
Email: yangguanqunit@outlook.com
'''

from httpx import RequestError

# class 里还能没有逻辑代码的， 第一次见
class DataFetchError(RequestError):
    """something error when fetch"""


class IPBlockError(RequestError):
    """fetch so fast that the server block us ip"""
