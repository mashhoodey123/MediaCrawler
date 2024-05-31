'''
File Name: __init__.py
Create File Time: 2024/5/28 10:38
File Create By Author: Yang Guanqun
Email: yangguanqunit@outlook.com
'''

from typing import List

import config

from .jrtt_store_db_types import *
from .jrtt_store_impl import *


class JinritoutiaostoreFactory:
    STORES = {
        "csv": JinritoutiaoCsvStoreImplement,
        "db": JinritoutiaoDbStoreImplement,
        "json": None
    }

    @staticmethod
    def create_store() -> AbstractStore:
        store_class = JinritoutiaostoreFactory.STORES.get(config.SAVE_DATA_OPTION)
        if not store_class:
            raise ValueError(
                "[JinritoutiaoFactory.create_store] Invalid save option only supported csv or db or json ..."
            )
        return store_class()


async def update_jinritoutiao_note(note_item: Dict):
    blog: Dict = note_item.get("blog")
    user_info: Dict = blog.get("user")
    note_id = blog.get("id")
    save_content_item = {
        # blog info
        "note_id": None,

        # user info
        "user_id": None
    }
    utils.logger.info(
        f"[store.jinritoutiao.udpate_jinritoutiao_note] jinritoutiao note id:{note_id}, title:{save_content_item.get('content')[:24]} ..."
    )
    await JinritoutiaostoreFactory.create_store().store_content(content_item=save_content_item)


async def batch_update_jinritoutiao_note_comments(note_id: str, comments: List[Dict]):
    if not comments:
        return
    for comment_item in comments:
        pass

async def update_jinritoutiao_note_comment(note_id: str, comment_item: Dict):
    comment_id: str = str(comment_item.get("id"))
    user_info: Dict = comment_item.get("user")
    save_comment_item = {
        # comment info
        "comment_id": None,

        # user info
        "user_id": None
    }
    utils.logger.info(
        f"[store.jinritoutiao.update_jinritoutiao_note_comment] Jinritoutiao note comment: {comment_id}, content: {save_comment_item.get('content', '')[:24]} ..."
    )
    await JinritoutiaostoreFactory.create_store().store_comment(comment_item=save_comment_item)

