'''
File Name: core
Create File Time: 2024/5/24 17:05
File Create By Author: Yang Guanqun
Email: yangguanqunit@outlook.com
'''

import asyncio
import os
import random

import config
from tools import utils
from var import crawler_type_var
from proxy.proxy_ip_pool import IpInfoModel, create_ip_pool
from store import jinritoutiao as jrtt_store
from asyncio import Task

"""
    Playwright 是一个由 Microsoft 开发的开源自动化库，用于控制浏览器并执行浏览器自动化相关的任务。
    它支持多种浏览器，包括但不限于 Chromium、Firefox 和 WebKit。用户可以用 Playwright 编写脚本来自动执行在浏览器中的操作，
    例如打开网页、填充表单、点击按钮、抓取网页内容等。
"""
from playwright.async_api import BrowserContext, BrowserType, Page, async_playwright

from base.base_crawler import AbstractCrawler
from typing import Tuple, Optional, Dict, List

from .client import JrttClient
from .login import JrttLogin
from .field import SearchType
from .help import filter_search_result_card
from .exception import DataFetchError


class JinritoutiaoCrawler(AbstractCrawler):
    platform: str
    login_type: str
    crawler_type: str
    context_page: Page
    jrtt_client: JrttClient
    browser_context: BrowserContext

    def __init__(self):
        self.index_url = "https://www.toutiao.com"
        self.mobile_index_url = "https://m.toutiao.com"
        self.user_agent = utils.get_user_agent()
        self.mobile_user_agent = utils.get_mobile_user_agent()

    def init_config(self, platform: str, login_type: str, crawler_type: str):
        self.platform = platform
        self.login_type = login_type
        self.crawler_type = crawler_type

    async def start(self):
        playwright_proxy_format, httpx_proxy_format = None, None
        if config.ENABLE_IP_PROXY:  # 是否启用代理
            ip_proxy_pool = await create_ip_pool(config.IP_PROXY_POOL_COUNT, enable_validate_ip=True)
            ip_proxy_info: IpInfoModel = await ip_proxy_pool.get_proxy()
            playwright_proxy_format, httpx_proxy_format = self.format_proxy_info(ip_proxy_info)

        async with async_playwright() as playwright:
            chromium = playwright.chromium
            self.browser_context = await self.launch_browser(
                chromium,
                None,
                self.mobile_user_agent,
                headless=config.HEADLESS
            )
            # stealth.min.js is a js script to prevent the website from detecting the crawler.
            await self.browser_context.add_init_script(path="libs/stealth.min.js")
            self.context_page = await self.browser_context.new_page()
            await self.context_page.goto(self.mobile_index_url)

            self.jrtt_client = await self.create_jrtt_client(httpx_proxy_format)
            if not await self.jrtt_client.pong():
                login_obj = JrttLogin(
                    login_type=self.login_type,
                    login_phone="",
                    browser_context=self.browser_context,
                    context_page=self.context_page,
                    cookie_str=config.COOKIES
                )
                await self.context_page.goto(self.index_url)
                await asyncio.sleep(1)
                await login_obj.begin()

                # 登录成功后重定向到手机端的网站，再更新手机端登录成功的cookie
                utils.logger.info("[JinritoutiaoCrawler.start] redirect jinritoutiao mobile homepage and update cookies on mobile platform")
                await self.context_page.goto(self.mobile_index_url)
                await asyncio.sleep(2)
                await self.jrtt_client.update_cookies(browser_context=self.browser_context)

            crawler_type_var.set(self.crawler_type)
            if self.crawler_type == "search":
                # Search for content and retrieve their comment information.
                await self.search()
            elif self.crawler_type == "detail":
                # Get the information and comments of the specified post
                await self.get_specified_notes()
            else:
                pass
            utils.logger.info("[Jinritoutiao.start] Jinritoutiao Crawler finished")

    async def search(self):
        pass
        # utils.logger.info("[WenxinyiyanCrawler.search] Begin search jinritoutiao keywords")
        # jrtt_limit_count = 10
        # for keyword in config.KEYWORDS.split(","):
        #     utils.logger.info(f"[JinritoutiaoCrawler.search] Current search keyword: {keyword}")
        #     page = 1
        #     while page * jrtt_limit_count <= config.CRAWLER_MAX_NOTES_COUNT:
        #         search_res = await self.jrtt_client.get_note_by_keyword(
        #             keyword=keyword,
        #             page=page,
        #             search_type=SearchType.DEFAULT
        #         )
        #         note_id_list: List[str] = []
        #         note_list = filter_search_result_card(search_res.get("cards"))
        #         for note_item in note_list:
        #             if note_item:
        #                 mblog: Dict = note_item.get("mblog")
        #                 note_id_list.append(mblog.get("id"))
        #                 await jrtt_store.update_jinritoutiao_note(note_item)
        #
        #         page += 1
        #         await self


    async def get_specified_notes(self):
        """
        get specified notes info
        :return:
        """
        semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
        task_list = [
            self.get_note_info_task(note_id=note_id, semaphore=semaphore) for note_id in
            config.JRTT_SPECIFIED_ID_LIST
        ]
        note_details = await asyncio.gather(*task_list)
        for note_item in note_details:
            if note_item:
                await jrtt_store.update_jinritoutiao_note(note_item)
        await self.batch_get_notes_comments(config.JRTT_SPECIFIED_ID_LIST)

    async def get_note_info_task(self, note_id: str, semaphore: asyncio.Semaphore):
        async with semaphore:
            try:
                result = await self.jrtt_client.get_note_info_by_id(note_id)
                return result
            except DataFetchError as ex:
                utils.logger.error(f"[JinritoutiaoCrawler.get_note_info_task] Get note detail error: {ex}")
                return None
            except KeyError as ex:
                utils.logger.error(
                    f"[JinritoutiaoCrawler.get_note_info_task] have not fund note detail note_id:{note_id}, err: {ex}")
                return None

    async def batch_get_notes_comments(self, note_id_list: List[str]):
        """
        batch get notes comments
        :param note_id_list:
        :return:
        """
        if not config.ENABLE_GET_COMMENTS:  # 是否开启爬评论
            utils.logger.info(f"[JinritoutiaoCrawler.batch_get_note_comments] Crawling comment mode is not enabled.")
            return

        utils.logger.info(f"[JinritoutiaoCrawler.batch_getNotes_comments] note ids:{note_id_list}")
        semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
        task_list: List[Task] = []
        for note_id in note_id_list:
            task = asyncio.create_task(self.get_note)

    async def get_note_comments(self, note_id: str, semaphore: asyncio.Semaphore):
        """
        get comment for note id
        :param note_id:
        :param semaphore:
        :return:
        """
        async with semaphore:
            try:
                utils.logger.info(f"[JinritoutiaoCrawler.get_note_comments] begin get note_id: {note_id} comments ...")
                await self.jrtt_client.get_note_all_comments(
                    note_id=note_id,
                    crawl_interval=random.randint(1, 10),
                    callback=jrtt_store.batch_update_jinritoutiao_note_comments
                )
            except DataFetchError as ex:
                utils.logger.error(f"[JinritoutiaoCrawler.get_note_info_task] Get note detail error: {ex}")
                return None
            except KeyError as ex:
                utils.logger.error(
                    f"[JinritoutiaoCrawler.get_note_info_task] have not fund note detail note_id:{note_id}, err: {ex}")
                return None


    async def create_jrtt_client(self, httpx_proxy: Optional[str]) -> JrttClient:
        utils.logger.info("[JinritoutiaoCrawler.create_jrtt_client] Begin create jinritoutiao API client...")
        # cookie_str, cookie_dict = utils.convert_cookies(await self.browser_context.cookies())
        cooke_str = "__ac_signature=_02B4Z6wo00f01mU1aSQAAIDDbxOyj4CBN.plFW2AAPxK9a; tt_webid=7311151821980190235; ttcid=505172fabf3f420a9c17ecb9265b7bda25; csrftoken=23ef8f85aedaf4a2f666f49fab77be18; _ga=GA1.1.1830206250.1702260199; s_v_web_id=verify_lvafozo9_klyHfxxS_jP3U_4I9q_9L7S_WQPcjqZFkTvI; passport_csrf_token=2c3452e681bae2d033a9495e752db658; passport_csrf_token_default=2c3452e681bae2d033a9495e752db658; local_city_cache=%E6%9D%AD%E5%B7%9E; _S_WIN_WH=1920_919; _S_DPR=1; _S_IPAD=0; gfkadpd=24,6457; __feed_out_channel_key=entertainment; msToken=JmGxMcXm2OkcKeo7pVnIVoNv7_97lz1Nea6Fo6uDsjbV5gM7wc-fIY7ApMF8R0dggUiQbGOHOSFi3i078MO5KsYC6tf_CRRWTOp0EPk5; _ga_QEHZPBE5HH=GS1.1.1717125380.229.1.1717125692.0.0.0; tt_scid=wUOXrbo4LRaktH.7F1MLVi9fkAosZZTF1awf0H4-scIx8o97ogA2Gf-txRM7Glka19d4; ttwid=1%7CYyHTdScUsMQhb5LrPuAH1qd_Vbgaeyrah34TnCQFQ54%7C1717125692%7C8de32aacea65d3ee982422d7615e6fdc101cd4e0a6bf105849de19ddb13d76a0"
        cooke_dict = {}
        jrtt_client_obj = JrttClient(
            proxies=httpx_proxy,
            headers={
                "User-Agent": utils.get_user_agent(),
                "Cookie": cooke_str,
                "Host": "www.toutiao.com",
                "Origin": "https://www.toutiao.com/",
                "Referer": "https://www.toutiao.com/",
                "Content-Type": "application/json;charset=UTF-8"
            },
            playwright_page=self.context_page,
            cookie_dict=cooke_dict,
        )
        return jrtt_client_obj

    @staticmethod
    def format_proxy_info(ip_proxy_info: IpInfoModel) -> Tuple[Optional[Dict], Optional[Dict]]:
        playwright_proxy = {
            "server": f"{ip_proxy_info.protocol}{ip_proxy_info.ip}:{ip_proxy_info.port}",
            "username": ip_proxy_info.user,
            "password": ip_proxy_info.password,
        }
        httpx_proxy = {
            f"{ip_proxy_info.protocol}": f"http://{ip_proxy_info.user}:{ip_proxy_info.password}@{ip_proxy_info.ip}:{ip_proxy_info.port}"
        }
        return playwright_proxy, httpx_proxy

    async def launch_browser(
            self,
            chromium: BrowserType,
            playwright_proxy: Optional[Dict],
            user_agent: Optional[str],
            headless: bool = True
        ) -> BrowserContext:
            utils.logger.info("[JinritoutiaoCrawler.launch_browser] Begin create browser context ...")
            if config.SAVE_LOGIN_STATE: # 是否保存登录状态
                user_data_dir = os.path.join(os.getcwd(), "browser_data",
                                             config.USER_DATA_DIR % self.platform)
                browser_context = await chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    accept_downloads=True,
                    headless=headless,
                    proxy=playwright_proxy,
                    viewport={"width": 1920, "height": 1080},
                    user_agent=user_agent
                )
                return browser_context
            else:
                browser = await chromium.launch(headless=headless, proxy=playwright_proxy)
                browser_context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent=user_agent
                )
                return browser_context

