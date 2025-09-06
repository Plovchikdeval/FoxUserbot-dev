# -*- coding: utf-8 -*-
import logging
import pip
import os
import time
import sys
import re

from requirements_installer import install_library
from migrate import convert_modules

def is_running_in_termux():
    termux_vars = [
        'TERMUX_VERSION',
        'TERMUX_APK_RELEASE',
        'PREFIX',
    ]
    return any(var in os.environ for var in termux_vars)

def check_structure():
    if os.path.exists("localhost_run_output.txt"):
        os.remove("localhost_run_output.txt")
    if not os.path.exists("temp"):
        os.mkdir("temp")
    if not os.path.exists("userdata"):
        os.mkdir("userdata")
    if not os.path.exists("triggers"):
        os.mkdir("triggers")

def autoupdater():
    try:
        from pyrogram.client import Client
    except ImportError:
        try:
            os.remove("temp/firstlaunch.temp")
        except OSError:
            pass

    first_launched = False
    try:
        with open("temp/firstlaunch.temp", "r", encoding="utf-8") as f:
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
        with open("temp/firstlaunch.temp", "w", encoding="utf-8") as f:
            f.write("1")
    
    install_library('-r requirements.txt -U')
    setup_logging()
    logger.info("Logging restored after installing dependencies")

async def start_userbot(app):
    await app.start()
    user = await app.get_me()
    session_file = "my_account.session"
    if os.path.exists(session_file):
        logger.info("[Session]: Session already exists, restart not required")
    else:
        logger.info("[Session]: First authorization, restarting main script")
        if os.path.exists("localhost_run_output.txt"):
            os.remove("localhost_run_output.txt")
        os.execv(sys.executable, [sys.executable] + sys.argv)

def setup_logging():
    if "--safe" in sys.argv:
        log_file = 'temp/fox_userbot_safe.log'
        try:
            if os.path.exists("temp/fox_userbot_safe.log"):
                os.remove("temp/fox_userbot_safe.log")
        except:
            pass
    else:
        log_file = 'temp/fox_userbot.log'
        try:
            if os.path.exists("temp/fox_userbot.log"):
                os.remove("temp/fox_userbot.log")
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

def userbot():
    from pyrogram.client import Client
    from configurator import my_api
    from prestarter import prestart
    from web_auth.web_auth import start_web_auth
    import os
    import sys
    import asyncio
    
    safe_mode = False
    if "--safe" in sys.argv:
        safe_mode = True
        logger.warning("[Userbot] Starting in safe mode (only system plugins)...")
    
    api_id, api_hash, device_mod = my_api()

    use_data_dir = 'SHARKHOST' in os.environ or 'DOCKER' in os.environ
    session_dir = '/data' if use_data_dir else os.getcwd()

    if use_data_dir and not os.path.exists(session_dir):
        try:
            os.makedirs(session_dir)
            logger.info(f"Created directory {session_dir} for session storage")
        except Exception as e:
            logger.error(f"Failed to create directory {session_dir}: {e}")
            return

    if not os.path.exists(os.path.join(session_dir, "my_account.session")):
        logger.warning("[Userbot] First launch! Authorization required...")  
        if "--cli" in sys.argv:
            logger.info("[Userbot] Running in CLI mode...")
            client = Client(
                "my_account",
                api_id=api_id,
                api_hash=api_hash,
                device_model=device_mod,
                workdir=session_dir
            ).run()
        else:      
            success, user = start_web_auth(api_id, api_hash, device_mod)
            
            if not success or user is None:
                logger.warning("[Userbot] Authorization failed!")
                return
            else:
                if not os.path.exists(os.path.join(session_dir, "my_account.session")):
                    logger.warning("[Userbot] Restarting...")
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                else:
                    logger.info("[Userbot] Session already exists, authorization not required")
    else:
        logger.info("[Userbot] Session already exists, authorization not required")
    
    prestart(api_id, api_hash, device_mod)

    try:
        client = Client(
            "my_account",
            api_id=api_id,
            api_hash=api_hash,
            device_model=device_mod,
            workdir=session_dir,
            plugins=dict(root="modules" if not safe_mode else "modules/plugins_1system")
        ).run()
    except Exception as e:
        if not safe_mode:
            logger.warning(f"[Userbot] Error detected: {e}")
            logger.warning("[Userbot] Restarting in safe mode (only system plugins)...")
            os.execv(sys.executable, [sys.executable] + sys.argv + ["--safe"])
        else:
            logger.warning(f"[Userbot] Critical error in safe mode: {e}")
            logging.critical(f"Critical error in safe mode: {e}")

if __name__ == "__main__":
    check_structure()
    convert_modules()
    logger = setup_logging()
    logger.info("Starting FoxUserbot...")
    autoupdater()
    userbot()
