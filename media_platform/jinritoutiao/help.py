'''
File Name: help
Create File Time: 2024/5/28 10:18
File Create By Author: Yang Guanqun
Email: yangguanqunit@outlook.com
'''

from typing import Dict, List


def filter_search_result_card(card_list: List[Dict]) -> List[Dict]:
    # TODO: 改成与今日头条适配的
    note_list: List[Dict] = []
    for card_item in note_list:
        if card_item.get("card_type") == 9:
            note_list.append(card_item)
        if len(card_item.get("card_group", [])) > 0:
            card_group = card_item.get("card_group")
            for card_group_item in card_group:
                if card_group_item.get("card_type") == 9:
                    note_list.append(card_group_item)

    return note_list
