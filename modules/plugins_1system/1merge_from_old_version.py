import os
import shutil
import wget
from modules.plugins_1system.restarter import restart_executor

# 1.0 > 2.0
if os.path.isdir("plugins"):
    i = random.randint(10000, 99999)
    os.rename("plugins", f"modules_old_{i}")

# 2.1 > 2.2
if os.path.exists("modules/plugins_1system/support.py"):
    os.remove("modules/plugins_1system/support.py")

# 2.2 > 2.3
use_data_dir = 'SHARKHOST' in os.environ or 'DOCKER' in os.environ
base_dir = '/data' if use_data_dir else os.getcwd()
temp_dir = os.path.join(base_dir, "temp")
userdata_dir = os.path.join(base_dir, "userdata")
triggers_dir = os.path.join(base_dir, "triggers")

if not os.path.exists(temp_dir):
    try:
        os.makedirs(temp_dir)
    except Exception:
        pass
if not os.path.exists(userdata_dir):
    try:
        os.makedirs(userdata_dir)
    except Exception:
        pass
if not os.path.exists(triggers_dir):
    try:
        os.makedirs(triggers_dir)
    except Exception:
        pass

if os.path.isdir(os.path.join(temp_dir, "autoanswer_DB")):
    shutil.move(os.path.join(temp_dir, "autoanswer_DB"), os.path.join(userdata_dir, "autoanswer_DB"))
if os.path.exists(os.path.join(temp_dir, "autoanswer")):
    os.replace(os.path.join(temp_dir, "autoanswer"), os.path.join(userdata_dir, "autoanswer"))
if os.path.exists(os.path.join(temp_dir, "lastfm_username.txt")):
    os.replace(os.path.join(temp_dir, "lastfm_username.txt"), os.path.join(userdata_dir, "lastfm_username"))
if os.path.exists(os.path.join(temp_dir, "lastfm_current_song.txt")):
    os.replace(os.path.join(temp_dir, "lastfm_current_song.txt"), os.path.join(userdata_dir, "lastfm_current_song"))
if os.path.exists(os.path.join(temp_dir, "lastfm_channel.txt")):
    os.replace(os.path.join(temp_dir, "lastfm_channel.txt"), os.path.join(userdata_dir, "lastfm_channel"))
if os.path.exists(os.path.join(temp_dir, "lastfm_id_in_channel_telegram.txt")):
    os.replace(os.path.join(temp_dir, "lastfm_id_in_channel_telegram.txt"), os.path.join(userdata_dir, "lastfm_id_in_channel_telegram"))
if os.path.exists(os.path.join(temp_dir, "lastfm_autostart.txt")):
    os.replace(os.path.join(temp_dir, "lastfm_autostart.txt"), os.path.join(triggers_dir, "lastfm_autostart"))
    autostartF = open(os.path.join(triggers_dir, "lastfm_autostart"), "w+", encoding="utf-8")
    autostartF.write("last_fm_trigger_start")
    autostartF.close()

# 2.2 > 2.3
# modules
modules = ["user_info.py", "weather.py", "webshot.py", "wikipedia.py", "switch.py", "tagall.py",
           "time_now.py", "type.py", "stats.py", "spamban.py", "spam.py", "speech.py", "short.py",
           "sendToId.py", "qr.py", "quotes.py", "reputation.py", "premium_text.py", "progressbar.py",
           "purge.py", "ignore.py", "kickall.py", "ladder.py", "lastfm.py", "link.py",
           "find_music.py", "gen_pass.py", "hearts.py", "afk.py", "autoanswer.py", "autoonline.py",
           "autoread.py", "chance.py", "demotivator.py"]
modules_value = 0
for _ in modules:
    try:
        if os.path.exists(f"modules/plugins_1system/{_}"):
            link = f"https://raw.githubusercontent.com/FoxUserbot/CustomModules/refs/heads/main/{_}"
            wget.download(link, f"temp/{_}")
            os.replace(f"temp/{_}", f"modules/plugins_2custom/{_}")
            os.remove(f"modules/plugins_1system/{_}")
            modules_value += 1
    except Exception:
        pass
if modules_value >= 1:
    restart_executor()

# 2.3 > 2.3.3
if os.path.exists("first_launch.bat"):
    os.remove("first_launch.bat")
if os.path.exists("check.py"):
    os.remove("check.py")
if os.path.exists("help_first_launch.py"):
    os.remove("help_first_launch.py")

# 2.3.3 > 2.3.4
if os.path.exists("config.ini"):
    os.replace("config.ini", os.path.join(userdata_dir, "config.ini"))
    restart_executor()

# 2.3.5 > 2.4
if os.path.isdir("modules/plugins_3finished"):
    shutil.rmtree("modules/plugins_3finished")
    restart_executor()

if os.path.exists("logo.png"):
    os.remove("logo.png")

# 2.4.3
if os.path.exists("photo/foxuserbot_info.jpg"):
    os.remove("photo/foxuserbot_info.jpg")
if os.path.exists("photo/system_info.jpg"):
    os.remove("photo/system_info.jpg")
if os.path.exists(os.path.join(temp_dir, "firstlaunch.temp")):
    os.remove(os.path.join(temp_dir, "firstlaunch.temp"))
