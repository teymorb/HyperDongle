import wx

class HyperPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent, size=(400, 400))
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.row_obj_dict = {}

        self.list_ctrl = wx.ListCtrl(
            self, size=(284, 200),
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.list_ctrl.InsertColumn(0, 'IP Address', width=140)
        self.list_ctrl.InsertColumn(1, 'MAC Address', width=140)
        main_sizer.Add(self.list_ctrl, 0, wx.ALL | wx.CENTER, 5)
        edit_button = wx.Button(self, label='Scan Local Network For Devices')
        edit_button.Bind(wx.EVT_BUTTON, self.scan_network)
        main_sizer.Add(edit_button, 0, wx.ALL | wx.CENTER, 5)
        self.SetSizer(main_sizer)

    def scan_network(self, event):
        self.list_ctrl.DeleteAllItems()
        from network_scanner import scan
        index = 0
        for res in scan("192.168.1.0/24"):
            self.list_ctrl.InsertItem(index, res['ip'])
            self.list_ctrl.SetItem(index, 1, res['mac'])


class HyperFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Hello World', size=(600, 400))
        self.panel = HyperPanel(self)
        self.Show()


if __name__ == '__main__':
    app = wx.App()
    frame = HyperFrame()
    app.MainLoop()