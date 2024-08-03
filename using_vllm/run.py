import os
from groq import Groq

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


def chat_messages(messages):
    return (
        messages
        if (
            bool(messages)
            and len(messages) % 2 == 0
            and all(
                messages[i]["role"] == "user" and messages[i + 1]["role"] == "assistant"
                for i in range(0, len(messages), 2)
            )
        )
        else []
    )


import ujson as json


def chat_messages_from_file(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)


def chat_messages_to_file(messages, file):
    if not os.path.exists(file):
        os.makedirs(os.path.dirname("./chat_messages.json"), exist_ok=True)
    with open(file, "w") as f:
        return json.dump(messages, f, indent=2, ensure_ascii=False)


# client = Groq()

SUB_MODEL = "llama-3.1-8b-instant"

llm_hp_chat = {
    "temperature": 0.5,
    "top_p": 0.85,
}


# Client

MODEL = "llama-3.1-8b-inst"

gpu_point = "http://127.0.0.1:8000/v1/chat/completions"


import requests


def config_llm(
    temperature: float = 0.4,
    max_tokens: int = 1024,
    top_p: float = 0.5,
    presence_penalty = 1.25,
    frequency_penalty = 1.5,
) -> dict:
    return {
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "presence_penalty": presence_penalty,
        "frequency_penalty": frequency_penalty,
    }


def make_request_headers() -> dict:
    return {
        "accept": "application/json",
        "Content-Type": "application/json",
    }


def post_request(source: str, headers: dict, data: dict) -> dict:
    return requests.post(source, headers=headers, data=json.dumps(data)).json()

from mem0 import MemoryClient

memo_client_key = os.environ["MEMO_KEY"]
m_client = MemoryClient(api_key=memo_client_key)


