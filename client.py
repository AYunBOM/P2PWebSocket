import socket
import threading
from queue import Queue
import random

#클라이언트가 보내는 경우
#- 서버에게 자신의 행렬 보내기
#- 서버에게 연산 결과 보내기
def Send(client_sock, send_queue):

    while True:
        try:
            #새롭게 추가된 클라이언트가 있을 경우 Send 쓰레드를 새롭게 만들기 위해 루프를 빠져나감
            recv = send_queue.get()

            thread_num, type, pair = recv.split()

            if type == 'matrix':
                c_list = [0, 1, 2, 3]
                pair = list(map(int, pair.split(",")))
                complement = list(set(c_list) - set(pair)) #행렬을 받을 클라이언트 둘

                recv_client = random.choice(complement) #행렬을 받을 클라이언트 랜덤으로 선택

                if int(thread_num) == min(pair)+1:
                    #행렬의 가로
                    #msg = "matrix" + "행렬의 가로" + str(recv_client) + "row"
                    client_sock.send(bytes(msg.encode()))
                else:
                    #행렬의 세로
                    #msg = "matrix" + "행렬의 세로" + str(recv_client) + "col"
                    client_sock.send(bytes(msg.encode()))
            
            elif type == 'calculating':
                data, rc = pair.split()

                if rc == "row":
                    #가로에 저장
                else:
                    #세로에 저장
                
                if #가로 세로 행이 2개 다 들어왔으면:
                    #연산
                    #msg = "cal_result" + "연산결과" + 아무번호 + "행열번호"
                    client_sock.send(bytes(msg.encode()))

        except:
            pass


#클라이언트가 받는 경우
#- 처음 서버한테 자기가 행렬(가로, 세로)를 주는 아인지 받는 아인지 확인
#- 행렬을 받음

def Recv(client_sock, send_queue):
    while True:
        recv_data = client_sock.recv(1024).decode()  # Server -> Client 데이터 수신
        print(recv_data)
        
        if recv_data.split()[1] == 'Client_all_connected':
            msg = 'Start 1 0'
            client_sock.send(bytes(msg.encode()))

        else:
            send_queue.put([recv_data])

#TCP Client
if __name__ == '__main__':
    send_queue = Queue()
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket
    Host = 'localhost' #통신할 대상의 IP 주소
    Port = 9000  #통신할 대상의 Port 주소
    client_sock.connect((Host, Port)) #서버로 연결시도
    print('Connecting to ', Host, Port)


    #Client의 메시지를 보낼 쓰레드
    thread1 = threading.Thread(target=Send, args=(client_sock, send_queue))
    thread1.start()

    #Server로 부터 다른 클라이언트의 메시지를 받을 쓰레드
    thread2 = threading.Thread(target=Recv, args=(client_sock, send_queue))
    thread2.start()