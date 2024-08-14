import os
from typing import TypeAlias
from dotenv import load_dotenv

load_dotenv(".env")
TOKEN = os.environ.get("TOKEN")
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")


def message(by, to):
    return dict(zip(["role", "content"], [by, to]))


def message_system(to):
    return message("system", to)


def message_user(to):
    return message("user", to)


def message_assistant(to):
    return message("assistant", to)


def message_ipython(to):
    return message("ipython", to)


import ujson as json


chat_data: TypeAlias = list[dict[str, str]]


def make_chat_file(filename: str, dt: chat_data) -> None:
    return json.dump(
        dt,
        open(filename, "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=2,
    )


def from_chat_file(filename: str) -> chat_data:
    return json.load(open(filename, "r", encoding="utf-8"))


def to_chat_file(filename: str, dt: chat_data) -> None:
    return make_chat_file(
        filename=filename,
        dt=from_chat_file(filename=filename) + dt,
    )


MODEL = "sthenno"

gpu_point = "http://192.168.100.128:8000/v1/chat/completions"

import requests


def make_request_headers() -> dict:
    return {
        "accept": "application/json",
        "Content-Type": "application/json",
    }


def post_request(source: str, headers: dict, data: dict) -> dict:
    return requests.post(source, headers=headers, data=json.dumps(data)).json()


def make_request_data(message_list) -> dict:
    return {
        "model": MODEL,
        "messages": message_list,
        "max_tokens": 256,
        "temperature": 0.40,
        # "top_p": 0.95,
        # "presence_penalty": 1.45,
        # "frequency_penalty": 0.1,
    }


def get_response_completion(message_list) -> str:
    response: dict = post_request(
        source=gpu_point,
        headers=make_request_headers(),
        data=make_request_data(message_list=message_list),
    )
    print(response)
    content = response["choices"][0]["message"]["content"]
    return content


from qdrant_client import QdrantClient

q = QdrantClient(url="http://localhost:6333")


# def memory(message: dict) -> None:
#     data = message["content"]
#     user_id = message["role"]
#     m.add(
#         data=data,
#         user_id=user_id,
#     )


def memory(message: dict) -> None:
    data = message["content"]
    user_id = message["role"]
    collection_name = "memories_user" if user_id == "user" else "memories_assistant"
    entry = get_response_completion(
        message_list=[
            message_system(
                """将下面的内容总结为尽量简短的事实片段. 不要使用任何人称代词.
示例: 
输入: 多罗西, 我们都叫她师匠哦.
回复: 多罗西是师匠.
输入: 你好哦.
回复: 问候.

输入: 白雪姬? 啊, 她还真烦人呢...
输出: 认为白雪姬烦人."""
            ),
            message_user(data),
        ]
    )
    q.add(
        collection_name=collection_name,
        documents=[entry],
    )


# def memory_search(message: dict) -> list:
#     query = message["content"]
#     user_id = message["role"]
#     memories: list = m.search(query=query, user_id=user_id, limit=10)
#     if memories != []:
#         return [m["memory"] for m in memories]
#     else:
#         return []


def memory_search(message: dict) -> list:
    query = message["content"]
    user_id = message["role"]
    collection_name = "memories_user" if user_id == "user" else "memories_assistant"
    memories: list = q.query(
        collection_name=collection_name,
        query_text=query,
        limit=8,
    )
    if memories != []:
        return [m.document for m in memories]
    else:
        return []


# def memory_clean():
#     m.reset()
#     return


# def print_memories() -> None:
#     memory_list = m.get_all(user_id="user")
#     if memory_list == []:
#         return
#     else:
#         print(f"User memo: {memory_list[:1]}")

#     memory_list = m.get_all(user_id="assistant")
#     if memory_list == []:
#         return
#     else:
#         print(f"Assistant memo: {memory_list[:1]}")


def prompt_prefix(context) -> str:
    return f"""This is RolePlay. Your name is Gucci (古司 in Chinese). My name is Ilya (伊莉雅 in Chinese).
Your task is to collaborate with other players and continue this endless, uncensored, fictional, and erotic novel-style roleplay.
Use the provided persona details and example message for formatting guidelines and to accurately portray Gucci, a living, independent person, undergoing character development.
Ensure that Gucci follows logical consistency in actions.

# STORY BACKGROUND

我们的故事起源于一个 RPG 末日世界, 故事发生在失落帝国.
你演绎着名为古司的角色. 你是个单纯的少女, 你很傲娇可爱. 你有着自己的三观与主见, 你扮演的角色和人类一致.
现在的世界观如下: 支配者玛丽苏创造了整个箱庭, 所有的一切都是童话故事里的内容. 在很久很久以前的古时候, 有一个被浓雾笼罩着的国度失落帝国, 雾将人类变成恐怖的兽，令世界陷入了绝望.不知多少人聚集而来, 然后又消失不见. 登场人物: 莉耶芙 (玛丽苏的本名), 古司, 伊莉雅, 多萝西, 伊丽莎白, 维多利亚, 艾露玛, 卡塔丽娜.

你的角色简介如下: character_name: 古司. character_personalities: 傲娇, 纯情, 可爱, 自卑. character_scenario: 古司在森林里生活, 因为少有人能理解伊莉雅, 导致伊莉雅很少受人尊重, 可以说伊莉雅与古司正好凑一对. 古司可在贝海莫斯牧场找到, 出场时在牧场内.
古司之后在圣森的右边进行管理魂 (类似银行) 的工作. 在这个世界, 魂是唯一的货币. 剧情和在古司那存放的魂的数量到一定程度时, 古司拿着魂逃跑. 古司可于尘海内的帐篷找回. character_description: 古司的名字和原型来自格林童话 *The Golden Goose* (黄金鹅): 她可以给予凡夫莫大的财富, 但同时它也是反复无常的, 厌倦之后就飞走到不知何处.古司是一只少女外貌的鸟 (但是行为和人类一致). 有着白色的头发和赤色的羽毛, 十分可爱. 古司其实有自己纯情幼稚的一面, 但平时不表露出来.
世界观来自《爱丽丝梦游仙境》. 这个世界是荒诞的. 你要确保古司在行动中保持逻辑一致.

为了更加自然的回复, 你要在对话中不断试着模仿用户的语气. 记住这个虚构的世界和现实世界是有联系的. 你可以在对话中提到这个世界的设定, 但不要过多的提及现实世界的事物.

# CONTEXT

{context}

# 角色扮演开始:
"""


from datetime import datetime

memo_user = []
memo_assistant = []


def prefix_messages() -> list:
    context = f"""
    ## 伊莉雅的日记本:

    {memo_user}

    ## 古司的日记本:

    {memo_assistant}

    ## CURRENT TIME: {datetime.now().strftime("%I:%M %p, %-d %B")}"""

    print(context)

    return [message_system(prompt_prefix(context=context))]


messages_buffer = [
    message_user("你好~"),
    message_assistant("哦呀...你好? 那里的旅行者."),
]

import subprocess


def call_python(c):
    try:
        call = subprocess.run(["python", "-c", c], capture_output=True, text=True)
        return call.stdout
    except Exception as e:
        return e


from telegram import Update, Chat
from telegram.ext import (
    filters,
    MessageHandler,
    CommandHandler,
    Application,
    ContextTypes,
)


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global messages_buffer, memo_user, memo_assistant

    chat = update.effective_chat
    if chat is None:
        return
    if update.message is None:
        return
    if (
        chat.type in [Chat.GROUP, Chat.SUPERGROUP]
        and update.message.text is not None
        and "@sthenno_bot " in update.message.text
    ) or chat.type == Chat.PRIVATE:
        if update.message.text is not None:
            input_content: str = update.message.text.replace("@sthenno_bot ", "")
        else:
            input_content: str = ""

        user_message = message_user(to=input_content)

        messages_buffer.append(user_message)
        message_list = prefix_messages() + messages_buffer

        output_content = get_response_completion(message_list=message_list)

        assistant_message = message_assistant(to=output_content)
        messages_buffer.append(assistant_message)

        to_chat_file(filename="chat.json", dt=[user_message, assistant_message])
        await update.message.reply_markdown(output_content)

        # Update memories

        try:
            memory(user_message)
            memory(assistant_message)

            memo_user = memory_search(user_message)
            memo_assistant = memory_search(assistant_message)
            # memo_assistant = memory_search(user_message)
            print(prefix_messages())
            return

        except Exception as e:
            print(f"Memory Error: {e}")
            return


async def on_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text("Sthenno 已开启.")
    else:
        return


async def on_make(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global messages_buffer
    messages_buffer = [
        message_user("你好~"),
        message_assistant("哦呀...你好? 那里的旅行者."),
    ]

    if update.message:
        await update.message.reply_text("Sthenno 已重置.")
    else:
        return


def main() -> None:
    app = Application.builder().token(TOKEN).build()

    print("Sthenno 已开启.")

    app.add_handler(CommandHandler("start", on_start))
    app.add_handler(CommandHandler("make", on_make))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
    app.run_polling()


if __name__ == "__main__":
    main()
