import socket
import struct
import json
import threading, time, datetime
import pyautogui
import logging

logging.basicConfig(filename='gb.log',level=logging.INFO)

 
tt = 0.001
IP_PORT = ('127.0.0.1', 8888)
buffer_size = 1024 * 8
is_Connect = 0
lock = threading.Lock()

class ChatMessageType():
    Text = 0
    FileInfo = 1
    FileContent = 2
    Shake = 3
    FileEnd = 4
    BroadCast = 5
    Verify = 6
    Command = 7
    CameraHandle = 8
    CameraPic = 9
    CameraBegin = 10
    CameraContent = 11
    CameraEnd = 12
    Gp = 13
  
def Pack(Type, Data, Args):   #Data是bytes Args是string
    DataLen = len(Data)  # DataLen 0<= ? <= 65535
    _Args = bytes(Args, "utf-8")
    ArgsLen = len(_Args)  # ArgsLen 0<= ? <= 65535
    bytes_re = struct.pack('<BHH', Type, DataLen, ArgsLen) + bytes(Data) + _Args
    return bytes_re
  
def UnPack(_bytes):
    Type, DataLen, ArgsLen = struct.unpack('<BHH', _bytes[0:5])
    return Type, DataLen, ArgsLen
 
def PackMsg(conn, Type, Data, Args):
    req = Pack(Type,Data,Args)
    conn.send(req)
    #print(f"<<--Type:{Type}, Data:{Data.decode('utf-8')}, Args:{Args}")
    
def check_it(conn):
    req = Pack(ChatMessageType.Verify, b'', "benben")
    conn.send(req)
    
def auto_buy(stock_code, amount):
    # 点击买入
    pyautogui.click(x=45, y=83) #点击买入
    time.sleep(tt)    
    pyautogui.click(x=305, y=122) #点击证券代码
    time.sleep(tt)
    # 输入股票代码
    pyautogui.typewrite(stock_code)
    time.sleep(tt)
    pyautogui.press('enter')
    time.sleep(tt)
    pyautogui.press('enter')
    time.sleep(tt)
    # 输入买入数量
    pyautogui.typewrite(str(amount))
    time.sleep(tt)
    # 确认买入
    pyautogui.click(x=338, y=243)
    time.sleep(tt)
    pyautogui.click(x=900, y=617)

def auto_sell(stock_code, amount):
    #  点击卖出
    pyautogui.click(x=52, y=100)
    time.sleep(tt)
    pyautogui.click(x=305, y=122) #点击证券代码
    time.sleep(tt)
    # 输入股票代码
    pyautogui.typewrite(stock_code)
    time.sleep(tt)
    pyautogui.press('enter')
    time.sleep(tt)
    pyautogui.press('enter')
    time.sleep(tt)
    # 输入卖出数量
    pyautogui.typewrite(str(amount))
    time.sleep(tt)
    # 确认买入
    pyautogui.click(x=338, y=243)
    time.sleep(tt)
    pyautogui.click(x=900, y=617)
    
#获取当前时间
def get_now():
    from datetime import datetime
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_datetime
    
def send_msg(s, send_data):
    send_data = send_data.encode('utf-8')
    req1=Pack(ChatMessageType.Text, send_data, "dirs")
    s.send(req1)  
    
