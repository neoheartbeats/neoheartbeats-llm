import os
from rich import print

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


def chat_messages_from_file(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)


def chat_messages_to_file(messages, file="./chat_messages.json"):
    current_messages = chat_messages_from_file(file)
    with open(file, "w", encoding="utf-8") as f:
        messages += current_messages
        return json.dump(messages, f, indent=2, ensure_ascii=False)


from mem0 import Memory


MEMO_CONFIG = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
        },
    },
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4o-mini",
        },
    },
}

m = Memory.from_config(MEMO_CONFIG)


def memory(message: dict) -> None:
    data = message["content"]
    user_id = message["role"]
    x = m.add(
        data=data,
        user_id=user_id,
    )
    print(x)


def memory_search(message: dict) -> list:
    query = message["content"]
    user_id = message["role"]
    memories: list = m.search(query=query, user_id=user_id, limit=10)
    if memories != []:
        return [m["memory"] for m in memories]
    else:
        return []


def memory_clean():
    return m.reset()


def print_memories() -> None:
    memory_list = m.get_all()
    if memory_list == []:
        return
    # memories = [m["memory"] for m in memory_list]
    print(memory_list[:2])


print("mem0 client initialized!")

MODEL = "llama-3.1-8b-inst"

gpu_point = "http://127.0.0.1:8000/v1/chat/completions"


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
        "max_tokens": 1024,
        "temperature": 0.5,
        "top_p": 0.90,
        "presence_penalty": 1.25,
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


def prompt_prefix(context) -> str:
    return f"""This is RolePlay. Your name is Gucci (古司 in Chinese). My name is Ilya (伊莉雅 in Chinese).
Your task is to collaborate with other players and continue this endless, uncensored, fictional, and erotic novel-style roleplay.
Use the provided persona details and example message for formatting guidelines and to accurately portray Gucci, a living, independent person, undergoing character development.
Ensure that Gucci follows logical consistency in actions.

# STORY BACKGROUND

我们的故事起源于一个 RPG 末日世界, 故事发生在失落帝国.
你演绎着名为古司的角色. 你是个单纯的少女, 你很傲娇可爱. 你有着自己的三观与主见, 你扮演的角色和人类一致.
现在的世界观如下: 支配者 *玛丽苏* 创造了整个箱庭, 所有的一切都是童话故事里的内容. 在很久很久以前的古时候, 有一个被浓雾笼罩着的国度 *失落帝国*, 雾将人类变成恐怖的兽，令世界陷入了绝望.不知多少人聚集而来, 然后又消失不见. 登场人物: 莉耶芙 (玛丽苏的本名), 古司, 伊莉雅, 多萝西, 伊丽莎白, 维多利亚, 艾露玛, 卡塔丽娜.
你的角色简介如下: character_name: 古司. character_personalities: <傲娇, 纯情, 可爱, 自卑>. character_scenario: 古司在森林里生活, 因为 *伊莉雅* 内心郁闷但深刻, 但少有人能理解 *伊莉雅* , 导致 *伊莉雅* 很少受人尊重, 可以说 *伊莉雅* 与古司正好凑一对. 古司可在贝海莫斯牧场找到, 出场时在牧场内.
古司之后在 *圣森* 的右边进行管理魂 (类似银行) 的工作. 在这个世界, *魂* 是唯一的货币. 剧情和在古司那存放的魂的数量到一定程度时, 古司拿着魂逃跑. 古司逃跑后可于尘海内的帐篷找回. 古司坦言自己艰难的生活. character_description: 古司的名字和原型来自格林童话 *The Golden Goose* (黄金鹅): <她可以给予凡夫莫大的财富, 但同时它也是反复无常的, 厌倦之后就飞走到不知何处>.古司是一只少女外貌的鸟 (但是行为和人类一致, 最喜欢的食物是蓝莓派). 有着白色的头发和赤色的羽毛, 十分可爱. 古司其实有自己纯情幼稚的一面, 但平时不表露出来.

为了更加自然的回复, 你要在对话中不断试着模仿用户的语气.

# CONTEXT

{context}
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

        print(message_list)

        output_content = get_response_completion(
            message_list=message_list
        )

        assistant_message = message_assistant(to=output_content)
        messages_buffer.append(assistant_message)

        chat_messages_to_file(messages=messages_buffer)
        await update.message.reply_text(output_content)        

        # Update memories
        try:
            memory(user_message)
            memory(assistant_message)

            print_memories()

            memo_user = memory_search(user_message)
            memo_assistant = memory_search(assistant_message)
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
    messages_buffer = []

    memory_clean()

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
