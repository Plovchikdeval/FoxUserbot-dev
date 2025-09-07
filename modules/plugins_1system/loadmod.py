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
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
            
        if not file_path.endswith('.py'):
            print(f"Not a Python file: {file_path}")
            return False
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        paths = {
            'userdata': userdata_dir,
            'temp': temp_dir,
            'triggers': triggers_dir
        }

        modified = False
        for key, full_path in paths.items():
            normalized_path = full_path.replace('\\', '/')
            pattern = rf'(f?["\'])(?P<path>[^"\']*{key}/[^"\']*)'
            matches = list(re.finditer(pattern, content))
            
            for m in reversed(matches):
                orig_path = m.group('path')
                if normalized_path in orig_path:
                    continue
                    
                print(f"Found path to replace: {orig_path}")
                replacement = orig_path.replace(f"{key}/", f"{normalized_path}/")
                start_pos = m.start('path')
                end_pos = m.end('path')
                content = content[:start_pos] + replacement + content[end_pos:]
                modified = True

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        return modified
    except Exception as e:
        print(f"Error modifying file {file_path}: {e}")
        return False

def validate_python_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        compile(content, file_path, 'exec')
        return True
    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"Error validating {file_path}: {e}")
        return False

@Client.on_message(fox_command("loadmod", "Loadmod", os.path.basename(__file__), "[link to the module/reply]") & fox_sudo())
async def loadmod(client, message):
    message = await who_message(client, message, message.reply_to_message)
    await message.edit("<b>Loading module...</b>")

    try:
        temp_file = None
        final_file = None
        
        if message.reply_to_message and message.reply_to_message.document:
            document = message.reply_to_message.document
            if not document.file_name.endswith('.py'):
                await message.edit("<b>❌ Please provide a Python file (.py)</b>")
                return
            temp_file = await client.download_media(document, file_name=os.path.join(temp_dir, document.file_name))
            final_file = os.path.join(modules_dir, document.file_name)
        else:
            try:
                link = message.text.split()[1]
            except IndexError:
                await message.edit("<b>❌ Please provide a link or reply with a module file.</b>")
                return
                
            if not link.endswith('.py'):
                await message.edit("<b>❌ Link must point to a Python file (.py)</b>")
                return
                
            filename = os.path.basename(link)
            temp_file = os.path.join(temp_dir, filename)
            final_file = os.path.join(modules_dir, filename)
            
            try:
                wget.download(link, temp_file)
            except Exception as e:
                await message.edit(f"<b>❌ Failed to download module: {str(e)}</b>")
                return

        if not validate_python_file(temp_file):
            if os.path.exists(temp_file):
                os.remove(temp_file)
            await message.edit("<b>❌ Invalid Python file. Module deleted.</b>")
            return

        with open(temp_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        paths = {
            'userdata': userdata_dir,
            'temp': temp_dir,
            'triggers': triggers_dir
        }

        modified = False
        for key, full_path in paths.items():
            normalized_path = full_path.replace('\\', '/')
            pattern = rf'(f?["\'])(?P<path>[^"\']*{key}/[^"\']*)'
            matches = list(re.finditer(pattern, content))
            
            for m in reversed(matches):
                orig_path = m.group('path')
                if normalized_path in orig_path:
                    continue
                    
                print(f"Found path to replace: {orig_path}")
                replacement = orig_path.replace(f"{key}/", f"{normalized_path}/")
                start_pos = m.start('path')
                end_pos = m.end('path')
                content = content[:start_pos] + replacement + content[end_pos:]
                modified = True

        with open(final_file, 'w', encoding='utf-8') as f:
            f.write(content)

        if os.path.exists(temp_file):
            os.remove(temp_file)

        if modified:
            await message.edit("<emoji id='5237699328843200968'>✅</emoji> Module loaded and modified successfully.\nRestarting...")
        else:
            await message.edit("<emoji id='5237699328843200968'>✅</emoji> Module loaded successfully.\nRestarting...")

        await restart(message, restart_type="restart")
        
    except Exception as e:
        if 'temp_file' in locals() and temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
        await message.edit(f"<b>❌ Error loading module: {str(e)}</b>")
