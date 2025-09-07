# -*- coding: utf-8 -*-
import pip
import os
import time
import sys
import re
import logging

from requirements_installer import install_library
from migrate import convert_modules

use_data_dir = 'SHARKHOST' in os.environ or 'DOCKER' in os.environ

def is_running_in_termux():
    termux_vars = [
        'TERMUX_VERSION',
        'TERMUX_APK_RELEASE',
        'PREFIX',
    ]
    return any(var in os.environ for var in termux_vars)

def check_structure():
    base_dir = '/data' if use_data_dir else os.getcwd()

    if use_data_dir and not os.path.exists(base_dir):
        try:
            os.makedirs(base_dir)
        except Exception:
            return

    if os.path.exists(os.path.join(base_dir, "localhost_run_output.txt")):
        os.remove(os.path.join(base_dir, "localhost_run_output.txt"))
    if not os.path.exists(os.path.join(base_dir, "temp")):
        os.mkdir(os.path.join(base_dir, "temp"))
    if not os.path.exists(os.path.join(base_dir, "userdata")):
        os.mkdir(os.path.join(base_dir, "userdata"))
    if not os.path.exists(os.path.join(base_dir, "triggers")):
        os.mkdir(os.path.join(base_dir, "triggers"))

def autoupdater():
    try:
        from pyrogram.client import Client
    except ImportError:
        try:
            session_dir = '/data' if use_data_dir else os.getcwd()
            os.remove(os.path.join(session_dir, "temp/firstlaunch.temp"))
        except OSError:
            pass

    first_launched = False
    session_dir = '/data' if use_data_dir else os.getcwd()
    try:
        with open(os.path.join(session_dir, "temp/firstlaunch.temp"), "r", encoding="utf-8") as f:
            if (f.readline().strip() == "1"):
                first_launched = True
    except FileNotFoundError:
        pass

    if not first_launched:
        pip.main(["uninstall", "pyrogram", "kurigram", "-y"])
        if not is_running_in_termux():
            install_library('uv -U')
        else:
            os.system("termux-wake-lock")
            os.system("pkg update -y ; pkg install uv -y")
        install_library('tgcrypto -U')
        with open(os.path.join(session_dir, "temp/firstlaunch.temp"), "w", encoding="utf-8") as f:
            f.write("1")
    
    install_library('-r requirements.txt -U')

def setup_logging():
    session_dir = '/data' if use_data_dir else os.getcwd()
    log_dir = os.path.join(session_dir, 'temp')
    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    if "--safe" in sys.argv:
        log_file = os.path.join(log_dir, 'fox_userbot_safe.log')
        try:
            if os.path.exists(log_file):
                os.remove(log_file)
        except:
            pass
    else:
        log_file = os.path.join(log_dir, 'fox_userbot.log')
        try:
            if os.path.exists(log_file):
                os.remove(log_file)
        except:
            pass

    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    console_handler = logging.StreamHandler()
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)
    
    return root_logger

async def start_userbot(app):
    await app.start()
    user = await app.get_me()
    session_dir = '/data' if use_data_dir else os.getcwd()
    session_file = os.path.join(session_dir, "my_account.session")
    
    if os.path.exists(session_file):
        pass
    else:
        localhost_file = os.path.join(session_dir, "localhost_run_output.txt")
        if os.path.exists(localhost_file):
            os.remove(localhost_file)
        os.execv(sys.executable, [sys.executable] + sys.argv)

def userbot():
    from pyrogram.client import Client
    from configurator import my_api
    from prestarter import prestart
    from web_auth.web_auth import start_web_auth
    import os
    import sys
    import asyncio
    import time
    
    safe_mode = False
    if "--safe" in sys.argv:
        safe_mode = True
    
    api_id, api_hash, device_mod = my_api()

    session_dir = '/data' if use_data_dir else os.getcwd()

    if use_data_dir and not os.path.exists(session_dir):
        try:
            os.makedirs(session_dir)
        except Exception:
            return
    
    session_file = os.path.join(session_dir, "my_account.session")
    
    if os.path.exists(session_file):
        prestart(api_id, api_hash, device_mod)
        try:
            client = Client(
                "my_account",
                api_id=api_id,
                api_hash=api_hash,
                device_model=device_mod,
                workdir=session_dir,
                plugins=dict(root="modules" if not safe_mode else "modules/plugins_1system")
            )
            client.run()
        except Exception as e:
            print(f"Error starting client: {e}")
            if not safe_mode:
                os.execv(sys.executable, [sys.executable] + sys.argv + ["--safe"])
        return
    
    if "--cli" in sys.argv:
        client = Client(
            "my_account",
            api_id=api_id,
            api_hash=api_hash,
            device_model=device_mod,
            workdir=session_dir
        )
        client.run()
    else:      
        success, user = start_web_auth(api_id, api_hash, device_mod)
        
        if not success or user is None:
            return
        
        time.sleep(2)
        
        if not os.path.exists(session_file):
            print("Session file was not created after web auth. Restarting...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
            return
    
    prestart(api_id, api_hash, device_mod)

    try:
        client = Client(
            "my_account",
            api_id=api_id,
            api_hash=api_hash,
            device_model=device_mod,
            workdir=session_dir,
            plugins=dict(root="modules" if not safe_mode else "modules/plugins_1system")
        )
        client.run()
    except Exception as e:
        print(f"Error starting client: {e}")
        if not safe_mode:
            os.execv(sys.executable, [sys.executable] + sys.argv + ["--safe"])

if __name__ == "__main__":
    check_structure()
    convert_modules()
    logger = setup_logging()
    logger.info("Starting FoxUserbot...")
    autoupdater()
    userbot()
