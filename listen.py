import PyHook3
import pythoncom
import socket

s = socket.socket()
s.connect(('127.0.0.1',8888))
s.send(b'\x05\x02')
s.send(b'\x00')
if s.recv(1) != b'\x01':
    exit('connect error')

hm = PyHook3.HookManager()

def temp(event):
    print('MessageName:',event.MessageName)          #同上，共同属性不再赘述
    print('Message:',event.Message)
    print('Time:',event.Time)
    print('Window:',event.Window)
    print('WindowName:',event.WindowName)
    print('Ascii:', event.Ascii, chr(event.Ascii))   #按键的ASCII码
    print('Key:', event.Key)                         #按键的名称
    print('KeyID:', event.KeyID)                     #按键的虚拟键值
    print('ScanCode:', event.ScanCode)               #按键扫描码
    print('Extended:', event.Extended)               #判断是否为增强键盘的扩展键
    print('Injected:', event.Injected)
    print('Alt', event.Alt)                          #是某同时按下Alt
    print('Transition', event.Transition)            #判断转换状态
    print('---')
    return True

mapping = {}

def KeyAll_filter(event):
    if(mapping.get(event.KeyID)==None): mapping[event.KeyID] = -1
    isup = event.Transition==0x80
    if(mapping[event.KeyID] != isup):
        if(isup): print(event.Key + ':' + str(event.KeyID) + ' Up: ' + str(isup))
        else: print(event.Key + ':' + str(event.KeyID) + ' Down: ' + str(isup))
    mapping[event.KeyID] = isup
    return True

def KeyAll(event):
    isup = event.Transition << 8
    msg = (isup + event.KeyID).to_bytes(length=2, byteorder='big')
    # print(bin(event.KeyID))
    # print(bin(isup))
    # print(bin(isup + event.KeyID))
    # print(msg)
    s.send(msg)
    return True

hm.SubscribeKeyAll(KeyAll)
hm.HookKeyboard()

pythoncom.PumpMessages()

while True:
    pass