#!/usr/bin/python3
import wx
from frames.main import MainFrame
from frames.config import MinecraftConfig
from state import ConfigState
from constants import APP_DESCRIPTION

class MinecraftClient(wx.App):
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
					dlg.ShowModal()
				return False

		mainframe = MainFrame(config)
		mainframe.Show()
		return True

if __name__ == '__main__':
	MinecraftClient().MainLoop()
