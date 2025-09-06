from pyrogram import Client, filters
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os
import asyncio
import json

def prestart(api_id, api_hash, device_mod):
    from pyrogram.client import Client
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    use_data_dir = 'SHARKHOST' in os.environ or 'DOCKER' in os.environ
    base_dir = '/data' if use_data_dir else os.getcwd()
    triggers_dir = os.path.join(base_dir, "triggers")
    userdata_dir = os.path.join(base_dir, "userdata")

    if not os.path.exists(triggers_dir):
        try:
            os.makedirs(triggers_dir)
        except Exception:
            pass
    
    if not os.path.exists(userdata_dir):
        try:
            os.makedirs(userdata_dir)
        except Exception:
            pass

    app = Client("my_account", api_id=api_id, api_hash=api_hash, device_model=device_mod, workdir=base_dir)
    
    async def check_connection():
        await app.connect()
        await app.disconnect()
    
    loop.run_until_complete(check_connection())
    with app:
        if len(sys.argv) >= 4:
            restart_type = sys.argv[3]
            thread_id = None
            if len(sys.argv) >= 5 and sys.argv[4] != "None":
                try:
                    thread_id = int(sys.argv[4])
                except ValueError:
                    thread_id = None
                    
            if restart_type == "1":
                text = "<emoji id='5237699328843200968'>✅</emoji> <code>Update process completed!</code>"
            else:
                text = "<emoji id='5237699328843200968'>✅</emoji> <code>Userbot succesfully Restarted</code>"
            try:
                app.send_message(int(sys.argv[1]), text, message_thread_id=thread_id)
            except Exception as f:
                app.send_message("me", f"<emoji id='5210952531676504517'>❌</emoji> Got error: {f}\n\n" + text)
        
        # Triggers
        for i in os.listdir(triggers_dir):
            with open(os.path.join(triggers_dir, i), 'r') as f:
                text = f.read().strip()
                app.send_message("me", text, schedule_date=(datetime.now() + timedelta(seconds=70)))

        # Sudo User
        current_user_id = (app.get_users("me")).id
        sudo_file = Path(os.path.join(userdata_dir, "sudo_users.json"))
        try:
            with open(sudo_file, "r") as f:
                existing_users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_users = []
        if current_user_id not in existing_users:
            existing_users.append(current_user_id)
            with open(sudo_file, "w") as f:
                json.dump(existing_users, f)
