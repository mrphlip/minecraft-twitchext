import wx
import os
from utils.minecraft import get_minecraft_user

class MinecraftConfig(wx.Dialog):
	def __init__(self, config, parent=None):
		super().__init__(parent, title="Minecraft World Selection")

		self.real_config = config
		self.config = config.copy()

		self.world_options = []
		self.user_options = []

		sizer = wx.BoxSizer(wx.VERTICAL)

		details = wx.GridSizer(2, 3, 5)
		details.Add(wx.StaticText(self, label='Base Path:'), 1,
			wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
		subsizer = wx.BoxSizer(wx.HORIZONTAL)
		self.lbl_base_path = wx.StaticText(self, label=self.config.minecraftbase,
			style=wx.ST_ELLIPSIZE_START)
		subsizer.Add(self.lbl_base_path, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
		btn_browse = wx.BitmapButton(self,
			bitmap=wx.ArtProvider.GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_BUTTON))
		self.Bind(wx.EVT_BUTTON, self.on_browse, btn_browse)
		subsizer.Add(btn_browse, 0)
		details.Add(subsizer, 1, wx.EXPAND)
		
		details.Add(wx.StaticText(self, label='World:'), 1,
			wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
		self.chs_world = wx.Choice(self, style=wx.ST_ELLIPSIZE_MIDDLE)
		self.Bind(wx.EVT_CHOICE, self.on_choose_world, self.chs_world)
		details.Add(self.chs_world, 1,
			wx.EXPAND)
		
		details.Add(wx.StaticText(self, label='Player:'), 1,
			wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
		self.chs_user = wx.Choice(self, style=wx.ST_ELLIPSIZE_MIDDLE)
		self.Bind(wx.EVT_CHOICE, self.on_choose_user, self.chs_user)
		details.Add(self.chs_user, 1,
			wx.EXPAND)
		
		sizer.Add(details, 1, wx.EXPAND | wx.ALL, 5)

		buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
		if buttons:
			sizer.Add(buttons, 0, wx.EXPAND | wx.BOTTOM, 10)
		
		self.SetSizer(sizer)

		self.SetClientSize(700, self.GetEffectiveMinSize().GetHeight())

		self.btn_ok = wx.Window.FindWindowById(wx.ID_OK, self)
		self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)

		self.refresh_world_list()

	def on_ok(self, event):
		assert self.config.has_minecraft_config()
		self.real_config.minecraftbase = self.config.minecraftbase
		self.real_config.world = self.config.world
		self.real_config.userid = self.config.userid
		self.real_config.save()
		self.EndModal(wx.ID_OK)

	def on_browse(self, event):
		with wx.DirDialog(self, defaultPath=self.lbl_base_path.GetLabel(),
				style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				self.config.minecraftbase = dlg.GetPath()
				self.lbl_base_path.SetLabel(self.config.minecraftbase)
				self.refresh_world_list()

	def on_choose_world(self, event):
		ix = self.chs_world.GetSelection()
		if ix != wx.NOT_FOUND:
			self.config.world = self.world_options[ix]
		else:
			self.config.world = None
		self.refresh_user_list()

	def on_choose_user(self, event):
		ix = self.chs_user.GetSelection()
		if ix != wx.NOT_FOUND:
			self.config.userid = self.user_options[ix]
		else:
			self.config.userid = None
		self.validate()

	def refresh_world_list(self):
		if not self.config.minecraftbase:
			dirs = []
		else:
			savesdir = os.path.join(self.config.minecraftbase, 'saves')
			try:
				dirs = os.listdir(savesdir)
			except FileNotFoundError:
				dirs = []
			else:
				dirs = [
					i for i in dirs
					if os.path.isdir(os.path.join(savesdir, i))
					and i not in {'.', '..'}]
			dirs.sort()

		self.world_options = dirs
		self.chs_world.SetItems(dirs)
		try:
			ix = dirs.index(self.config.world)
		except ValueError:
			self.config.world = None
			self.chs_world.SetSelection(wx.NOT_FOUND)
		else:
			self.chs_world.SetSelection(ix)
		self.refresh_user_list()

	def refresh_user_list(self):
		if not self.config.minecraftbase or not self.config.world:
			userids = usernames = []
		else:
			advdir = os.path.join(self.config.minecraftbase, 'saves', self.config.world, 'advancements')
			try:
				files = os.listdir(advdir)
			except FileNotFoundError:
				files = []
			else:
				files = [
					i for i in files
					if os.path.isfile(os.path.join(advdir, i))
					and i.lower().endswith('.json')]
			users = [(i[:-5], get_minecraft_user(i[:-5])['name']) for i in files]
			users.sort(key=lambda x:x[1])
			userids = [i[0] for i in users]
			usernames = [i[1] for i in users]

		self.user_options = userids
		self.chs_user.SetItems(usernames)
		try:
			ix = userids.index(self.config.userid)
		except ValueError:
			self.config.userid = None
			self.chs_user.SetSelection(wx.NOT_FOUND)
		else:
			self.chs_user.SetSelection(ix)
		self.validate()

	def validate(self):
		self.btn_ok.Enable(self.config.has_minecraft_config())

class TwitchConfig(wx.Dialog):
	def __init__(self, config, parent=None):
		super().__init__(parent, title="Twitch Login")

		self.real_config = config
		self.config = config.copy()

		sizer = wx.BoxSizer(wx.VERTICAL)

		sizer.Add(wx.StaticText(self, label="TODO"), 1, wx.ALIGN_CENTER)

		buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
		if buttons:
			sizer.Add(buttons, 0, wx.EXPAND | wx.BOTTOM, 10)
		
		self.SetSizer(sizer)

		self.SetClientSize(700, self.GetEffectiveMinSize().GetHeight())

		self.btn_ok = wx.Window.FindWindowById(wx.ID_OK, self)
		self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)

	def on_ok(self, event):
		self.real_config.twitchtoken = 'dummy'
		self.real_config.save()
		self.EndModal(wx.ID_OK)
