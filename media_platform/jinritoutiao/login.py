'''
File Name: login
Create File Time: 2024/5/27 16:44
File Create By Author: Yang Guanqun
Email: yangguanqunit@outlook.com
'''
import asyncio
from typing import Optional

from playwright.async_api import BrowserContext, Page
from base.base_crawler import AbstractLogin
from tools import utils

class JrttLogin(AbstractLogin):
    def __init__(self,
                 login_type: str,
                 browser_context: BrowserContext,
                 context_page: Page,
                 login_phone: Optional[str] = "",
                 cookie_str: str = ""
                 ):
        self.login_type = login_type
        self.browser_context = browser_context
        self.context_page = context_page
        self.login_phone = login_phone
        self.cookie_str = cookie_str

    async def begin(self):
        utils.logger.info("[Jinritoutiao.begin] Begin login jinritoutiao...")
        if self.login_type == "qrcode":
            await self.login_by_qrcode()
        elif self.login_type == "phone":
            await self.login_by_mobile()
        elif self.login_type == "cookie":
            await self.login_by_cookies()
        else:
            raise ValueError(
                "[Jinritoutiao.begin] Invalid Login Type Currently only supported qrcode or phone or cookie ..."
            )


    async def popup_login_dialog(self):
        dialog_selector = "xpath=//div[@class='woo-modal-main']"
        try:
            await self.context_page.wait_for_selector(dialog_selector, timeout=1000*4)
        except Exception as e:
            utils.logger.error(f"[JrttLogin.popup_login_dialog] login dialog box does not pop up automatically, error: {e}")
            utils.logger.info(f"[JrttLogin.popup_login_dialog] login dialog box does not pop up automatically, we will manually click the login button")

            # 向下滚动1000像素
            await self.context_page.mouse.wheel(0, 500)
            await asyncio.sleep(0.5)

            try:
                login_button_ele = self.context_page.locator(
                    "xpath=//*[@id='root']/div/div[3]/div[2]/a",
                )
                await login_button_ele.click()
                await asyncio.sleep(0.5)
            except Exception as e:
                utils.logger.info(f"[JrttLogin.popup_login_dialog] manually click the login button failed maybe login dialog Appear: {e}")

    async def login_by_qrcode(self):
        utils.logger.info("[JinritoutiaoLogin.login_by_qrcode] Begin login jinritoutiao by qrcode ...")
        await self.popup_login_dialog()





    async def login_by_mobile(self):
        pass

    async def login_by_cookies(self):
        pass