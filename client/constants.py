import os
import appdirs

APP_NAME = 'TwitchMinecraftAdvancements'
APP_DESCRIPTION = 'Twitch Minecraft Advancements'
APP_AUTHOR = 'MrPhlip'
APP_DIRS = appdirs.AppDirs(APP_NAME, APP_AUTHOR, roaming=True)

# see https://help.mojang.com/customer/portal/articles/1480874-where-are-minecraft-files-stored-
if appdirs.system == 'win32':
	DEF_MINECRAFT_DIR = appdirs.user_data_dir('.minecraft', roaming=True)
elif appdirs.system == 'darwin':
	DEF_MINECRAFT_DIR = appdirs.user_data_dir('minecraft')
else:
	DEF_MINECRAFT_DIR = os.path.expanduser("~/.minecraft")
