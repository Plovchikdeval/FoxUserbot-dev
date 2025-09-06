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
        
        patterns = {
            r'"userdata/': f'"{userdata_dir}/',
            r"'userdata/": f"'{userdata_dir}/",
            r'"temp/': f'"{temp_dir}/',
            r"'temp/": f"'{temp_dir}/",
            r'"triggers/': f'"{triggers_dir}/',
            r"'triggers/": f"'{triggers_dir}/",
            r'os.path.join\("userdata"': f'os.path.join("{userdata_dir}"',
            r"os.path.join('userdata'": f"os.path.join('{userdata_dir}'",
            r'os.path.join\("temp"': f'os.path.join("{temp_dir}"',
            r"os.path.join('temp'": f"os.path.join('{temp_dir}'",
            r'os.path.join\("triggers"': f'os.path.join("{triggers_dir}"',
            r"os.path.join('triggers'": f"os.path.join('{triggers_dir}'"
        }
        
        modified = False
        for pattern, replacement in patterns.items():
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
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
    
    if not message.reply_to_message:
        await message.edit("<b>Load module...</b>")
        link = message.text.split()[1]
        filename = wget.download(link, modules_dir)
        file_path = os.path.join(modules_dir, os.path.basename(filename))
        
        if modify_module_file(file_path):
            await message.edit(
                f"<emoji id='5237699328843200968'>✅</emoji> **The module has been loaded and modified successfully** \nRestart..."
            )
        else:
            await message.edit(
                f"<emoji id='5237699328843200968'>✅</emoji> **The module has been loaded successfully** \nRestart..."
            )
        
        await restart(message, restart_type="restart")
    else:
        document = message.reply_to_message.document
        file_path = await client.download_media(document, file_name=modules_dir)
        
        if modify_module_file(file_path):
            await message.edit(
                f"<emoji id='5237699328843200968'>✅</emoji> **The module has been loaded and modified successfully** \nRestart..."
            )
        else:
            await message.edit(
                f"<emoji id='5237699328843200968'>✅</emoji> **The module has been loaded successfully** \nRestart..."
            )
        
        await restart(message, restart_type="restart")
