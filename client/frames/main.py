import wx
from constants import APP_DESCRIPTION
from frames.config import MinecraftConfig, TwitchConfig
from utils.minecraft import get_minecraft_user, get_minecraft_icon
from utils.twitch import get_twitch_data
from utils.worker import send_update
import io

class MainFrame(wx.Frame):
	def __init__(self, config):
		super().__init__(None, title=APP_DESCRIPTION,
			style=wx.DEFAULT_FRAME_STYLE & ~(wx.MAXIMIZE_BOX | wx.RESIZE_BORDER)
			)

		self.config = config

		sizer = wx.BoxSizer(wx.VERTICAL)

		details = wx.GridSizer(2, 3, 5)
		details.Add(wx.StaticText(self, label='Base Path:'), 1, wx.ALIGN_RIGHT)
		self.lbl_base_path = wx.StaticText(self, style=wx.ST_ELLIPSIZE_START)
		details.Add(self.lbl_base_path, 1, wx.EXPAND)
		
		details.Add(wx.StaticText(self, label='World:'), 1, wx.ALIGN_RIGHT)
		self.lbl_world = wx.StaticText(self, style=wx.ST_ELLIPSIZE_MIDDLE)
		details.Add(self.lbl_world, 1, wx.EXPAND)
		
		details.Add(wx.StaticText(self, label='Player:'), 1, wx.ALIGN_RIGHT)
		subsizer = wx.BoxSizer(wx.HORIZONTAL)
		self.img_user = wx.StaticBitmap(self)
		subsizer.Add(self.img_user, 0, wx.ALIGN_CENTRE | wx.RIGHT, 5)
		self.lbl_user = wx.StaticText(self, style=wx.ST_ELLIPSIZE_END)
		subsizer.Add(self.lbl_user, 1, wx.EXPAND)
		details.Add(subsizer, 1, wx.EXPAND)
		
		details.Add(wx.StaticText(self, label='Twitch channel:'), 1, wx.ALIGN_RIGHT)
		self.lbl_twitchuser = wx.StaticText(self, style=wx.ST_ELLIPSIZE_END)
		details.Add(self.lbl_twitchuser, 1, wx.EXPAND)

		sizer.Add(details, 0, wx.EXPAND | wx.ALL, 5)
		
		btn_mc_config = wx.Button(self, label='Change Minecraft World')
		self.Bind(wx.EVT_BUTTON, self.on_click_mc_config, btn_mc_config)
		sizer.Add(btn_mc_config, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

		btn_twitch_config = wx.Button(self, label='Change Twitch Channel')
		self.Bind(wx.EVT_BUTTON, self.on_click_twitch_config, btn_twitch_config)
		sizer.Add(btn_twitch_config, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

		btn_do_post = wx.Button(self, label='do post')
		self.Bind(wx.EVT_BUTTON, lambda e:send_update(self.config), btn_do_post)
		sizer.Add(btn_do_post, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

		btn_exit = wx.Button(self, wx.ID_CANCEL, label='Exit')
		self.Bind(wx.EVT_BUTTON, self.on_click_exit, btn_exit)
		sizer.Add(btn_exit, 1, wx.EXPAND | wx.ALL, 10)
		self.SetSizer(sizer)

		self.SetSize(800, sizer.ComputeFittingWindowSize(self).height)

		self.update_config()

	def update_config(self):
		self.lbl_base_path.SetLabel(self.config.minecraftbase or '')
		self.lbl_world.SetLabel(self.config.world or '')
		if self.config.userid:
			self.lbl_user.SetLabel(get_minecraft_user(self.config.userid)['name'])
			img = get_minecraft_icon(self.config.userid)
			if img:
				#img = wx.Bitmap.NewFromPNGData(img, len(img))
				img = wx.Image(io.BytesIO(img), wx.BITMAP_TYPE_PNG)
				img.Rescale(16, 16, wx.IMAGE_QUALITY_NEAREST)
				self.img_user.SetBitmap(img.ConvertToBitmap())
			else:
				self.img_user.SetBitmap(wx.NullBitmap)
		else:
			self.lbl_user.SetLabel('')
			self.img_user.SetBitmap(wx.NullBitmap)
		self.lbl_twitchuser.SetLabel(get_twitch_data(self.config.twitchtoken)['name'])
		self.SendSizeEvent()

	def on_click_exit(self, event):
		self.Close()

	def on_click_mc_config(self, event):
		with MinecraftConfig(self.config) as dlg:
			dlg.ShowModal()
		self.update_config()

	def on_click_twitch_config(self, event):
		with TwitchConfig(self.config) as dlg:
			dlg.ShowModal()
		self.update_config()
