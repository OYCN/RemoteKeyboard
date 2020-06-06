# '''
# A P2P Server with single direction
# #
#
# # \x01: ensure for online
# # \x02: response for \x01
# # \x03: ask for auth
# # \x04: need length of token (bytes)
# # \xXX: length of token, max(length) = 255B
# # \x05: need token
# # \xXX: token
# # \x06: token access & auth session over
# # \x07: token failed & auth session over
# # \xXXXX: password => \x05\x02
# # \xXX: room and role:
#     0b X 000 0000
#        ^ ^^^ ^^^^
#        |  room number
#        0 -> sender
#        1 -> recver
# \xXXXX: key msg:
#     0b X000 0000 XXXX XXXX
#        ^         ^^^^ ^^^^
#      status        KeyNum
#
# time:
#     1 auth
#     2 room & role
#     3 check online
# '''

import socket
import multiprocessing
import threading
import logging

# logger = logging.getLogger('P2PSD')
# logger.setLevel(logging.DEBUG)
# logger.debug('start')

def p2psdRun(clients, roomNum, thdCallbackQ):
    sender = clients['sender']
    recver = clients['recver']
    sender.setblocking(False)

    # 清空缓冲区
    while True:
        try:
            sender.recv(1024)
        except BlockingIOError:
            break
        except Exception as e:
            thdCallbackQ.put((roomNum, 'sender'))
            print(f'room:{roomNum} sender close with {str(e)}')
            return

    # recver.setblocking(False)
    while True:
        try:
            res = sender.recv(1024)
        except BlockingIOError:
            res = ''
        except Exception as e:
            thdCallbackQ.put((roomNum, 'sender'))
            print(f'room:{roomNum} sender close with {str(e)}')
            return

        try:
            if res != '':
                recver.sendall(res)
            else:
                recver.sendall(b'\x00\x00')
        except BlockingIOError:
            pass
        except Exception as e:
            thdCallbackQ.put((roomNum, 'recver'))
            print(f'room:{roomNum} recver close with {str(e)}')
            return

def roomRole(clientsQ, thdCallbackQ):
    '''
    分辨客户端请求和类型，放入响应房间
    :param clientsQ:
    :param roomsM:
    :return:
    '''
    rooms = {}
    while True:
        if (not thdCallbackQ.empty()):
            tmp = thdCallbackQ.get()
            rooms[tmp[0]].pop(tmp[1])
            print(f'clean {tmp[1]} @ room: {tmp[0]}')
        if(not clientsQ.empty()):
            raw_client = clientsQ.get()
            client = raw_client[0]
            # logger.debug(f'{raw_client[0]} connect')
            print(f'{raw_client[1]} connect')
            # 验证密钥
            if client.recv(2) == b'\x05\x02':
                res = client.recv(1)[0]
                role = 'recver' if (res & 0x80) == 0x80 else 'sender'
                roomNum = int(res & 0x7F)
                client.send(b'\x01')
                print(f'{raw_client[1]} access @room: {roomNum} with {role}')


                # 房间
                if rooms.get(roomNum) == None: rooms[roomNum] = {}
                # 类型
                if rooms[roomNum].get(role) == None:
                    rooms[roomNum][role] = client
                    if (len(rooms[roomNum].keys()) == 2):
                        # logger.debug(f'creat room: {number}')
                        print(f'creat room: {roomNum}')
                        p = threading.Thread(target=p2psdRun, args=(rooms[roomNum], roomNum, thdCallbackQ))
                        p.start()
                    else:
                        print(f'room: {roomNum} len is {len(rooms[roomNum].keys())}, can\'t created')
                else:
                    try:
                        rooms[roomNum].get(role).send(b'\x00\x00')
                    except:
                        rooms[roomNum].pop(role)
                        print(f'{raw_client[1]} need retry: {rooms[roomNum].get(role)}')
                        client.close()
                    else:
                        print(f'{raw_client[1]} role already using: {rooms[roomNum].get(role)}')
                        client.close()
            else:
                print(f'{raw_client[1]} pwd error')
                client.close()

if __name__ == '__main__':
    # 全部房间
    # roomsM = multiprocessing.Manager().dict()
    clientsQ = multiprocessing.Queue()
    thdCallbackQ = multiprocessing.Queue()
    processList = []
    # logger.info('roomRole process creat')
    print('roomRole process creat')
    processList.append(multiprocessing.Process(target=roomRole, args=(clientsQ, thdCallbackQ)))

    for p in processList:
        p.start()

    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s = socket.socket()
    s.bind(('127.0.0.1', 8888))
    s.listen(2)
    # logger.info('start listen')
    print('start listen')
    while True:
        clientsQ.put(s.accept())

