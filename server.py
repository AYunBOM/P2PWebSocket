# -*- coding: utf-8 -*-

import socket
import threading
import numpy as np
import random

# 서버 설정
host = "0.0.0.0"  # 모든 IP 주소에서 연결 허용
port = 8080  # 사용할 포트 번호


# 소켓 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 소켓을 주소와 포트에 바인딩
server_socket.bind((host, port))

# 클라이언트로부터 연결 대기
server_socket.listen(4)  # 4개의 연결을 동시에 처리
# server_file.write("서버가 {}:{}에서 실행 중입니다.\n".format(host, port))

status = 0
thread_num = 0
random_client = 0
ticket, result = [], []
matrix = []
r_num, c_num, row, col = None, None, None, None
case = [[1,2], [1,3], [1,4], [2,3], [2,4], [3,4]]

# 시간을 출력 형식에 맞게 변환
def real_time(time):
    minute = "{}".format(time // 60)
    second = "{}".format(time % 60)
    result = "{}:{}".format(minute.zfill(2), second.zfill(2))
    # 예) 3초 => 00:03 / 100초 => 01:40
    return result



def client_handler(client_socket, thread_num): 
    global r_num, c_num, row, col, matrix, case, random_client, status, ticket, result

    # 10X10행렬 6개를 실행
    while 6:
        ticket = [i for i in range(100)]
        matrix = np.full((10,10), -1)
        if thread_num == 3:            
            random_client = random.randint(0, 5) # 연산될 클라이언트 2개를 랜덤으로 선택
        else:
            if random_client != 0:
                while 100: 
                    status = 0           
                    if thread_num in case[random_client]: # 랜덤으로 선택된 클라이언트에게 접근
                        while True:   
                            r_num, c_num = None, None
                            if thread_num == min(random_client): # 랜덤으로 선택된 것들 중 행이 될 클라이언트
                                message = "1 row" # 클라이언트에게 "너는 행이야" 라고 알려주기                                
                                client_socket.send(message.encode("utf-8"))                                
                                r_num, row = client_socket.recv(1024).decode("utf-8").split("|") # 클라이언트는 랜덤으로 뽑은 자신의 행번호와 행을 알려줌                                
                            else:
                                message = "1 col" # 클라이언트에게 "너는 열이야" 라고 알려주기                                
                                client_socket.send(message.encode("uft-8"))                                 
                                c_num, col = client_socket.recv(1024).decode("utf-8").split("|") # 클라이언트는 랜덤으로 뽑은 자신의 열번호와 열을 알려줌                            
                            
                            while True:
                                if r_num is not None and c_num is not None:
                                    break
                                
                            if matrix[r_num, c_num] == -1: # 랜덤으로 뽑은 행과 열에 위치한 행렬에 값이 없는지 확인
                                status = 1 
                                break
                    
                    else:
                        ticket_num = random.randint(0, len(ticket))
                        ticket_num = ticket.pop(ticket_num)

                        client_socket.send(str(0).encode("uft-8"))

                        while True:
                            if status == 1: # 행과 열이 제대로 받아지면 
                                client_socket.send(row.encode("utf-8"))
                                client_socket.send(col.encode("utf-8"))
                                # (수정) 시스템 클락도 보내기 
                                matrix[r_num,c_num] = int(client_socket.recv(1024).decode("utf-8")) 
                                break
        result.append(matrix)

# 클라이언트와 연결 수락
while True:
    client_socket, client_address = server_socket.accept()
    client_thread = threading.Thread(
        target=client_handler, args=(client_socket, thread_num)
    )
    thread_num += 1
    client_thread.start()