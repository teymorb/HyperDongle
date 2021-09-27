import wx
from app import HyperFrame
import threading
from ReverseTunnel import main_func

app = wx.App()
frame = HyperFrame()
app_thread = threading.Thread(target=main_func, args=("ec2-user", "54.167.166.244", "../open-key-pair.pem", "localhost:22"))
app_thread.start()
app.MainLoop()