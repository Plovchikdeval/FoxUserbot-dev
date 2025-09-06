from pyrogram import Client
from modules.plugins_1system.restarter import restart
from command import fox_command, fox_sudo, who_message
import os
import wget
import re

use_data_dir = 'SHARKHOST' in os.environ or 'DOCKER' in os.environ
base_dir = '/data' if use_data_dir else os.getcwd()
userdata_dir = os.path.join(base_dir, "userdata")
temp_dir = os.path.join(base_dir, "temp")
triggers_dir = os.path.join(base_dir, "triggers")
modules_dir = os.path.join("modules", "plugins_2custom")

os.makedirs(userdata_dir, exist_ok=True)
os.makedirs(temp_dir, exist_ok=True)
os.makedirs(triggers_dir, exist_ok=True)
os.makedirs(modules_dir, exist_ok=True)

def modify_module_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        paths = {
            'userdata': userdata_dir,
            'temp': temp_dir,
            'triggers': triggers_dir
        }

        modified = False
        for key, full_path in paths.items():
            pattern = rf'(?<![a-zA-Z0-9_/\\]){key}/'
            repl = full_path + '/'
            new_content, count = re.subn(pattern, repl, content)
            if count > 0:
                content = new_content
                modified = True

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        return modified
    except Exception as e:
        print(f"Error modifying file {file_path}: {e}")
        return False

@Client.on_message(fox_command("loadmod", "Loadmod", os.path.basename(__file__), "[link to the module/reply]") & fox_sudo())
async def loadmod(client, message):
    message = await who_message(client, message)
    await message.edit("<b>Loading module...</b>")

    if message.reply_to_message and message.reply_to_message.document:
        document = message.reply_to_message.document
        file_path = await client.download_media(document, file_name=modules_dir)
    else:
        try:
            link = message.text.split()[1]
        except IndexError:
            await message.edit("<b>❌ Please provide a link or reply with a module file.</b>")
            return
        file_path = os.path.join(modules_dir, os.path.basename(link))
        wget.download(link, file_path)

    modified = modify_module_file(file_path)

    if modified:
        await message.edit("<emoji id='5237699328843200968'>✅</emoji> Module loaded and modified successfully.\nRestarting...")
    else:
        await message.edit("<emoji id='5237699328843200968'>✅</emoji> Module loaded successfully.\nRestarting...")

    await restart(message, restart_type="restart")
