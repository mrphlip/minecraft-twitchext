import os
import appdirs
import sys
import wx

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

LOGIN_URL = 'https://www.mrphlip.com/mc_twitchext/login.php'

_icon = None
def ICON():
	global _icon
	if _icon is None:
		if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
			fn = os.path.join(sys._MEIPASS, 'icon.ico')
		elif os.path.isfile("../assets/icon.ico") and not os.path.isfile("icon.ico"):
			fn = "../assets/icon.ico"
		else:
			fn = "icon.ico"
		with open(fn, 'rb') as fp:
			_icon = wx.IconBundle(fp)
	return _icon
