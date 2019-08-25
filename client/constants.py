import os
import appdirs

APP_NAME = 'TwitchMinecraftAdvancements'
APP_DESCRIPTION = 'Twitch Minecraft Advancements'
APP_AUTHOR = 'MrPhlip'
APP_DIRS = appdirs.AppDirs(APP_NAME, APP_AUTHOR, roaming=True)

# see https://help.mojang.com/customer/portal/articles/1480874-where-are-minecraft-files-stored-
if appdirs.system == 'win32':
	DEF_MINECRAFT_DIR = appdirs.user_data_dir('.minecraft', False, roaming=True)
elif appdirs.system == 'darwin':
	DEF_MINECRAFT_DIR = appdirs.user_data_dir('minecraft')
else:
	DEF_MINECRAFT_DIR = os.path.expanduser("~/.minecraft")

CLIENT_ID = 'slvinmcxz6qqkut8s3oxckx14ka85w'

LOGIN_URL = 'https://www.mrphlip.com/twitchext.php'
