import socket
import threading
from queue import Queue
import random
import numpy as np

global pair_check, data_row, data_col
pair_check = []; data_row = []; data_col = [] # 짝만 맞출 리스트, data를 저장해놓을 리스트

#클라이언트가 보내는 경우
#- 서버에게 자신의 행렬 보내기
#- 서버에게 연산 결과 보내기
def Send(client_sock, send_queue):
    
    while True:
        try:
            #새롭게 추가된 클라이언트가 있을 경우 Send 쓰레드를 새롭게 만들기 위해 루프를 빠져나감
            recv = send_queue.get()
            print("send로 왔음")

            thread_num, type_name, pair, etc = recv[0].split()

            if type_name == 'matrix':
                print("matrix로 왔음")
                pair = list(map(int, pair.split(",")))
                recv_client = etc

                pair_mul = pair[0] * pair[1]

                if int(thread_num) == min(pair):
                    #행렬의 가로
                    random_row = random.randint(0, 9) # 아무 행이나 선택
                    #msg = "matrix" + "행렬의 가로" + str(recv_client) + "row" + 가로의 번호
                    mtx = ",".join(map(str, matrix[random_row]))
                    msg = "matrix " + str(pair_mul) + " " + mtx + " " + str(recv_client) + " row " + str(random_row) # 수정필요할지도
                    print("가로 행렬 서버에게 보냄")
                    client_sock.send(bytes(msg.encode()))
                else:
                    #행렬의 세로
                    random_col = random.randint(0, 9) # 아무 열이나 선택
                    #msg = "matrix" + "행렬의 세로" + str(recv_client) + "col" + 세로의 번호
                    mtx = ",".join(map(str, matrix[:, random_col]))
                    msg = "matrix " + str(pair_mul) + " " + mtx + " " + str(recv_client) + " col " + str(random_col) # 수정필요
                    print("세로 행렬 서버에게 보냄")
                    client_sock.send(bytes(msg.encode()))
            
            elif type_name == 'calculating':
                print("연산 시작")
                pair_cal = int(pair) # 연산할 클라이언트 번호 곱 계산 했던거
                data, rc, rc_num = etc.split("|") # 연산할 행이나 열, 행인지 열인지, 자신이 가진 행이나 열의 번호
                
                data = list(map(int, data.split(","))) # ,로 구분해서 나눈 다음 리스트로 만들기
                pair_check.append(pair_cal) # pair_cal 저장 [2]
                
                # 왜 row랑 col 리스트를 나눴냐면 나중에 연산하고 값을 넘겨줄 때 자신이 행인지 열인지 알 수 없어 그래서 구분했음
                if rc == "row":
                    print("row 데이터 받음") 
                    data_row.append([pair_cal, rc_num, data]) # [2, 6, [1, 2, 3, 4, 5]] 데이터 저장
                else:
                    print("col 데이터 받음")
                    data_col.append([pair_cal, rc_num, data]) # [2, 6, [1, 2, 3, 4, 5]] 데이터 저장

                if pair_check.count(pair_cal) == 2: # 가로 세로 행이 2개 다 들어왔으면
                    print("둘 다 받음")
                    x, y = 0 # pop할 위치 정할 변수들
                    for i in data_row: # 해당 pair_mul을 가지고 있는 data_row와 data_col 속 데이터 추출
                        if i[0] == pair_cal:
                            cal_row_dir = i[1]
                            cal_row = i[2]
                            data_row.pop(x)
                        else:
                            x += 1
                    for j in data_col:
                        if j[0] == pair_cal:
                            cal_col_dir = j[1]
                            cal_col = j[2]
                            data_col.pop(y)
                        else:
                            y += 1
                    print(cal_row, cal_col)
                    result = sum(x * y for x, y in zip(cal_row, cal_col))
                    msg = "cal_result " + str(result) + " " + str(5) + " " + str(cal_row_dir) + " " + str(cal_col_dir)
                    pair_check = [x for x in pair_check if x != pair_cal]
                    print("연산 완료. 연산 결과 서버에게 보냄")
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


    #Client의 메시지를 보낼 쓰레드
    thread1 = threading.Thread(target=Send, args=(client_sock, send_queue))
    thread1.start()

    #Server로 부터 다른 클라이언트의 메시지를 받을 쓰레드
    thread2 = threading.Thread(target=Recv, args=(client_sock, send_queue))
    thread2.start()
