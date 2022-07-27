# -*- coding: utf-8 -*-

import wx
import numpy as np

class Screen(wx.Panel):
    """示波器显示屏幕"""
    
    def __init__(self, parent, rate=44100):
        """构造函数"""
        
        wx.Panel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        self.SetBackgroundColour(wx.Colour(0, 0, 0))
        self.SetDoubleBuffered(True)
                
        self.parent = parent                        # 父级控件
        self.rate = rate                            # 采样频率
        self.scale = 1024                           # 信号幅度基准
        self.tw = 32                                # 以ms为单位的时间窗口宽度
        self.pos = 0                                # 时间窗口左侧在数据流上的位置
        self.k = int(self.tw*self.rate/1000)        # 时间窗口覆盖的数据点数
        self.leftdown = False                       # 鼠标左键按下
        self.mpos = wx._core.Point()                # 鼠标位置
        self.data = np.array([], dtype=np.int16)    # 音频数据
        self.scrsize = self.GetSize()               # 示波器屏幕宽度和高度
        self.args = self._update()                  # 绘图参数
        self.font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Courier New')
        
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_wheel)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)                
        self.Bind(wx.EVT_MOTION, self.on_mouse_motion)
    
    def _update(self):
        """更新绘图参数"""
        
        u_padding, v_padding, gap = 80, 50, 5           # 示波器屏幕左右留白、上下留白、边框间隙
            
        args = {        
            'b_left': u_padding,                        # 示波器边框左侧坐标
            'b_top': v_padding,                         # 示波器边框顶部坐标
            'b_right': self.scrsize[0] - u_padding,     # 示波器边框右侧坐标
            'b_bottom': self.scrsize[1] - v_padding,    # 示波器边框底部坐标
            'w': self.scrsize[0] - 2*(u_padding+gap),   # 示波器有效区域宽度
            'h': self.scrsize[1] - 2*(v_padding+gap),   # 示波器有效区域高度
            'mid': self.scrsize[1]/2,                   # 水平中心线高度坐标
            'up': v_padding + gap,                      # 示波器有效区域顶部坐标
            'down': self.scrsize[1] - v_padding - gap,  # 示波器有效区域底部坐标
            'left': u_padding + gap,                    # 示波器有效区域左侧坐标
            'right': self.scrsize[0] - u_padding - gap  # 示波器有效区域右侧坐标
        }
        
        x = np.linspace(args['left'], args['right'], self.k)
        y = args['mid'] + (args['h']/2)*self.data[self.pos:self.pos+self.k]/self.scale
        skip = max(self.k//args['w'], 1)
        
        if x.shape[0] > y.shape[0]:
            x = x[:y.shape[0]]
        
        if skip > 1:
            y = y[::skip]
            x = x[::skip]
        
        if y.shape[0] == 0:
            y = np.array([args['mid']])
            x = np.array([u_padding + gap])
        else:
            y = np.where(y < args['up'], args['up'], y)
            y = np.where(y > args['down'], args['down'], y)
        
        args.update({'points':np.stack((x, y), axis=1), 'gu':args['w']/10, 'gv':args['h']/8})
        
        return args
    
    def _check_pos(self):
        """时间窗口位置校正"""
        
        if self.pos < 0 or self.data.data.shape[0] <= self.k:
            self.pos = 0
            self.parent.slider.SetValue(0)
        elif self.pos > self.data.data.shape[0] - self.k:
            self.pos = self.data.data.shape[0] - self.k
            self.parent.slider.SetValue(1000)
        else:
            self.parent.slider.SetValue(int(1000*self.pos/(self.data.data.shape[0] - self.k)))
    
    def on_wheel(self, evt):
        """响应鼠标滚轮调整波形幅度"""
        
        self.scale = self.scale*0.8 if evt.WheelRotation > 0 else self.scale*1.2
        if self.scale < 32:
            self.scale = 32
        if self.scale > 32768:
            self.scale = 32768
        
        self.parent.vknob.SetValue(10 * (np.log2(self.scale)-5))
        self.args = self._update()
        self.Refresh()
    
    def on_left_down(self, evt):
        """响应鼠标左键按下事件"""
        
        self.leftdown = True
        self.mpos = evt.GetPosition()
        
    def on_left_up(self, evt):
        """响应鼠标左键弹起事件"""
        
        self.leftdown = False
        
    def on_mouse_motion(self, evt):
        """响应鼠标移动事件"""
        
        if evt.Dragging() and self.leftdown:
            pos = evt.GetPosition()
            dx, dy = pos - self.mpos
            self.mpos = pos
            
            self.pos -= int(self.k * dx / self.scrsize[0])
            self._check_pos()
            self.args = self._update()
            self.Refresh()
            
    def on_size(self, evt):
        """响应窗口大小变化"""
        
        self.scrsize = self.GetSize()
        self.args = self._update()
        self.Refresh()
    
    def on_paint(self, evt):
        """响应重绘事件"""
        
        dc = wx.PaintDC(self)
        self.plot(dc)
    
    def set_amplitude(self, value):
        """设置幅度缩放比例"""
        
        self.scale = pow(2, 5 + value/10)
        self.args = self._update()
        self.Refresh()
    
    def set_time_width(self, value):
        """设置时间窗口宽度"""
        
        center = self.pos + self.k//2
        self.tw = 0.1 * pow(1.1220184543019633, value)
        self.k = int(self.tw*self.rate/1000)
        self.pos = center - self.k//2
        self._check_pos()
        self.args = self._update()
        self.Refresh()
    
    def append_data(self, data):
        """追加数据"""
        
        self.data = np.hstack((self.data, data))
        self.pos = max(0, self.data.data.shape[0] - self.k)
        self.args = self._update()
        self.Refresh()
    
    def set_pos(self, pos):
        """设置时间窗口位置"""
        
        length = self.data.shape[0] - self.k
        self.pos = int(length*pos/1000) if length > 0 else 0
        self.args = self._update()
        self.Refresh()
        
        if self.pos == 0:
            self.parent.slider.SetValue(0)
    
    def clear(self):
        """清除数据"""
        
        self.data = np.array([], dtype=np.int16)
        self.pos = 0
        self.args = self._update()
        self.Refresh()
    
    def plot(self, dc):
        """绘制屏幕"""
        
        # 绘制中心水平线
        dc.SetPen(wx.Pen(wx.Colour(0,224,0), 1))
        dc.DrawLine(self.args['left'], self.args['mid'], self.args['right'], self.args['mid'])
        
        # 绘制网格
        dc.SetPen(wx.Pen(wx.Colour(64,64,64), 1))
        dc.DrawLineList([(self.args['left']+i*self.args['gu'], self.args['up'], self.args['left']+i*self.args['gu'], self.args['down']) for i in range(0,11)])
        dc.DrawLineList([(self.args['left'], self.args['up']+i*self.args['gv'], self.args['right'], self.args['up']+i*self.args['gv']) for i in [0,1,2,3,5,6,7,8]])
        
        # 绘制数据
        dc.SetPen(wx.Pen(wx.Colour(32,96,255), 1))
        dc.DrawLines(self.args['points'])
        dc.DrawCircle(self.args['points'][-1], 3)
        
        # 绘制外边框
        dc.SetPen(wx.Pen(wx.Colour(224,0,0), 1))
        dc.DrawLines([
            (self.args['b_left'], self.args['b_top']), 
            (self.args['b_right'], self.args['b_top']), 
            (self.args['b_right'], self.args['b_bottom']), 
            (self.args['b_left'], self.args['b_bottom']), 
            (self.args['b_left'], self.args['b_top'])
        ])
        
        # 标注
        dc.SetTextForeground(wx.Colour(224,255,255))
        dc.SetFont(self.font)
        
        top = 100 * self.scale / 32768
        step = top / 4
        for i in range(9):
            label = '%.2f%%'%(top-i*step)
            label_left = label.rjust(8)
            label_right = label.ljust(8)
            dc.DrawText(label_left, self.args['b_left']-70, self.args['up']+i*self.args['gv']-8)
            dc.DrawText(label_right, self.args['b_right']+5, self.args['up']+i*self.args['gv']-8)
        
        start = 1000 * self.pos / self.rate
        step = self.tw / 10
        for i in range(11):
            label = '%.2fms'%(start+i*step)
            label = label.center(12)
            dc.DrawText(label, self.args['left']+i*self.args['gu']-40, self.args['b_top']-25)
            dc.DrawText(label, self.args['left']+i*self.args['gu']-40, self.args['b_bottom']+10)
