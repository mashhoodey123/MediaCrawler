'''
File Name: async_test
Create File Time: 2024/5/27 10:52
File Create By Author: Yang Guanqun
Email: yangguanqunit@outlook.com
'''
import copy
import re
import json
import asyncio

import httpx
from tools import utils
from bs4 import BeautifulSoup


# headers = {
#     "User-Agent": utils.get_user_agent(),
#     "Cookie": "__ac_signature=_02B4Z6wo00f01mU1aSQAAIDDbxOyj4CBN.plFW2AAPxK9a; tt_webid=7311151821980190235; ttcid=505172fabf3f420a9c17ecb9265b7bda25; csrftoken=23ef8f85aedaf4a2f666f49fab77be18; _ga=GA1.1.1830206250.1702260199; s_v_web_id=verify_lvafozo9_klyHfxxS_jP3U_4I9q_9L7S_WQPcjqZFkTvI; passport_csrf_token=2c3452e681bae2d033a9495e752db658; passport_csrf_token_default=2c3452e681bae2d033a9495e752db658; local_city_cache=%E6%9D%AD%E5%B7%9E; _S_WIN_WH=1920_919; _S_DPR=1; _S_IPAD=0; gfkadpd=24,6457; msToken=-CWr-yWLqfiX5ZcbHe60wBwQ1CINWcqmrqxkPBF8PgIBrZ7LL0G2gozkuRTooS8dn670SQS7fHoi5vLDUytiCK9TxFLMaU0H2YLNMLch; _ga_QEHZPBE5HH=GS1.1.1717059270.227.1.1717064549.0.0.0; tt_scid=026YIKwCIHKMh3zWinNyHK3z0L.7IAxKqjNtGKBcE6GKHpLTEXSRhNJnXKk6e3Qz38e1; ttwid=1%7CYyHTdScUsMQhb5LrPuAH1qd_Vbgaeyrah34TnCQFQ54%7C1717064549%7Cbb52f7b1545441d383624d4774170bff68644ef924154850373f0b6a3feed782",
#     "Origin": "https://www.toutiao.com/c/user/token/MS4wLjABAAAAdG03Zz3A5JFDQ7cvPAhk4mWiXZz",
#     "Referer": "https://www.toutiao.com/c/user/token/MS4wLjABAAAAdG03Zz3A5JFDQ7cvPAhk4mWiXZz",
#     "Content-Type": "application/json;charset=UTF-8"
# }

# headers = {
#     "User-Agent": utils.get_mobile_user_agent(),
#     "Cookie": "",
#     "Origin": "https://m.weibo.cn/",
#     "Referer": "https://m.weibo.cn/",
#     "Content-Type": "application/json;charset=UTF-8"
# }

# async def get_note_info_by_id():
#     url = "https://www.toutiao.com/c/user/token/MS4wLjABAAAAdG03Zz3A5JFDQ7cvPAhk4mWiXZzMDEcThpoKYuBBkfZhUzg8YneMVr2Lok4e1Dcw"
#     # url = "https://m.toutiao.com/w/1800364020539524"
#     # url = "https://m.weibo.cn/detail/5038039157449102"
#     async with httpx.AsyncClient() as client:
#         response = await client.request(
#             "GET", url, timeout=10, headers=headers
#         )
#         print(response.json())
#         # soup = BeautifulSoup(response.text, 'html.parser')
#         # div = soup.find_all("div", "weitoutiao-content")
#         # for br in div[0].find_all("br"):
#         #     br.replace_with("\n")
#         # text = div[0].get_text()
#         # print(re.sub(r'\n+', '\n', text))
#
#
# asyncio.run(get_note_info_by_id())
import execjs
from tools import utils
from playwright.async_api import async_playwright

