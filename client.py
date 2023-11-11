import socket
import threading
from queue import Queue
import random
import numpy as np
import time




#클라이언트가 보내는 경우
#- 서버에게 자신의 행렬 보내기
#- 서버에게 연산 결과 보내기
def Send(client_sock, send_queue):
    global pair_check, data_row, data_col
    while True:
        try:
            #새롭게 추가된 클라이언트가 있을 경우 Send 쓰레드를 새롭게 만들기 위해 루프를 빠져나감
            recv = send_queue.get()
    
            thread_num, type_name, pair, etc = recv[0].split()

            if type_name == 'matrix':
                time.sleep(0.01)
                pair = list(map(int, pair.split(",")))
                recv_client = etc

                pair_mul = pair[0] * pair[1]

                if int(thread_num) == min(pair):
                    time.sleep(0.008)
                    #행렬의 가로
                    random_row = random.randint(0, 9) # 아무 행이나 선택
                    #msg = "matrix" + "행렬의 가로" + str(recv_client) + "row" + 가로의 번호
                    mtx = ",".join(map(str, matrix[random_row]))
                    msg = "matrix " + str(pair_mul) + " " + mtx + " " + str(recv_client) + " row " + str(random_row) # recv_client는 행렬을 받을 클라이언트
                    print("가로 행렬 서버에게 보냄")
                    client_sock.send(bytes(msg.encode()))
                else:
                    time.sleep(0.005)
                    #행렬의 세로
                    random_col = random.randint(0, 9) # 아무 열이나 선택
                    #msg = "matrix" + "행렬의 세로" + str(recv_client) + "col" + 세로의 번호
                    mtx = ",".join(map(str, matrix[:, random_col]))
                    msg = "matrix " + str(pair_mul) + " " + mtx + " " + str(recv_client) + " col " + str(random_col) # 수정필요
                    print("세로 행렬 서버에게 보냄")
                    client_sock.send(bytes(msg.encode()))
            
            elif type_name == 'calculating':
                time.sleep(0.02)
                print("연산함")
                pair_cal = int(pair) # 연산할 클라이언트 번호 곱 계산 했던거
                cal_row_dir, cal_row, cal_col_dir, cal_col = etc.split("|") # 연산할 행이나 열, 행인지 열인지, 자신이 가진 행이나 열의 번호
                
                cal_row = list(map(int, cal_row.split(","))) # ,로 구분해서 나눈 다음 리스트로 만들기
                cal_col = list(map(int, cal_col.split(",")))
                
                result = sum(x * y for x, y in zip(cal_row, cal_col))

                msg = "cal_result " + str(pair_cal) + " " + str(result) + " " + thread_num + " " + cal_row_dir + " " + cal_col_dir

                client_sock.send(bytes(msg.encode()))
        except:
            pass


#클라이언트가 받는 경우
#- 처음 서버한테 자기가 행렬(가로, 세로)를 주는 아인지 받는 아인지 확인
#- 행렬을 받음

def Recv(client_sock, send_queue):
    while True:
        recv_data = client_sock.recv(1024).decode()  # Server -> Client 데이터 수신
        
        
        send_queue.put([recv_data])

#TCP Client
if __name__ == '__main__':
    send_queue = Queue()
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket
    Host = 'localhost' #통신할 대상의 IP 주소
    Port = 9000  #통신할 대상의 Port 주소
    client_sock.connect((Host, Port)) #서버로 연결시도
    print('Connecting to ', Host, Port)

    matrix = np.random.randint(0, 101, (10, 10)) # 10X10 행렬 만들기 
    #pair_check, data_row, data_col = [], [], [] # 짝만 맞출 리스트, data를 저장해놓을 리스트


    #Client의 메시지를 보낼 쓰레드
    thread1 = threading.Thread(target=Send, args=(client_sock, send_queue))
    thread1.start()

    #Server로 부터 다른 클라이언트의 메시지를 받을 쓰레드
    thread2 = threading.Thread(target=Recv, args=(client_sock, send_queue))
    thread2.start() 
