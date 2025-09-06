import os
import sys
import configparser

use_data_dir = 'SHARKHOST' in os.environ or 'DOCKER' in os.environ
base_dir = '/data' if use_data_dir else os.getcwd()
userdata_dir = os.path.join(base_dir, "userdata")
PATH_FILE = os.path.join(userdata_dir, "config.ini")

config = configparser.ConfigParser()
config.read(PATH_FILE)

def get_prefix():
    prefix = config.get("prefix", "prefix")
    return prefix

def my_prefix():
    try:
        prefix = get_prefix()
    except:
        if not os.path.exists(userdata_dir):
            try:
                os.makedirs(userdata_dir)
            except Exception:
                pass
        config.add_section("prefix")
        config.set("prefix", "prefix", "!")
        with open(PATH_FILE, "w") as config_file:
            config.write(config_file)
        prefix = "!"
    return prefix
