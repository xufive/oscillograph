# -*- coding: utf-8 -*-

import pyaudio
import numpy as np

class AudioSampler:
    """音频采样器"""
    
    def __init__(self, dq, rate=44100):
        """构造函数"""
        
        self.dq = dq                                # 数据队列
        self.rate = rate                            # 采样频率
        self.chunk = 1024                           # 数据块大小
        self.mode = 1                               # 模式开关：0 - 触发模式，1 - 实时模式
        self.level = 16                             # 触发模式下的触发阈值
        self.over = 1                               # 触发模式下的触发数量
        self.running = False                        # 采样器工作状态
        
    def set_args(self, **kwds):
        """设置参数"""
        
        if 'mode' in kwds:
            self.mode = kwds['mode']
        
        if 'level' in kwds:
            self.level = kwds['level']
        
        if 'over' in kwds:
            self.over = kwds['over']
    
    def start(self):
        """音频采集"""
        
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format              = pyaudio.paInt16,  # 量化精度（16位，动态范围：-32768~32767）
            channels            = 1,                # 通道数
            rate                = self.rate,        # 采样频率
            frames_per_buffer   = self.chunk,       # pyAudio内部缓存的数据块大小
            input               = True
        )
        
        self.running = True
        self.dq.queue.clear()
        
        while self.running:
            data = stream.read(self.chunk)
            data = np.fromstring(data, dtype=np.int16)
            
            if self.mode or np.sum([data > self.level, data < -self.level]) > self.over:
                self.dq.put(data)
        
        stream.close()
        pa.terminate()
        
    def stop(self):
        """停止采集"""
        
        self.running = False