user_agent = utils.get_user_agent()
headers = {
    "User-Agent": user_agent,
    "Cookie": "__ac_signature=_02B4Z6wo00f01mU1aSQAAIDDbxOyj4CBN.plFW2AAPxK9a; tt_webid=7311151821980190235; ttcid=505172fabf3f420a9c17ecb9265b7bda25; csrftoken=23ef8f85aedaf4a2f666f49fab77be18; _ga=GA1.1.1830206250.1702260199; s_v_web_id=verify_lvafozo9_klyHfxxS_jP3U_4I9q_9L7S_WQPcjqZFkTvI; passport_csrf_token=2c3452e681bae2d033a9495e752db658; passport_csrf_token_default=2c3452e681bae2d033a9495e752db658; local_city_cache=%E6%9D%AD%E5%B7%9E; _S_WIN_WH=1920_919; _S_DPR=1; _S_IPAD=0; gfkadpd=24,6457; __feed_out_channel_key=entertainment; msToken=JmGxMcXm2OkcKeo7pVnIVoNv7_97lz1Nea6Fo6uDsjbV5gM7wc-fIY7ApMF8R0dggUiQbGOHOSFi3i078MO5KsYC6tf_CRRWTOp0EPk5; _ga_QEHZPBE5HH=GS1.1.1717125380.229.1.1717125692.0.0.0; tt_scid=wUOXrbo4LRaktH.7F1MLVi9fkAosZZTF1awf0H4-scIx8o97ogA2Gf-txRM7Glka19d4; ttwid=1%7CYyHTdScUsMQhb5LrPuAH1qd_Vbgaeyrah34TnCQFQ54%7C1717125692%7C8de32aacea65d3ee982422d7615e6fdc101cd4e0a6bf105849de19ddb13d76a0",
    "Host": "www.toutiao.com",
    "Origin": "https://www.toutiao.com/",
    "Referer": "https://www.toutiao.com/",
    "Content-Type": "application/json;charset=UTF-8"
}
host = "https://www.toutiao.com"
uri = "/article/v4/tab_comments/"
params = {
    "aid": "24",
    "app_name": "toutiao_web",
    "offset": "0",
    "count": "20",
    "group_id": "1800531661838474",
    "item_id": "1800531661838474"
}


with httpx.Client() as client:
    response = client.request("GET", url=f"{host}{uri}", params=params, headers=headers)

#%%




#
# params = {
#     "aweme_id": ""
# }
# del headers["Origin"]
# index_url = "https://www.toutiao.com"
#
# # async with async_playwright() as playwright:
# #     chromium = playwright.chromium
# #     browser = await chromium.launch(headless=True, proxy=None)  # type: ignore
# #     browser_context = await browser.new_context(
# #         viewport={"width": 1920, "height": 1080},
# #         user_agent=user_agent
# #     )
# #     await browser_context.add_init_script(path="libs/stealth.min.js")
# #     context_page = await browser_context.new_page()
# #     await context_page.goto(index_url)
#
# async def __process_req_params(params, headers):
#     if not params:
#         return
#     headers = headers or headers
#     # local_storage: Dict = await playwright_page.evaluate("() => window.localStorage")  # type: ignore
#     douyin_js_obj = execjs.compile(open('libs/douyin.js').read())
#     common_params = {
#         "device_platform": "webapp",
#         "aid": "6383",
#         "channel": "channel_pc_web",
#         "cookie_enabled": "true",
#         "browser_language": "zh-CN",
#         "browser_platform": "Win32",
#         "browser_name": "Firefox",
#         "browser_version": "110.0",
#         "browser_online": "true",
#         "engine_name": "Gecko",
#         "os_name": "Windows",
#         "os_version": "10",
#         "engine_version": "109.0",
#         "platform": "PC",
#         "screen_width": "1920",
#         "screen_height": "1200",
#         # " webid": douyin_js_obj.call("get_web_id"),
#         # "msToken": local_storage.get("xmst"),
#         # "msToken": "abL8SeUTPa9-EToD8qfC7toScSADxpg6yLh2dbNcpWHzE0bT04txM_4UwquIcRvkRb9IU8sifwgM1Kwf1Lsld81o9Irt2_yNyUbbQPSUO8EfVlZJ_78FckDFnwVBVUVK",
#     }
#     params.update(common_params)
#     query = '&'.join([f'{k}={v}' for k, v in params.items()])
#     x_bogus = douyin_js_obj.call('sign', query, headers["User-Agent"])
#     params["X-Bogus"] = x_bogus
#
# # async def get(uri: str, params, headers):
#
# asyncio.run((__process_req_params(params, headers)))
#
#


