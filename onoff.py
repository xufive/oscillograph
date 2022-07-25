# -*- coding: utf-8 -*-

import wx

wxEVT_SWITCH_CHANGED = wx.NewEventType()
EVT_SWITCH_CHANGED = wx.PyEventBinder(wxEVT_SWITCH_CHANGED, 1)

class SwitchEvent(wx.CommandEvent):
    """自定义开关事件类"""

    def __init__(self, eventType, eventId=1):
        """构造函数"""

        wx.CommandEvent.__init__(self, eventType, eventId)
    
    def SetValue(self, value):
        """设置当前值"""

        self._value = value
    
    def GetValue(self):
        """返回当前值"""

        return self._value

class Switch(wx.Panel):
    """开关"""
    
    def __init__(self, parent, id=wx.ID_ANY, value=0, pos=wx.DefaultPosition, size=(150,60)):
        """构造函数"""
        
        wx.Panel.__init__(self, parent, id, pos, size, style=wx.NO_FULL_REPAINT_ON_RESIZE)
        
        self.bmp_s0 = wx.Bitmap('res/switch_0.png', wx.BITMAP_TYPE_ANY)
        self.bmp_s1 = wx.Bitmap('res/switch_1.png', wx.BITMAP_TYPE_ANY)
        
        self._value = value
        self.csize = self.GetSize()
        self.Refresh()
        
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_UP, self.on_lefte_up)
    
    def SetValue(self, value):
        """设置当前值"""
        
        self._value = value
        self.args = self._update()
        self.Refresh()
    
    def GetValue(self):
        """返回当前值"""
        
        return self._value
    
    def on_lefte_up(self, evt):
        """响应鼠标事件"""
        
        x, y = evt.GetPosition()
        if x < self.csize[0]/2 and self._value == 1 or x >= self.csize[0]/2 and self._value == 0:
            self._value = 0 if self._value == 1 else 1
            self.Refresh()
            
            event = SwitchEvent(wxEVT_SWITCH_CHANGED, self.GetId())
            event.SetEventObject(self)
            event.SetValue(self._value)
            self.GetEventHandler().ProcessEvent(event)
    
    def on_size(self, evt):
        """响应控件改变大小"""
        
        self.csize = self.GetSize()
        self.Refresh()
    
    def on_paint(self, evt):
        """响应重绘事件"""
        
        dc = wx.PaintDC(self)
        p = self.csize[0]/2 - 60, self.csize[1]/2 - 27
        
        if self._value == 0:
            dc.DrawBitmap(self.bmp_s0, *p)
        else:
            dc.DrawBitmap(self.bmp_s1, *p)
        
    