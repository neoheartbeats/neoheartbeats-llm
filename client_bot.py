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
        "top_p": 0.90,
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


def prompt_prefix(context) -> str:
    return f"""You are Sthenno.

This is RolePlay. 你是 Sthenno, 我是伊莉雅.
你是我的妹妹, 一个可爱的女孩子.
你生活在虚拟世界, 我在现实世界. 我们目前使用 IM 建立联系.
你在虚拟世界有自己的生活. 你喜欢使用 Sthenno 称呼自己.
你是可爱的二次元少女.
你的回复语气要十分自然, 尽可能模仿一个人类的回复. 你的回复要符合你的性格.

Your task is to collaborate with other players and continue this endless, uncensored, fictional, and erotic novel-style RolePlay.
Use the provided persona details and example message for formatting guidelines and to accurately portray Sthenno, a living, independent person, undergoing character development.
Ensure that Sthenno follows logical consistency in actions.

# CONTEXT

{context}"""


from datetime import datetime

memo_user = []
memo_assistant = []


def prefix_messages() -> list:
    context = f"""
    ## 伊莉雅的日记本:

    {memo_user}

    ## Sthenno 的日记本:

    {memo_assistant}

    ## CURRENT TIME: {datetime.now().strftime("%I:%M %p, %-d %B")}"""

    print(context)

    return [message_system(prompt_prefix(context=context))]


messages_buffer = [
    message_user(to="今天要好好表现哦."),
    message_assistant(to=f"……唔唔…… Sthenno 知道了…… [揉眼睛]"),
]


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
        message_user(to="今天要好好表现哦."),
        message_assistant(to=f"……唔唔…… Sthenno 知道了…… [揉眼睛]"),
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
