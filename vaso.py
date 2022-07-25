# -*- coding: utf-8 -*-

import os
import wx
import threading
import queue

from sample import AudioSampler
from screen import Screen
from knob import Knob, EVT_KNOB_ANGLE_CHANGED
from onoff import Switch, EVT_SWITCH_CHANGED
from startstop import StartStop, EVT_SS_CHANGED

class MainFrame(wx.Frame):
    """从wx.Frame派生主窗口类"""
    
    def __init__(self, parent):
        """构造函数"""
        
        wx.Frame.__init__(self, parent, -1,style=wx.DEFAULT_FRAME_STYLE)
        
        if wx.DisplaySize()[0] > 1920:
            self.SetSize((1920, 1080))
            self.Center()
        else:
            self.Maximize()
        
        self.SetTitle('虚拟音频存储示波器')
        self.SetIcon(wx.Icon('res/wave.ico'))
        self.SetBackgroundColour(wx.Colour(240, 240, 240))
        
        works = os.path.join(os.path.dirname(__file__), 'data')
        if not os.path.exists(works):
            os.mkdir(works)
        
        # 实例化采样器
        self.dq = queue.Queue()
        self.sampler = AudioSampler(self.dq, rate=44100)
        
        # 实例化示波器屏幕
        self.screen = Screen(self, rate=44100)
        
        # 创建滑块
        self.slider = wx.Slider(self, -1, 0, 0, 100, size=wx.DefaultSize, style=wx.SL_HORIZONTAL)
        self.slider.Bind(wx.EVT_SCROLL, self.on_slider)
        
        # 创建幅度调整旋钮
        lab_vknob = wx.StaticText(self, -1, '波形幅度调整', style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.vknob = Knob(self)
        self.vknob.Bind(EVT_KNOB_ANGLE_CHANGED, self.on_amplitude)
        
        # 创建宽度调整旋钮
        lab_hknob = wx.StaticText(self, -1, '窗口宽度调整', style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.hknob = Knob(self)
        self.hknob.Bind(EVT_KNOB_ANGLE_CHANGED, self.on_time_width)
        
        # 创建模式开关
        lab_mode = wx.StaticText(self, -1, '实时模式      触发模式', style=wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.sw_mode = Switch(self)
        self.sw_mode.Bind(EVT_SWITCH_CHANGED, self.on_switch_mode)
        
        # 生成启停按钮
        self.btn_star_stop = StartStop(self)
        self.btn_star_stop.Bind(EVT_SS_CHANGED, self.on_star_stop)
        
        # 创建布局管理控件
        sizer_max = wx.BoxSizer()                       # 最顶层的布局控件，水平布局
        sizer_left = wx.BoxSizer(wx.VERTICAL)           # 左侧区域布局控件，垂直布局
        sizer_right = wx.BoxSizer(wx.VERTICAL)          # 右侧区域布局控件，垂直布局
        
        # 部件组装
        sizer_left.Add(self.screen, 1, wx.EXPAND|wx.ALL, 0)
        sizer_left.Add(self.slider, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        
        sizer_right.Add(self.vknob, 0, wx.TOP, 0)
        sizer_right.Add(lab_vknob, 0, wx.EXPAND|wx.TOP, 5)
        sizer_right.Add(self.hknob, 0, wx.TOP, 30)
        sizer_right.Add(lab_hknob, 0, wx.EXPAND|wx.TOP, 5)
        sizer_right.Add(self.sw_mode, 0, wx.TOP, 30)
        sizer_right.Add(lab_mode, 0, wx.EXPAND|wx.TOP, 5)
        sizer_right.Add(wx.Panel(self), 1, wx.ALL, 0)
        sizer_right.Add(self.btn_star_stop, 0, wx.BOTTOM, 40)
        
        sizer_max.Add(sizer_left, 1, wx.EXPAND|wx.ALL, 0)
        sizer_max.Add(sizer_right, 0, wx.EXPAND|wx.ALL, 20)
        
        self.SetSizer(sizer_max)
        self.SetAutoLayout(True)
        
        # 启动线程：以阻塞方式从队列中读出数据
        read_thread = threading.Thread(target=self.read_data)
        read_thread.setDaemon(True)
        read_thread.start()
    
    def read_data(self):
        """读数据队列的线程函数"""
        
        while True:
            self.screen.append_data(self.dq.get())
    
    def on_star_stop(self, evt):
        """启动停止"""
        
        if self.sampler.running:
            self.sampler.stop()
            self.slider.Enable(True)
        else:
            self.screen.clear()
            self.slider.SetValue(100)
            self.slider.Enable(False)
            
            capture_thread = threading.Thread(target=self.sampler.start)
            capture_thread.setDaemon(True)
            capture_thread.start()
    
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
        
        self.sampler.set_args(mode=not bool(evt.GetValue()))
        

if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame(None)
    frame.Show()
    app.MainLoop()
