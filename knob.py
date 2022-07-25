# -*- coding: utf-8 -*-

import wx
import numpy as np

wxEVT_KNOB_ANGLE_CHANGED = wx.NewEventType()
EVT_KNOB_ANGLE_CHANGED = wx.PyEventBinder(wxEVT_KNOB_ANGLE_CHANGED, 1)

class KnobEvent(wx.CommandEvent):
    """自定义旋钮事件类"""

    def __init__(self, eventType, eventId=1):
        """构造函数"""

        wx.CommandEvent.__init__(self, eventType, eventId)
    
    def SetValue(self, value):
        """设置当前值"""

        self._value = value
    
    def GetValue(self):
        """返回当前值"""

        return self._value

class Knob(wx.Panel):
    """旋钮"""
    
    def __init__(self, parent, id=wx.ID_ANY, value=50, pos=wx.DefaultPosition, size=(150,150)):
        """构造函数"""
        
        wx.Panel.__init__(self, parent, id, pos, size, style=wx.NO_FULL_REPAINT_ON_RESIZE)
        
        self.bmp_wp = wx.Bitmap('res/wpoint.png', wx.BITMAP_TYPE_ANY)
        self.bmp_bp = wx.Bitmap('res/bpoint.png', wx.BITMAP_TYPE_ANY)
        self.bmp_rp = wx.Bitmap('res/rpoint.png', wx.BITMAP_TYPE_ANY)
        self.bmp_core = wx.Bitmap('res/knob.png', wx.BITMAP_TYPE_ANY)
        
        self._state = 0
        self._value = value
        self._angle = -60, 240
        self.args = self._update()
        self.Refresh()
        
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse_event)
    
    def _update(self):
        """更新重绘参数"""
        
        w, h = self.GetSize()
        r = min(w, h)/2 - 5
        origin = w/2, h/2
        
        theta = np.radians(np.linspace(*self._angle, 15))
        x = r * np.cos(theta) + origin[0]
        y = -r * np.sin(theta) + origin[1]
        
        a = np.radians(self._angle[1] - (self._angle[1] - self._angle[0]) * self._value / 100)
        ax = r * np.cos(a) * 0.5 + origin[0]
        ay = -r * np.sin(a) * 0.5 + origin[1]
        
        k = np.where(theta >= a)[0][0]
        if self._value == 0:
            k += 1
        
        return {'points': np.stack((x, y), axis=1), 'origin': origin, 'r': r, 'curr': (ax, ay), 'k': k}
    
    def SetValue(self, value):
        """设置当前值"""
        
        self._value = value
        self.args = self._update()
        self.Refresh()
    
    def GetValue(self):
        """返回当前值"""
        
        return self._value
    
    def on_mouse_event(self, evt):
        """响应鼠标事件"""
        
        if self._state == 0 and evt.Entering():
            self._state = 1
        elif self._state >= 1 and evt.Leaving():
            self._state = 0
        elif self._state == 2 and evt.LeftUp():
            self._state = 1
        elif self._state == 1 and evt.LeftDown() or self._state == 2 and evt.LeftIsDown():
            self._state = 2
            x, y = evt.GetPosition()
            dx, dy = x - self.args['origin'][0], self.args['origin'][1] - y
            
            if dx == 0:
                angle = 90 if dy > 0 else -90
            else:
                angle = np.degrees(np.arctan(dy/dx)) if dx > 0 else np.degrees(np.arctan(dy/dx)) + 180
            
            if (self._angle[0]-10) < angle < self._angle[0]:
                angle = self._angle[0]
            
            if self._angle[1] < angle < (self._angle[1]+10):
                angle = self._angle[1]
            
            if self._angle[0] <= angle <= self._angle[1]:
                self._value = 100 * (self._angle[1] - angle) / (self._angle[1] - self._angle[0])
                self.args = self._update()
                self.Refresh()
                
                event = KnobEvent(wxEVT_KNOB_ANGLE_CHANGED, self.GetId())
                event.SetEventObject(self)
                event.SetValue(self._value)
                self.GetEventHandler().ProcessEvent(event)
    
    def on_size(self, evt):
        """响应控件改变大小"""
        
        self.args = self._update()
        self.Refresh()
    
    def on_paint(self, evt):
        """响应重绘事件"""
        
        dc = wx.PaintDC(self)
        
        for i in range(self.args['points'].shape[0]):
            if i < self.args['k']:
                dc.DrawBitmap(self.bmp_bp, self.args['points'][i][0]-5, self.args['points'][i][1])
            else:
                dc.DrawBitmap(self.bmp_wp, self.args['points'][i][0]-5, self.args['points'][i][1])
        
        dc.DrawBitmap(self.bmp_core, self.args['origin'][0]-60, self.args['origin'][1]-60)
        dc.DrawBitmap(self.bmp_rp, self.args['curr'][0]-5, self.args['curr'][1])
        
        dc.DrawText('MIN', self.args['points'][-1][0]-35, self.args['points'][-1][1]-5)
        dc.DrawText('MAX', self.args['points'][0][0]+10, self.args['points'][0][1]-5)
    