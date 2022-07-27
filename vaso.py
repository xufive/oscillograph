# -*- coding: utf-8 -*-

import os
import wx
import queue
import threading
from PIL import ImageGrab

from sample import AudioSampler
from screen import *
from knob import *
from onoff import *
from startstop import *

class MainFrame(wx.Frame):
    """主窗口类"""
    
    def __init__(self, parent):
        """构造函数"""
        
        wx.Frame.__init__(self, parent, -1,style=wx.DEFAULT_FRAME_STYLE)
        
        if wx.DisplaySize()[0] > 1920:
            self.SetSize((1920, 1080))
            self.Center()
        else:
            self.Maximize()
        
        self.SetTitle('音频存储示波器')
        self.SetIcon(wx.Icon('res/wave.ico'))
        self.SetBackgroundColour(wx.Colour(240, 240, 240))
        
        self.works = os.path.join(os.path.dirname(__file__), 'data')
        if not os.path.exists(self.works):
            os.mkdir(self.works)
        
        # 实例化采样器
        self.sample_thread = None
        self.dq = queue.Queue()
        self.sampler = AudioSampler(self.dq)
        
        # 实例化示波器屏幕
        self.screen = Screen(self)
        
        # 创建滑块
        self.slider = wx.Slider(self, -1, 0, 0, 1000, size=wx.DefaultSize, style=wx.SL_HORIZONTAL)
        self.slider.Bind(wx.EVT_SCROLL, self.on_slider)
        
        # 创建宽度调整旋钮
        self.lab_hknob = wx.StaticText(self, -1, '窗口宽度调整', style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.hknob = Knob(self, value=50)
        self.hknob.Bind(EVT_KNOB_ANGLE_CHANGED, self.on_time_width)
        
        # 创建幅度调整旋钮
        self.lab_vknob = wx.StaticText(self, -1, '波形幅度调整', style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.vknob = Knob(self, value=50)
        self.vknob.Bind(EVT_KNOB_ANGLE_CHANGED, self.on_amplitude)
        
        # 创建模式开关
        lab_mode = wx.StaticText(self, -1, '实时模式      触发模式', style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.sw_mode = Switch(self)
        self.sw_mode.Bind(EVT_SWITCH_CHANGED, self.on_switch_mode)
        
        # 触发电平和触发数量
        self.level_rb = wx.RadioBox(self, -1, label='触发电平', choices=['0.05%', '0.1%', '0.2%', '0.5%'], majorDimension=2, style=wx.RA_SPECIFY_COLS, name='level')
        self.over_rb = wx.RadioBox(self, -1, label='触发数量', choices=['1', '2', '5', '10', '20', '50'], majorDimension=3, style=wx.RA_SPECIFY_COLS, name='over')
        self.level_rb.SetSelection(0)
        self.over_rb.SetSelection(0)
        self.level_rb.Enable(False)
        self.over_rb.Enable(False)
        self.Bind(wx.EVT_RADIOBOX, self.on_radio_box)
        
        # 生成启停按钮
        self.btn_star_stop = StartStop(self)
        self.btn_star_stop.Bind(EVT_SS_CHANGED, self.on_star_stop)
        
        # 生成清除|保存|截屏文本按钮
        t_clear = wx.StaticText(self, -1, '清除', name='clear')
        t_s1 = wx.StaticText(self, -1, ' | ')
        t_capture = wx.StaticText(self, -1, '截屏', name='capture')
        t_s2 = wx.StaticText(self, -1, ' | ')
        t_save = wx.StaticText(self, -1, '保存', name='save')
        t_s3 = wx.StaticText(self, -1, ' | ')
        t_open = wx.StaticText(self, -1, '打开', name='open')
        
        t_clear.Bind(wx.EVT_MOUSE_EVENTS, self.on_text_button)
        t_save.Bind(wx.EVT_MOUSE_EVENTS, self.on_text_button)
        t_capture.Bind(wx.EVT_MOUSE_EVENTS, self.on_text_button)
        t_open.Bind(wx.EVT_MOUSE_EVENTS, self.on_text_button)
        
        # 创建布局管理控件
        sizer_max = wx.BoxSizer()                       # 最顶层的布局控件，水平布局
        sizer_left = wx.BoxSizer(wx.VERTICAL)           # 左侧区域布局控件，垂直布局
        sizer_right = wx.BoxSizer(wx.VERTICAL)          # 右侧区域布局控件，垂直布局
        sizer_text = wx.BoxSizer()                      # 右侧底部文本控件，水平布局
        
        # 部件组装
        sizer_left.Add(self.screen, 1, wx.EXPAND|wx.ALL, 0)
        sizer_left.Add(self.slider, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        
        sizer_text.Add(t_clear, 0, wx.ALL, 0)
        sizer_text.Add(t_s1, 0, wx.ALL, 0)
        sizer_text.Add(t_capture, 0, wx.ALL, 0)
        sizer_text.Add(t_s2, 0, wx.ALL, 0)
        sizer_text.Add(t_save, 0, wx.ALL, 0)
        sizer_text.Add(t_s3, 0, wx.ALL, 0)
        sizer_text.Add(t_open, 0, wx.ALL, 0)
        
        sizer_right.Add(self.hknob, 0, wx.TOP, 0)
        sizer_right.Add(self.lab_hknob, 0, wx.EXPAND|wx.TOP, 5)
        sizer_right.Add(self.vknob, 0, wx.TOP, 20)
        sizer_right.Add(self.lab_vknob, 0, wx.EXPAND|wx.TOP, 5)
        sizer_right.Add(self.sw_mode, 0, wx.TOP, 30)
        sizer_right.Add(lab_mode, 0, wx.EXPAND|wx.TOP, 5)
        sizer_right.AddSpacer(15)
        sizer_right.Add(self.level_rb, 0, wx.EXPAND|wx.ALL, 10)
        sizer_right.Add(self.over_rb, 0, wx.EXPAND|wx.ALL, 10)
        sizer_right.Add(wx.Panel(self), 1, wx.ALL, 0)
        sizer_right.Add(self.btn_star_stop, 0, wx.TOP, 10)
        sizer_right.Add(sizer_text, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.TOP, 10)
        
        sizer_max.Add(sizer_left, 1, wx.EXPAND|wx.ALL, 0)
        sizer_max.Add(sizer_right, 0, wx.EXPAND|wx.ALL, 20)
        
        self.SetSizer(sizer_max)
        self.SetAutoLayout(True)
        
        # 启动线程：以阻塞方式从队列中读出数据
        read_thread = threading.Thread(target=self.read_data)
        read_thread.setDaemon(True)
        read_thread.start()
        
        self.Bind(wx.EVT_SIZE, self.on_size)            # 绑定窗口尺寸改变事件
        self.Bind(wx.EVT_CLOSE, self.on_close)          # 绑定窗口关闭事件
    
    def read_data(self):
        """读数据队列的线程函数"""
        
        while True:
            self.screen.append_data(self.dq.get())
        
    def on_close(self, evt):
        """关闭窗口"""
        
        if self.sample_thread and self.sample_thread.isAlive():
            self.ac.stop()
        
        if self.sample_thread:
            self.sample_thread.join()
        
        self.Destroy()
            
    def on_size(self, evt):
        """响应窗口大小变化"""
        
        w, h = self.GetSize()
        
        if h < 960:
            self.level_rb.Show(False)
            self.over_rb.Show(False)
            self.Layout()
        else:
            self.level_rb.Show(True)
            self.over_rb.Show(True)
            self.Layout()
            
        if h < 760:
            self.vknob.Show(False)
            self.lab_vknob.Show(False)
            self.Layout()
        else:
            self.vknob.Show(True)
            self.lab_vknob.Show(True)
            self.Layout()
            
        if h < 580:
            self.hknob.Show(False)
            self.lab_hknob.Show(False)
            self.Layout()
        else:
            self.hknob.Show(True)
            self.lab_hknob.Show(True)
            self.Layout()
    
    def on_star_stop(self, evt):
        """启动停止"""
        
        if self.sampler.running:
            self.sampler.stop()
            self.slider.Enable(True)
        else:
            self.slider.SetValue(1000)
            self.slider.Enable(False)
            
            self.sample_thread = threading.Thread(target=self.sampler.start)
            self.sample_thread.setDaemon(True)
            self.sample_thread.start()
    
    def on_slider(self, evt):
        """拖动滑块"""
        
        self.screen.set_pos(self.slider.GetValue())
    
    def on_amplitude(self, evt):
        """改变幅度缩放比例"""
        
        self.screen.set_amplitude(evt.GetValue())
    
    def on_time_width(self, evt):
        """改变时间窗口宽度"""
        
        self.screen.set_time_width(evt.GetValue())
    
    def on_switch_mode(self, evt):
        """改变模式"""
        
        mode = not bool(evt.GetValue())
        self.sampler.set_args(mode=mode)
        
        if mode:
            self.level_rb.Enable(False)
            self.over_rb.Enable(False)
        else:
            self.level_rb.Enable(True)
            self.over_rb.Enable(True)
        
    def on_radio_box(self, evt):
        """改变触发电平和触发数量"""
        
        objName = evt.GetEventObject().GetName()
        if objName == 'level':
            self.level = self.sampler.set_args(level=[16,32,64,160][evt.GetInt()])
        else:
            self.over = self.sampler.set_args(over=[1,2,5,10,20,50][evt.GetInt()])
    
    def on_text_button(self, evt):
        """响应清除、截屏、保存和打开操作"""
        
        obj = evt.GetEventObject()
        name = obj.GetName()
        
        if evt.Entering():
            obj.SetCursor(wx.Cursor(wx.CURSOR_HAND)) 
        elif evt.Leaving():
            obj.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        
        if evt.LeftUp():
            if name == 'clear':
                self.screen.clear()
                self.slider.SetValue(0)
            elif name == 'capture':
                w, h = self.screen.GetSize()
                im = ImageGrab.grab().crop((3, 25, w-6, h+20))
                
                wildcard = "image file (*.png)|*.png"     
                dlg = wx.FileDialog(self, 
                    message     = '保存图片为...',
                    defaultDir  = self.works, 
                    defaultFile = '',
                    wildcard    = wildcard, 
                    style       = wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
                
                dlg.Center()
                if dlg.ShowModal() == wx.ID_OK: 
                    im.save(dlg.GetPath())
            elif name == 'save':
                wildcard = 'data file (*.npy)|*.npy'
                dlg = wx.FileDialog(self, 
                    message     = '保存数据为...', 
                    defaultDir  = self.works, 
                    defaultFile = '', 
                    wildcard    = wildcard, 
                    style       = wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
                
                dlg.Center()
                if dlg.ShowModal() == wx.ID_OK:
                    np.save(dlg.GetPath(), self.screen.data)
            else:
                wildcard = 'data file (*.npy)|*.npy'    
                dlg = wx.FileDialog(self, 
                    message       = '选择数据文件',
                    defaultDir    = self.works,  
                    defaultFile   = '',
                    wildcard      = wildcard,
                    style         = wx.FD_OPEN 
                )
                
                dlg.Center()
                if dlg.ShowModal() == wx.ID_OK: 
                    self.screen.data = np.array([], dtype=np.int16)
                    self.screen.append_data(np.load(dlg.GetPath()))
                    self.slider.SetValue(1000)

if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame(None)
    frame.Show()
    app.MainLoop()
