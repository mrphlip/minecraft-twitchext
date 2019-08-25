#!/usr/bin/python3
import wx
from frames.main import MainFrame
from frames.config import MinecraftConfig, TwitchConfig
from state import ConfigState
from constants import APP_DESCRIPTION, ICON

class MinecraftClient(wx.App):
	def __init__(self):
		super().__init__(useBestVisual=True, clearSigInt=True)

	def OnInit(self):
		config = ConfigState.load()

		if not config.has_minecraft_config():
			with MinecraftConfig(config) as dlg:
				ret = dlg.ShowModal()
			if ret == wx.ID_CANCEL:
				return False
			elif not config.has_minecraft_config():
				with wx.MessageDialog(None, "Error in Minecraft config", APP_DESCRIPTION,
						style=wx.OK | wx.ICON_ERROR | wx.CENTRE) as dlg:
					dlg.SetIcons(ICON())
					dlg.ShowModal()
				return False

		if not config.has_twitch_config():
			with TwitchConfig(config) as dlg:
				ret = dlg.ShowModal()
			if ret == wx.ID_CANCEL:
				return False
			elif not config.has_twitch_config():
				with wx.MessageDialog(None, "Error in Twitch config", APP_DESCRIPTION,
						style=wx.OK | wx.ICON_ERROR | wx.CENTRE) as dlg:
					dlg.SetIcons(ICON())
					dlg.ShowModal()
				return False

		mainframe = MainFrame(config)
		mainframe.Show()
		return True

if __name__ == '__main__':
	MinecraftClient().MainLoop()