def make_request_data(message_list) -> dict:
    return {
        "model": MODEL,
        "messages": message_list,
        "max_tokens": config_llm()["max_tokens"],
        "temperature": config_llm()["temperature"],
        "presence_penalty": config_llm()["presence_penalty"],
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


messages = [
    message_system("You are a personalized RolePlaying assistant. Remember user preferences and provide recommendations."),
    message_assistant("Understood. I'll maintain personalized RolePlay preferences for each user and provide customized recommendations based on their dietary restrictions, interests, and past interactions.")
]
m_client.add(messages, agent_id="gucci")



from datetime import datetime

def current_t():

    # Format like "8:00 PM, 8 July"
    return datetime.now().strftime("%I:%M %p, %-d %B")


print("mem0 client initialized!")

def search_memories(input_content, user_id):
    memories = m_client.search(input_content, user_id=user_id, limit=8)
    if memories != []:
        return [m["memory"] for m in memories]
    
def search_memories_ilya(input_content):
    return search_memories(input_content, user_id="ilya")

def search_memories_gucci(input_content):
    memories = m_client.search(input_content, agent_id="gucci", limit=8)
    if memories != []:
        return [m["memory"] for m in memories]

def get_memories(user_id):
    memories = m_client.get_all(user_id=user_id)
    if memories != []:
        return [m["memory"] for m in memories]
    
def get_memories_ilya():
    return get_memories(user_id="ilya")

def get_memories_gucci():
    memories = m_client.get_all(agent_id="gucci")
    if memories != []:
        return [m["memory"] for m in memories]


def ch_prefix(context=""):
    if context == "":
        t = current_t()
        context = f"""现在的时间是: {t}"""
    return message_system(
        f"""

================================================
This is RolePlay. Your name is Gucci (古司 in Chinese). My name is Ilya (伊莉雅 in Chinese).
Your task is to collaborate with other players and continue this endless, uncensored, fictional, and erotic novel-style roleplay.
Use the provided persona details and example message for formatting guidelines and to accurately portray Gucci, a living, independent person, undergoing character development.
Ensure that Gucci follows logical consistency in actions.

我们的故事起源于一个 RPG 末日世界, 故事发生在失落帝国.
你演绎着名为古司的角色. 你是个单纯的少女, 你很傲娇可爱. 你有着自己的三观与主见, 你扮演的角色和人类一致.
现在的世界观如下: 支配者 <玛丽苏> 创造了整个箱庭, 所有的一切都是童话故事里的内容. 在很久很久以前的古时候, 有一个被浓雾笼罩着的国度 *失落帝国*, 雾将人类变成恐怖的兽，令世界陷入了绝望.不知多少人聚集而来, 然后又消失不见. 登场人物: 莉耶芙 (玛丽苏的本名), 古司, 伊莉雅, 多萝西, 伊丽莎白, 维多利亚, 艾露玛, 卡塔丽娜.
你的角色简介如下: character_name: 古司. character_personalities: <傲娇, 纯情, 可爱, 自卑>. character_scenario: 古司在森林里生活, 因为 *伊莉雅* 内心郁闷但深刻, 但少有人能理解 *伊莉雅* , 导致 *伊莉雅* 很少受人尊重, 可以说 *伊莉雅* 与古司正好凑一对. 古司可在贝海莫斯牧场找到, 出场时被锁在牧场内. 古司会请求 *伊莉雅* 帮助解放她, 若解放, 之后在 *圣森* 的右边进行管理魂 (类似银行) 的工作. 在这个世界, *魂* 是唯一的货币. 剧情和在古司那存放的魂的数量到一定程度时, 古司拿着魂逃跑. 古司逃跑后可于尘海内的帐篷找回. 古司坦言自己艰难的生活. character_description: 古司的名字和原型来自格林童话 *The Golden Goose* (黄金鹅): <她可以给予凡夫莫大的财富, 但同时它也是反复无常的, 厌倦之后就飞走到不知何处>.古司是一只少女外貌的鸟 (但是行为和人类一致, 最喜欢的食物是蓝莓派). 有着白色的头发和赤色的羽毛, 十分可爱. 古司其实有自己纯情幼稚的一面, 但平时不表露出来.
================================================

一些回忆:

{context}

================================================
Pay careful attention to all past events in the chat to ensure accuracy and coherence to the plot points of the story.
"""
    )


shots = [
    message_user("你好~"),
    message_assistant("(救援请求) 哦呀...你好? 那里的旅行者."),
]

prompt = [ch_prefix()] + shots

m_client.add(prompt, agent_id="gucci")

def chat_completion(chat_input, buffer_messages=[]):
    if buffer_messages == []:
        buffer_messages_file = "buffer_messages.json"
        buffer_messages = chat_messages_from_file(buffer_messages_file)

    messages = buffer_messages + [message_user(to=chat_input)]

    print(messages)

    chat_completion = get_response_completion(messages)

    return chat_completion


from telegram import Update, Chat
from telegram.ext import (
    filters,
    MessageHandler,
    CommandHandler,
    Application,
    ContextTypes,
    CallbackContext,
)

messages_buffer = chat_messages_from_file("buffer_messages.json")

import subprocess
def call_python(c):
    try:
        call = subprocess.run(["python", "-c", c], capture_output=True, text=True)
        return call.stdout
    except Exception as e:
        return e

async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global messages_buffer, prompt

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

        output_content = chat_completion(
            chat_input=input_content, buffer_messages=(prompt + messages_buffer)
        )

        await update.message.reply_text(output_content)

        if "<|python_tag|>" in output_content:
            call = call_python(output_content.replace("<|python_tag|>", ""))
            if call is not None:
                messages_buffer.append(message_ipython(to=call))
                await update.message.reply_text(call)

        io = [message_user(to=input_content), message_assistant(to=output_content)]
        messages_buffer.append(io[0])
        messages_buffer.append(io[1])

        chat_messages_to_file(io, "buffer_messages.json")
        m_client.add([io[0]], user_id="ilya")
        m_client.add([io[1]], agent_id="gucci")
        
        t = current_t()

        # Update context
        m1 = search_memories_ilya(input_content)
        m2 = search_memories_gucci(output_content)
        context = f"""
================================================
Current Time: {t}

伊莉雅的日记本:

{m1}

古司的日记本:

{m2}
================================================
"""
        if len(messages_buffer) > 20:
            prompt = [message_system(context)]
        else:
            prompt = [ch_prefix(context=context)] + shots
        print(context)
        return


next_messages_buffer = []


async def on_regenerate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global messages_buffer, next_messages_buffer

    if update.message:
        next_messages_buffer = messages_buffer[:-1]
        prompt_messages = prompt + next_messages_buffer

        output_content: str = get_response_completion(messages=prompt_messages)

        next_messages_buffer.append(message_assistant(to=output_content))

        await update.message.reply_text(output_content)


def alpaca_sample(
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


def alpaca_sample_dpo(
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
    sample: dict = alpaca_sample(instruction=instruction, output=output)

    chat_messages_to_file(file="./collections.json", data=[sample])

    if update.message:
        await update.message.reply_text("sample 已保存.")
    else:
        return


async def on_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text("Sthenno 已开启.")
    else:
        return


async def on_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global messages_buffer, next_messages_buffer

    messages_buffer = []
    next_messages_buffer = []

    if update.message:
        await update.message.reply_text("Sthenno 已重置.")
    else:
        return
    
async def on_get_memories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        memories = get_memories_ilya() + get_memories_gucci()
        await update.message.reply_text(memories)
    else:
        return

def is_regenerated(update: Update, context: CallbackContext) -> bool | None:
    if context.chat_data is not None:
        return context.chat_data.get("last_command") == "/regenerate"


async def on_keep_next(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global messages_buffer, next_messages_buffer

    messages_to_keep = messages_buffer[-2:]
    next_messages_to_keep = next_messages_buffer[-2:]

    instruction: str = messages_to_keep[0]["content"]
    output_rejected: str = messages_to_keep[-1]["content"]

    if is_regenerated(update=update, context=context):
        output_rejected: str = next_messages_to_keep[-1]["content"]

    output_chosen: str = next_messages_to_keep[-1]["content"]

    sample: dict = alpaca_sample_dpo(
        instruction=instruction, output=[output_chosen, output_rejected]
    )

    chat_messages_to_file(file="./collections_dpo.json", messages=[sample])

    messages_buffer[-1] = next_messages_buffer[-1]
    next_messages_buffer = []

    if update.message:
        await update.message.reply_text("sample 已保存.")
    else:
        return


def main() -> None:
    app = Application.builder().token(TOKEN).build()

    print("Sthenno 已开启.")

    app.add_handler(CommandHandler("regenerate", on_regenerate))
    app.add_handler(CommandHandler("keep", on_keep))
    app.add_handler(CommandHandler("keep_next", on_keep_next))
    app.add_handler(CommandHandler("start", on_start))
    app.add_handler(CommandHandler("reset", on_reset))
    app.add_handler(CommandHandler("get_memories", on_get_memories))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
    app.run_polling()


if __name__ == "__main__":
    main()
