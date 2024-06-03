'''
File Name: jrtt_store_db_types
Create File Time: 2024/5/28 10:48
File Create By Author: Yang Guanqun
Email: yangguanqunit@outlook.com
'''

"""Object Relational Mapping(对象关系映射)，把对象当作数据库来使用"""
from tortoise import fields
from tortoise.models import Model


class JinritoutiaoBaseModel(Model):
    id = fields.IntField(pk=True, autoincrement=True, description="自增ID")
    user_id = fields.CharField(null=True, max_length=64, description="user id")
    nickname = fields.CharField(null=True, max_length=64, description="nickname")
    avatar = fields.CharField(null=True, max_length=255, description="touxiang")
    gender = fields.CharField(null=True, max_length=12, description="gender")
    profile_url = fields.CharField(null=True, max_length=255, description="user homepage")
    ip_location = fields.CharField(null=True, max_length=32, description="user location")
    add_ts = fields.BigIntField(description="timestamp")
    last_modify_ts = fields.BigIntField(description="last modify timestamp")

    class Meta:
        abstract = True


class JinritoutiaoNote(JinritoutiaoBaseModel):
    note_id = fields.CharField(max_length=64, index=True, description="note id")  # 帖子ID
    content = fields.TextField(null=True, description="note content")  # 帖子正文内容
    create_time = fields.BigIntField(description="note timestamp", index=True)  # 帖子发布时间戳
    create_data_time = fields.CharField(max_length=32, description="note date", index=True)  # 帖子发布日期 index 可能是按某种顺序存储？
    liked_count = fields.CharField(null=True, max_length=16, description="liked count")  # 帖子点赞数
    comments_count = fields.CharField(null=True, max_length=16, description="comments count")  # 帖子评论数量
    shared_count = fields.CharField(null=True, max_length=16, description="transmits count")  # 帖子转发数量
    note_url = fields.CharField(null=True, max_length=512, description="note url")  # 帖子详情URL

    class Meta:
        table = "jinritoutiao_note"
        table_description = "今日头条帖子"

    def __str__(self):
        return f"{self.note_id}"


class JinritoutiaoComment(JinritoutiaoBaseModel):
    note_id = fields.CharField(max_length=64, index=True, description="note id")  # 帖子id  index设置为True时，将为该字段创建数据库索引，这有助于加快查询速度
    comment_id = fields.CharField(max_length=64, index=True, description="comment id")  # 评论id
    user_id = fields.CharField(max_length=64, description="user id")
    user_name = fields.TextField(null=False, description="user name")
    content = fields.TextField(null=True, description="comment content")  # 评论内容
    create_time = fields.BigIntField(description="comment timestamp")  # 评论时间戳
    # create_data_time = fields.CharField(max_length=32, description="comment date", index=True)  # 评论日期 index 可能是按某种顺序存储？
    # comment_like_count = fields.CharField(max_length=16, description="like count")  # 评论点赞数
    # sub_comment_count = fields.CharField(max_length=16, description="sub comment count")  # 评论回复数

    class Meta:
        table = "jinritoutiao_note_comment"
        table_description = "今日头条帖子评论"

    def __str__(self):
        return f"{self.comment_id}"


class JinritoutiaoReply(JinritoutiaoBaseModel):
    note_id = fields.CharField(max_length=64, index=True, description="note id")
    comment_id = fields.CharField(max_length=64, index=True, description="comment id")
    reply_id = fields.CharField(max_length=64, index=True, description="reply id")
    user_id = fields.CharField(max_length=64, description="user id")
    user_name = fields.TextField(null=False, description="user name")
    content = fields.TextField(null=True, description="reply content")
    create_time = fields.BigIntField(description="reply timestamp")

    class Meta:
        table = "jinritoutiao_note_comment_reply"
        table_description = "今日头条评论回复"

    def __str__(self):
        return f"{self.reply_id}"