def recv_it(conn):
    global buffer_size, is_Connect
    
    while True:
        bytes_video = b''
        file_dict = {}
        recvfile_size = 0
        while True:
            total_data = b''
            Data = b''
            Args = b''
            num = 0
     
            # 1.#先收5个字节
            total_length = 5
            received_length = 0
            data_list = []
            while received_length < total_length:
                _data = conn.recv(total_length - received_length)
                if not _data:  #如果连接断开
                    print('对方已断开连接')
                    lock.acquire()
                    is_Connect = 0
                    lock.release()
                    return None
                received_length += len(_data)
                data_list.append(_data)
            complete_data = b''.join(data_list)
            data_head = complete_data
            # data_head = conn.recv(5)
            if not data_head:
                break
     
            # 2.拆包
            # Type,DataLen,ArgsLen,Data,Args = UnPack(data)   #拆包
            Type, DataLen, ArgsLen = UnPack(data_head)  # 拆包
     
            total_data += data_head
            # print("total_data:", len(total_data))
            # print(DataLen)
     
            # 3.接收Data
            file_size = DataLen
            recv_size = 0
            while recv_size < file_size:
                # 2.拆包
                left_size = file_size - recv_size
                if (left_size > buffer_size):  # 如果剩下超过一个buf
                    frame = conn.recv(buffer_size)
                else:
                    frame = conn.recv(left_size)
                if not frame:
                    break
     
                Data += frame
                recv_size += len(frame)
     
            # 4. 接收Args
            file_size = ArgsLen
            recv_size = 0
            while recv_size < file_size:
                # 2.拆包
                left_size = file_size - recv_size
                if (left_size > buffer_size):  # 如果剩下超过一个buf
                    frame = conn.recv(buffer_size)
                else:
                    frame = conn.recv(left_size)
                if not frame:
                    break
     
                Args += frame
                recv_size += len(frame)
     
            total_data += Data + Args
            # print("totel:", len(total_data))
     
            # 3.收Data Args
            #print(f"Type:{Type}, DataLen:{DataLen}, ArgsLen:{ArgsLen}, Args:{Args}")
            num += 5 + DataLen + ArgsLen
            data = data_head + Data + Args

            # 5.打印
            if Type == 0 or Type == 5 or Type == 7 or Type == 6:
                if len(Data) > 10:
                    print(f"--->Recv Type = {Type} DataLen = {DataLen} ArgsLen = {ArgsLen} Data = [{Data}] Args = {Args.decode('utf-8')}")
                else:
                    print(f"--->Recv Type = {Type} DataLen = {DataLen} ArgsLen = {ArgsLen} Data = [] Args = {Args.decode('utf-8')}")
                
            if Type == ChatMessageType.Text:
                print(Data.decode('utf-8'))
                pass
            elif Type == ChatMessageType.Command:
                m = Data.decode('utf-8')
                if m == "ping":
                    send_msg(conn, "pong")

            elif (Type == ChatMessageType.Gp):
                print(f"--->Recv Type = {Type} DataLen = {DataLen} ArgsLen = {ArgsLen} Data = [{Data}] Args = {Args.decode('utf-8')}")
                m = Data.decode('utf-8')
                if m == 'exit':
                    exit()
                    pass
                else:
                    s = json.loads(m)
                    #print(type(s))
                    
                    
                    if len(s) >= 1:
                        for ss in s:
                            #print(ss)
                            if ss['action'] == 'buy':
                                stock = ss['zqdm'][:6]
                                num = ss['qty']
                                strategy = ss['strategy']
                                trade_time = ss['trade_time']
                                now_time = ss['time']
                    
                                logging.info(f'%s %s %s %s %s %s' % (stock, num, 'buy',trade_time, strategy, now_time))
                                #auto_buy(stock, num)
                            elif ss['action'] == 'sell':
                                stock = ss['zqdm'][:6]
                                num = ss['qty']
                                strategy = ss['strategy']
                                trade_time = ss['trade_time']
                                now_time = ss['time']
                                
                                logging.info(f'%s %s %s %s %s %s' % (stock, num, 'sell',trade_time, strategy, now_time))
                                #auto_sell(stock, num)
                
                print(Data.decode('utf-8'))
                pass
                

        
def run():
    
    while True:
        try:
            conn = socket.socket(socket.AF_INET,  socket.SOCK_STREAM)
            ret = conn.connect_ex(IP_PORT)  #连接服务端端口

            if ret==0:
                global is_Connect
                is_Connect = 1
                print("conn successfully")
                #启动一个线程来接收
                th = threading.Thread(target=recv_it, args=(conn,))
                th.setDaemon(True)
                th.start()
                
                check_it(conn)  #验证
                print("verify success")
                
                while True:
                    # 1、发命令
                    cmd = input('').strip()  # 'get a.txt'
                    if not cmd:continue
                        
                    if(cmd == 'video'):
                        PackMsg(conn, ChatMessageType.Command, b'', cmd)
                    elif(cmd == 'stop'):
                        PackMsg(conn, ChatMessageType.Command, b'', cmd)
                    elif(cmd == 'exit'):
                        PackMsg(conn, ChatMessageType.Command, b'', cmd)
                        exit(0)
                    elif (cmd == 'off'):
                        PackMsg(conn, ChatMessageType.Command, b'', cmd)
                        exit(0)
                    else:
                        #print("send" + cmd)
                        PackMsg(conn, ChatMessageType.Command, b'', cmd)
                    #client.send(cmd.encode('utf-8'))
             
             
                conn.close()

                #th.join()
                print('主线程检测到子线程退出')

                conn.close()
            else:
                print("conn failture")
        except (ConnectionRefusedError, OSError) as e:
            print(f"Connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)  # 等待一段时间后重试
        
if __name__ == '__main__':
    run()