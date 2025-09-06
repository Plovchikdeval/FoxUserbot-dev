from pyrogram import Client
import os
import shutil
import tarfile
import tempfile
from pathlib import Path
from modules.plugins_1system.settings.main_settings import version
from modules.plugins_1system.restarter import restart
from command import fox_command, fox_sudo, who_message

# backup_dirs
use_data_dir = 'SHARKHOST' in os.environ or 'DOCKER' in os.environ
base_dir = '/data' if use_data_dir else os.getcwd()
BACKUP_PATHS = [
    os.path.join(base_dir, 'userdata'),
    os.path.join(base_dir, 'triggers'), 
    'modules/plugins_2custom'
]

async def create_backup() -> str:
    def exclude_sudo_users(tarinfo):
        if tarinfo.name == os.path.join(base_dir, "userdata/sudo_users.json"):
            return None
        return tarinfo

    temp_dir = os.path.join(base_dir, "temp")
    if not os.path.exists(temp_dir):
        try:
            os.makedirs(temp_dir)
        except Exception:
            pass

    with tempfile.NamedTemporaryFile(suffix='_FoxUB_Backup.tar.gz', dir=temp_dir, delete=False) as tmp:
        with tarfile.open(tmp.name, mode='w:gz') as tar:
            for path in BACKUP_PATHS:
                if os.path.exists(path):
                    tar.add(path, arcname=os.path.relpath(path, base_dir) if path != 'modules/plugins_2custom' else path, filter=exclude_sudo_users)
        return tmp.name

async def restore_backup(client, message):
    if not message.reply_to_message or not message.reply_to_message.document:
        await message.edit("<b><emoji id='5210952531676504517'>❌</emoji> Need to reply to a message with a backup archive!</b>")
        return

    temp_dir = os.path.join(base_dir, "temp")
    if not os.path.exists(temp_dir):
        try:
            os.makedirs(temp_dir)
        except Exception:
            pass

    try:
        download_path = await message.reply_to_message.download(file_name=os.path.join(temp_dir, "restore_backup.tar.gz"))
        
        for path in BACKUP_PATHS:
            if os.path.exists(path):
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)

        with tarfile.open(download_path, 'r:gz') as tar:
            tar.extractall(path=base_dir)
        
        await message.edit("<b><emoji id='5237699328843200968'>✅</emoji> Data restored successfully!</b>")
    except Exception as e:
        await message.edit(f"<b><emoji id='5210952531676504517'>❌</emoji> Restore Error:</b>\n<code>{str(e)}</code>")
    finally:
        if 'download_path' in locals() and os.path.exists(download_path):
            os.remove(download_path)

@Client.on_message(fox_command("backup", "Backup", os.path.basename(__file__)) & fox_sudo())
async def backup_command(client, message):
    message = await who_message(client, message)
    try:
        msg = await message.edit("<b><emoji id='5264727218734524899'>🔄</emoji> Creating a backup copy...</b>")
        backup_file = await create_backup()
        
        await client.send_document(
            chat_id=message.chat.id,
            document=backup_file,
            caption=f"<emoji id='5472308992514464048'>🔐</emoji> | Backup {Path(backup_file).name}\n<emoji id='5283051451889756068'>🦊</emoji> | Only for FoxUserbot\n<emoji id='5296369303661067030'>🔒</emoji> | Version: {version}\n<emoji id='5271604874419647061'>🔗</emoji> | https://github.com/FoxUserbot/FoxUserbot",
            message_thread_id=message.message_thread_id
        )
        await msg.delete()
    except Exception as e:
        await message.edit(f"<b><emoji id='5210952531676504517'>❌</emoji> Error creating backup:</b>\n<code>{str(e)}</code>")
    finally:
        if 'backup_file' in locals() and os.path.exists(backup_file):
            os.remove(backup_file)

@Client.on_message(fox_command("restore", "Backup", os.path.basename(__file__), "[reply]") & fox_sudo())
async def restore_command(client, message):
    message = await who_message(client, message)
    await message.edit("<b><emoji id='5264727218734524899'>🔄</emoji> Ready for restoration...</b>")
    await restore_backup(client, message)
    await restart(message, restart_type="restart")
