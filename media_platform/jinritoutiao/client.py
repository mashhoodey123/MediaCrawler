'''
File Name: client
Create File Time: 2024/5/27 15:20
File Create By Author: Yang Guanqun
Email: yangguanqunit@outlook.com
'''
import copy
import json
import re

import httpx
from typing import Dict, Any, Optional, Callable
from urllib.parse import urlencode
from playwright.async_api import Page, BrowserContext

from tools import utils

from .exception import DataFetchError

class JrttClient:
    def __init__(
            self,
            timeout=10,
            proxies=None,
            *,
            headers: Dict[str, str],
            playwright_page: Page,
            cookie_dict: Dict[str, str],
    ):
        self.proxies = proxies
        self.timeout = timeout
        self.headers = headers
        self._host = "https://www.toutiao.com"
        self.playwright_page = playwright_page
        self.cookie_dict = cookie_dict

        # self.comment_headers = copy.deepcopy(headers)
        self.comment_uri = "/article/v4/tab_comments/"
        self.reply_uri = "/2/comment/v4/reply_list/"

    # Q: method 是个函数吗? A: get and post
    async def request(self, method, url, **kwargs) -> Any:
        async with httpx.AsyncClient(proxies=self.proxies) as client:
            response = await client.request(
                method, url, timeout=self.timeout,
                **kwargs
            )
        data: Dict = response.json()
        if data.get("ok") != 1:
            utils.logger.error(f"[JinritoutiaoClient.request] request {method}:{url} err, res:{data}")
            raise DataFetchError(data.get("msg", "unkonw error"))
        else:
            return data

    # uri: uniform resource identifier  url: uniform resource locator  url 是一种具体的uri
    async def get(self, uri: str, params=None, headers=None) -> Dict:
        final_uri = uri
        if isinstance(params, dict):
            final_uri = (f"{uri}?"
                         f"{urlencode(params)}")

        if headers is None:
            headers = self.headers
        return await self.request(method="GET", url=f"{self._host}{final_uri}", headers=headers)

    async def post(self, uri: str, data: dict) -> Dict:
        # separators 默认是(',', ': ')
        json_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        return await self.request(method="POST", url=f"{self._host}{uri}",
                                  data=json_str, headers=self.headers)

    async def pong(self) -> bool:
        utils.logger.info("[JinritoutiaoClient.pong] Begin pong jinritoutiao...")
        ping_flag = False
        try:
            uri = "/api/config"
            resp_data: Dict = await self.request(method="GET", url=f"{self._host}{uri}", headers=self.headers)
            if resp_data.get("login"):
                ping_flag = True
            else:
                utils.logger.error("[JinritoutiaoClient.pong] cookie may be invalid and again login...")
        except Exception as e:
            utils.logger.error(f"[JinritoutiaoClient.pong] Pong jinritoutiao failed: {e}, and try to login again...")
            ping_flag = False
        return ping_flag

    async def update_cookies(self, browser_context: BrowserContext):
        cookie_str, cookie_dict = utils.convert_cookies(await browser_context.cookies())
        self.headers["Cookie"] = cookie_str
        self.cookie_dict = cookie_dict

    async def get_note_all_comments(self, note_id: str):
        # get count of comments
        comment_info = await self.get_note_comments(note_id, 0, 1)
        total_comments = comment_info




    async def get_note_comments(self, note_id: str, offset=0, count=20, init=False):
        params = {
            "aid": "24",
            "app_name": "toutiao_web",
            "offset": f"{offset}",
            "count": f"{count}",
            "group_id": note_id,
            "item_id": note_id
        }
        uri = self.comment_uri
        headers = self.headers
        comments_res = await self.get(uri, params, headers)
        if init:
            return comments_res
        return comments_res



    async def get_comment_all_replies(self, comment_id: str, offset=0, count=5):
        params = {
            "aid": "24",
            "app_name": "toutiao_web",
            "id": "7371978804346553123",
            "offset": f"{offset}",
            "count": f"{count}",
            "repost": "0"
        }
        pass


    async def get_note_info_by_id(self, note_id: str) -> Dict:
        url = f"{self._host}//{note_id}"
        async with httpx.AsyncClient(proxies=self.proxies) as client:
            response = await client.request(
                "GET", url, timeout=self.timeout, headers=self.headers
            )
            if response.status_code != 200:
                raise DataFetchError(f"get jinritoutiao detail err: {response.text}")
            match = re.search(r'var \$render_data = (\[.*?\])\[0\]', response.text, re.DOTALL)
            if match:
                render_data_json = match.group(1)
                render_data_dict = json.loads(render_data_json)
                note_detail = render_data_dict[0].get("status")
                note_item = {
                    "blog": note_detail
                }
                return note_item
            else:
                utils.logger.info(f"[JinritoutiaoClient.get_note_info_by_id] 未找到$render_data的值")
                return dict()