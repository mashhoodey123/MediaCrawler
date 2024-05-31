'''
File Name: jrtt_store_impl
Create File Time: 2024/5/28 13:57
File Create By Author: Yang Guanqun
Email: yangguanqunit@outlook.com
'''
import csv
import pathlib
from typing import Dict

import aiofiles

from base.base_crawler import AbstractStore
from tools import utils
from var import crawler_type_var  # 类似全局变量的东西
from tortoise.contrib.pydantic import pydantic_model_creator

class JinritoutiaoCsvStoreImplement(AbstractStore):
    csv_store_path: str = "data/jinritoutiao"

    def make_save_file_name(self, store_type: str) -> str:
        """
        make save file name by store type
        Args:
            store_type: contents or comments

        Returns: eg: data/bilibili/search_comments_20240114.csv ...

        """
        return f"{self.csv_store_path}/{crawler_type_var.get()}_{store_type}_{utils.get_current_date()}.csv"

    async def save_data_to_csv(self, save_item: Dict, store_type: str):
        """
        Below is a simple way to save it in CSV format.
        Args:
            save_item:  save content dict info
            store_type: Save type contains content and comments（contents | comments）

        Returns: no returns

        """
        pathlib.Path(self.csv_store_path).mkdir(parents=True, exist_ok=True)
        save_file_name = self.make_save_file_name(store_type=store_type)
        async with aiofiles.open(save_file_name, mode="a+", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            if await f.tell() == 0:
                await writer.writerow(save_item.keys())
            await writer.writerow(save_item.values())

    async def store_content(self, content_item: Dict):
        """
        Jinritoutiao content CSV storage implementation
        Args:
            content_item: note item dict

        Returns:

        """
        await self.save_data_to_csv(save_item=content_item, store_type="content")

    async def store_comment(self, comment_item: Dict):
        """
        Jinritoutiao comment CSV storage implementation
        Args:
            comment_item: comment item dict

        Returns:

        """
        await self.save_data_to_csv(save_item=comment_item, store_type="comment")


class JinritoutiaoDbStoreImplement(AbstractStore):
    async def store_content(self, content_item: Dict):
        """
        Jinritoutiao content DB storage implementation
        Args:
            content_item: content item dict

        Returns:

        """
        from .jrtt_store_db_types import JinritoutiaoNote
        note_id = content_item.get("note_id")
        if not await JinritoutiaoNote.filter(note_id=note_id).exists():
            content_item["add_ts"] = utils.get_current_timestamp()
            jinritoutiao_note_pydantic = pydantic_model_creator(JinritoutiaoNote, name="JinritoutiaoNoteCreate", exclude=('id',))
            jinritoutiao_data = jinritoutiao_note_pydantic(**content_item)
            jinritoutiao_note_pydantic.model_validate(jinritoutiao_data)
            await JinritoutiaoNote.create(**jinritoutiao_data.model_dump())
        else:
            jinritoutiao_note_pydantic = pydantic_model_creator(JinritoutiaoNote, name="JinritoutiaoNoteUpdate",
                                                                exclude=('id', 'add_ts'))
            jinritoutiao_data = jinritoutiao_note_pydantic(**content_item)
            jinritoutiao_note_pydantic.model_validate(jinritoutiao_data)
            await JinritoutiaoNote.filter(note_id=note_id).update(**jinritoutiao_data.model_dump())

    async def store_comment(self, comment_item: Dict):
        """
        Jinritoutiao content DB storage implementation
        Args:
            comment_item: comment item dict

        Returns:

        """
        from .jrtt_store_db_types import JinritoutiaoComment
        comment_id = comment_item.get("comment_id")
        if not await JinritoutiaoComment.filter(comment_id=comment_id).exists():
            comment_item["add_ts"] = utils.get_current_timestamp()
            comment_pydantic = pydantic_model_creator(JinritoutiaoComment, name="JinrotoutiaoNoteCommentCreate",
                                                      exclude=('id',))
            comment_data = comment_pydantic(**comment_item)
            comment_pydantic.model_validate(comment_data)
            await JinritoutiaoComment.create(**comment_data.model_dump())
        else:
            comment_pydantic = pydantic_model_creator(JinritoutiaoComment, name="JinritoutiaoNoteCommentUpdate",
                                                      exclude=('id', 'add_ts'))
            comment_data = comment_pydantic(**comment_item)
            comment_pydantic.model_validate(comment_data)
            await JinritoutiaoComment.filter(comment_id=comment_id).update(**comment_data.model_dump())
