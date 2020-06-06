from __future__ import print_function
import time
import ctypes, sys
import socket

maps = {
    192: 200,  # Oem_3
    49: 201,  # 1
    50: 202,  # 2
    51: 203,  # 3
    52: 204,  # 4
    53: 205,  # 5
    54: 206,  # 6
    55: 207,  # 7
    56: 208,  # 8
    57: 209,  # 9
    48: 210,  # 0
    189: 211,  # Oem_Minus
    187: 212,  # Oem_Plus
    220: 213,  # Oem_5
    8: 214,  # Back
    9: 300,  # Tab
    81: 301,  # Q
    87: 302,  # W
    69: 303,  # E
    82: 304,  # R
    84: 305,  # T
    89: 306,  # Y
    85: 307,  # U
    73: 308,  # I
    79: 309,  # O
    80: 310,  # P
    219: 311,  # Oem_4
    221: 312,  # Oem_6
    20: 400,  # Capital
    65: 401,  # A
    83: 402,  # S
    68: 403,  # D
    70: 404,  # F
    71: 405,  # G
    72: 406,  # H
    74: 407,  # J
    75: 408,  # K
    76: 409,  # L
    186: 410,  # Oem_1
    222: 411,  # Oem_7
    13: 313,  # Return
    160: 500,  # Lshift
    90: 501,  # Z
    88: 502,  # X
    67: 503,  # C
    86: 504,  # V
    66: 505,  # B
    78: 506,  # N
    77: 507,  # M
    188: 508,  # Oem_Comma
    190: 509,  # Oem_Period
    191: 510,  # Oem_2
    161: 511,  # Rshift
    162: 600,  # Lcontrol
    164: 602,  # Lmenu
    32: 603,  # Space
    165: 604,  # Rmenu
    163: 607,  # Rcontrol
}

class Simul:
    def __init__(self):
        self.success = False
        if self.is_admin():
            try:
                self.dd_dll = ctypes.windll.LoadLibrary('D:\pycharm\RemoteKeyBoard\DD94687.64.dll')
            except Exception as e:
                input('dll加载失败，可能重复加载', str(e))
                exit()
            self.success = True
        else:
            if sys.version_info[0] == 3:
                exit(ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1))
            else:  # in python2.x
                exit(ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(__file__), None, 1))

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
                return False

    def down(self, code):
        self.dd_dll.DD_key(code, 1)

    def up(self, code):
        self.dd_dll.DD_key(code, 2)

    def down_up(self, code):
        self.down(code)
        self.up(code)

    def autoPress(self, isup, key):
        if isinstance(key, int):
            if(isup):
                self.up(key)
            else:
                self.down(key)

class RemoteNet:
    def __init__(self, ipaddress, port, token=None):
        self.server = socket.socket()
        try:
            self.server.connect((ipaddress, port))
            self.server.send(b'\x05\x02')
            self.server.send(b'\x80')
            if self.server.recv(1) == b'\x01':
                self.success = True
            else:
                self.success = False
        except:
            self.success = False

    def isOnline(self):
        self.server.send(b'\x01')
        if self.server.recv(2) == b'\x02':
            return True
        return False

    def recv(self):
        msg = self.server.recv(2)
        if(msg!=b'\x00\x00'):
            # print(int.from_bytes(msg,'big'))
            isup = msg[0]&0x80 != 0
            # key = int.from_bytes(msg,'big')&0x7F
            key = msg[1]
            return (isup, key)
        return

if __name__ == '__main__':
    keyboard = Simul()
    if keyboard.success:
        # net = RemoteNet('', 7777)
        net = RemoteNet('127.0.0.1', 8888)
        if net.success == False:
            input('connect serror')
            exit()
        while True:
            res = net.recv()
            if isinstance(res, tuple):
                print(res[0], res[1], maps.get(res[1]))
                # keyboard.autoPress(res[0], maps.get(res[1]))