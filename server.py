import socket
import threading
from queue import Queue
import random

# 서버가 보내는 경우
#- 클라이언트 랜덤으로 선택해서 역할 정해주기
#- 행렬 보내주기

#1, 2 선택


def Send(group, send_queue):
    print('Thread Send Start')
    while True:
        s_client = []
        try:
            #새롭게 추가된 클라이언트가 있을 경우 Send 쓰레드를 새롭게 만들기 위해 루프를 빠져나감
            recv = send_queue.get()
            if recv == 'Group Changed':
                print('Group Changed')
                break

            
            type, data, recv_client_num, rc = recv[0].split()

            if type == "Start":
                case = [[0,1], [0,2], [0,3], [1,2], [1,3], [2,3]]
                for i in case:
                    msg = str(recv[2]) + ' matrix ' + ','.join(i)
                    for j in i:
                        group[j].send(bytes(data.encode()))

            
            elif type == "matrix":
                recv_client = group[int(recv_client_num)]

                msg = recv_client_num + " calculating " + data + " " + rc
                
                recv_client.send(bytes(msg.encode()))

            elif type == "cal_result":
                #행렬에 넣기
                #matrix[rc] = data
            
                
        except:
            pass


# 서버가 받는 경우
#- 행렬 받기
#- 연산결과 받기

def Recv(conn, count, send_queue, group):
    print('Thread Recv' + str(count) + ' Start')
    if count == 4:
        for conn in group:
            msg = str(count) + ' Client_all_connected 0'
            conn.send(bytes(msg.encode()))

    while True:
        data = conn.recv(1024).decode()
        send_queue.put([data, conn, count]) #각각의 클라이언트의 메시지, 소켓정보, 쓰레드 번호를 send로 보냄


# TCP Echo Server
if __name__ == '__main__':
    send_queue = Queue()
    HOST = ''  # 수신 받을 모든 IP를 의미
    PORT = 9000  # 수신받을 Port
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP Socket
    server_sock.bind((HOST, PORT))  # 소켓에 수신받을 IP주소와 PORT를 설정
    server_sock.listen(5)  # 소켓 연결, 여기서 파라미터는 접속수를 의미
    count = 0
    group = [] #연결된 클라이언트의 소켓정보를 리스트로 묶기 위함
    while True:
        count = count + 1
        conn, addr = server_sock.accept()  # 해당 소켓을 열고 대기
        group.append(conn) #연결된 클라이언트의 소켓정보
        print('Connected ' + str(addr))


        #소켓에 연결된 모든 클라이언트에게 동일한 메시지를 보내기 위한 쓰레드(브로드캐스트)
        #연결된 클라이언트가 1명 이상일 경우 변경된 group 리스트로 반영

        if count > 1:
            send_queue.put('Group Changed')
            thread1 = threading.Thread(target=Send, args=(group, send_queue,))
            thread1.start()
            pass
        else:
            thread1 = threading.Thread(target=Send, args=(group, send_queue,))
            thread1.start()

        #소켓에 연결된 각각의 클라이언트의 메시지를 받을 쓰레드
        thread2 = threading.Thread(target=Recv, args=(conn, count, send_queue, group))
        thread2.start()