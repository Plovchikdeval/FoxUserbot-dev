from pyrogram import Client
from pyrogram.types import Message
from command import fox_command, fox_sudo, who_message
import os
import zipfile
import wget
import shutil

def restart_executor(chat_id=None, message_id=None, text=None, thread=None):
    use_data_dir = 'SHARKHOST' in os.environ or 'DOCKER' in os.environ
    base_dir = '/data' if use_data_dir else os.getcwd()
    temp_dir = os.path.join(base_dir, "temp")
    
    if not os.path.exists(temp_dir):
        try:
            os.makedirs(temp_dir)
        except Exception:
            pass
            
    if os.name == "nt":
        os.execvp(
            "python",
            [
                "python",
                "main.py",
                f"{chat_id}",
                f"{message_id}",
                f"{text}",
                f"{thread}" if thread else "None",
            ],
        )
    else:
        os.execvp(
            "python3",
            [
                "python3",
                "main.py",
                f"{chat_id}",
                f"{message_id}",
                f"{text}",
                f"{thread}" if thread else "None",
            ],
        )

async def restart(message: Message, restart_type):
    if restart_type == "update":
        text = "1"
    else:
        text = "2"
    thread_id = message.message_thread_id if message.message_thread_id else None
    restart_executor(message.chat.id, message.id, text, thread_id)

@Client.on_message(fox_command("restart", "Restarter", os.path.basename(__file__)) & fox_sudo())
async def restart_get(client, message):
    message = await who_message(client, message, message.reply_to_message)
    try:
        await message.edit("<emoji id='5264727218734524899'>🔄</emoji> **Restarting userbot...**")
        await restart(message, restart_type="restart")
    except:
        await message.edit("<emoji id='5210952531676504517'>❌</emoji> **An error occured...**")

@Client.on_message(fox_command("update", "Restarter", os.path.basename(__file__)) & fox_sudo())
async def update(client, message):
    message = await who_message(client, message, message.reply_to_message)
    use_data_dir = 'SHARKHOST' in os.environ or 'DOCKER' in os.environ
    base_dir = '/data' if use_data_dir else os.getcwd()
    temp_dir = os.path.join(base_dir, "temp")
    
    if not os.path.exists(temp_dir):
        try:
            os.makedirs(temp_dir)
        except Exception:
            pass
            
    try:
        await message.edit('<emoji id="5264727218734524899">🔄</emoji> **Updating...**')
        link = "https://github.com/FoxUserbot/FoxUserbot/archive/refs/heads/main.zip"
        wget.download(link, os.path.join(temp_dir, 'archive.zip'))

        with zipfile.ZipFile(os.path.join(temp_dir, "archive.zip"), "r") as zip_ref:
            zip_ref.extractall(temp_dir)
        os.remove(os.path.join(temp_dir, "archive.zip"))

        shutil.make_archive(os.path.join(temp_dir, "archive"), "zip", os.path.join(temp_dir, "FoxUserbot-main"))

        with zipfile.ZipFile(os.path.join(temp_dir, "archive.zip"), "r") as zip_ref:
            zip_ref.extractall(".")
        os.remove(os.path.join(temp_dir, "archive.zip"))
        shutil.rmtree(os.path.join(temp_dir, "FoxUserbot-main"))

        await message.edit('<emoji id="5237699328843200968">✅</emoji> **Userbot succesfully updated\nRestarting...**')
        await restart(message, restart_type="update")
    except:
        await message.edit(f"<emoji id='5210952531676504517'>❌</emoji> **An error occured...**")

@Client.on_message(fox_command("beta", "Restarter", os.path.basename(__file__)) & fox_sudo())
async def update_beta(client, message):
    message = await who_message(client, message, message.reply_to_message)
    use_data_dir = 'SHARKHOST' in os.environ or 'DOCKER' in os.environ
    base_dir = '/data' if use_data_dir else os.getcwd()
    temp_dir = os.path.join(base_dir, "temp")
    
    if not os.path.exists(temp_dir):
        try:
            os.makedirs(temp_dir)
        except Exception:
            pass
            
    try:
        await message.edit('<emoji id="5264727218734524899">🔄</emoji> **Updating beta...**')
        link = "https://github.com/FoxUserbot/FoxUserbot-dev/archive/refs/heads/main.zip"
        wget.download(link, os.path.join(temp_dir, 'archive.zip'))

        with zipfile.ZipFile(os.path.join(temp_dir, "archive.zip"), "r") as zip_ref:
            zip_ref.extractall(temp_dir)
        os.remove(os.path.join(temp_dir, "archive.zip"))

        shutil.make_archive(os.path.join(temp_dir, "archive"), "zip", os.path.join(temp_dir, "FoxUserbot-dev-main"))

        with zipfile.ZipFile(os.path.join(temp_dir, "archive.zip"), "r") as zip_ref:
            zip_ref.extractall(".")
        os.remove(os.path.join(temp_dir, "archive.zip"))
        shutil.rmtree(os.path.join(temp_dir, "FoxUserbot-main"))

        await message.edit('<emoji id="5237699328843200968">✅</emoji> **Userbot succesfully updated\nRestarting...**')
        await restart(message, restart_type="update")
    except:
        await message.edit(f"<emoji id='5210952531676504517'>❌</emoji> **An error occured...**")

