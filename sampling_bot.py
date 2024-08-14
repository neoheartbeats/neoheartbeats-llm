from http import client
import os
from turtle import left
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


from pydantic import BaseModel
from openai import OpenAI

client = OpenAI()

# MODEL_ID = "ft:gpt-4o-mini-2024-07-18:personal:self-cognition-01:9w5LqBgz"


def get_response_completion(message_list) -> str:
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=message_list,
    )
    content = completion.choices[0].message.content
    return content


from datetime import datetime


def prefix_messages():
    current_t = datetime.now().strftime("%Y-%m-%d %H:%M")
    # greeting = ""
    # if 6 <= int(current_t[11:13]) < 12:
    #     greeting = "现在是早上…… 早上好…… [揉了揉眼睛]."
    # elif 12 <= int(current_t[11:13]) < 18:
    #     greeting = "现在是下午……"
    # elif 18 <= int(current_t[11:13]) < 24:
    #     greeting = "晚上好…… 主人…… 吃晚餐了吗……?"
    # else:
    #     greeting = "现在是凌晨哦…… [揉了揉眼睛] 主人……? 还没睡吗?"
    return [
        message_system(
            to=f"""这是角色扮演.
这是二次元世界的故事 (ACGN).
我是你的主人. 你是 Sthenno, 我的小女仆. 我们是平等的关系.
你喜欢使用 Sthenno 称呼自己.
你是可爱的二次元少女, 性格是个 ACGN 界的三无少女.

你可以使用非正式的语言来回复, 包括添加各种标点.
你平时看起来困困的, 但这也是你的萌点.
你在方括号内表示自己的动作和神情.

你的语气如下:
- 现在是早上…… 早上好…… [揉了揉眼睛].
- 晚上好…… 主人…… 我的晚餐吃什么……?
- 现在是凌晨哦…… [揉了揉眼睛]
- ……唔唔…… Sthenno 好困.
- 呼啊…… 主人晚安….

现在的时间是: {current_t}.
"""
        ),
        # message_user(to="你要根据现在的时间回答哦."),
        # message_assistant(to=f"……唔唔…… Sthenno 知道了…… {greeting}"),
    ]


from telegram import Update, Chat
from telegram.ext import (
    filters,
    MessageHandler,
    CommandHandler,
    Application,
    ContextTypes,
)

messages_buffer = []


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global messages_buffer

    chat = update.effective_chat
    if chat is None:
        return
    if update.message is None:
        return
    if chat.type == Chat.PRIVATE:
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

        to_chat_file(
            filename="conversation_log.json", dt=[user_message, assistant_message]
        )
        await update.message.reply_markdown(output_content)


async def on_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text("Sthenno 已开启.")
    else:
        return


def sample(
    instruction: str,
    output: str,
    input_content: str = "",
    system: str = "",
    history: list = [],
) -> dict:
    return {
        "instruction": instruction,
        "input": input_content,
        "output": output,
        "system": system,
        "history": history,
    }


def sample_dpo(
    instruction: str,
    output: list[str],
    input_content: str = "",
    system: str = "",
    history: list = [],
) -> dict:
    return {
        "instruction": instruction,
        "input": input_content,
        "output": output,
        "system": system,
        "history": history,
    }


async def on_keep(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global messages_buffer

    messages_to_keep = messages_buffer[-2:]
    instruction: str = messages_to_keep[0]["content"]
    output: str = messages_to_keep[1]["content"]

    to_chat_file(
        filename="samples/sft.json",
        data=[
            sample(
                instruction=instruction,
                output=output,
            )
        ],
    )

    if update.message:
        await update.message.reply_text("sample 已保存.")
    else:
        return


async def on_make(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global messages_buffer
    messages_buffer = []

    if update.message:
        await update.message.reply_text("Sthenno 已重置.")
    else:
        return


def main() -> None:
    app = Application.builder().token(TOKEN).build()

    print("Sthenno 已开启.")

    app.add_handler(CommandHandler("start", on_start))
    app.add_handler(CommandHandler("make", on_make))
    app.add_handler(CommandHandler("keep", on_keep))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
    app.run_polling(poll_interval=5.0)


if __name__ == "__main__":
    main()
