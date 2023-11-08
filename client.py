# -*- coding: utf-8 -*-

import socket
import numpy as np
import random

# 서버 정보 설정
server_host = "101.101.208.213"  # 서버의 IP 주소로 변경
server_port = 8080  # 서버에서 설정한 포트 번호로 변경


# 시간을 출력 형식에 맞게 변환
def real_time(time):
    minute = "{}".format(time // 60)
    second = "{}".format(time % 60)
    result = "{}:{}".format(minute.zfill(2), second.zfill(2))
    # 예) 3초 => 00:03 / 100초 => 01:40
    return result


# 소켓 생성
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 서버에 연결
client_socket.connect((server_host, server_port))

#클라이언트가 해야 할 거
while True: 
    matrix = np.random.randint(0, 101, (10, 10)) #10X10 행렬 만들기

    answer = client_socket.recv(1024).decode("utf-8")
    answer_split = answer.split(",")

    if answer_split[0]: # 만약 자신이 선택됐다면 (1이라면 선택 / 0이라면 선택X)
        answer_dir = answer_split[1] #자신이 행인지 열인지 확인 
        if answer_dir == 'row': #행이 걸렸다면   
            while True:
                random_dir = random.randint(0, 9)
                client_socket.send(str(random_dir).encode("utf-8"))
                check = client_socket.recv(1024).decode("utf-8")
                if int(check): #랜덤값 확인 받았으면 탈출
                    break
            row_send = ' '.join(str(i) for i in matrix[random_dir]) #해당 행을 str로 변환
            client_socket.send(row_send.encode("utf-8")) #해당 행 서버로 전송
            
        if answer_dir == 'col':
            while True:
                random_dir = random.randint(0, 9)
                client_socket.send(str(random_dir).encode("utf-8"))
                check = client_socket.recv(1024).decode("utf-8")
                if int(check): #랜덤값 확인 받았으면 탈출
                    break
            col_send = ' '.join(str(i) for i in matrix[:, random_dir]) #해당 열을 str로 변환
            client_socket.send(col_send.encode("utf-8")) #해당 열 서버로 전송
    
    # 만약 선택받지 못했다면
    else:
        row_recv = client_socket.recv(1024).decode("utf-8") # 선택된 행 저장
        col_recv = client_socket.recv(1024).decode("utf-8") # 선택된 열 저장

        row_recv_list = [int(i) for i in row_recv.split(' ')] # 행 리스트로 변환
        col_recv_list = [int(i) for i in col_recv.split(' ')] # 열 리스트로 변환

        result = sum(x * y for x, y in zip(row_recv_list, col_recv_list)) # 두 리스트를 인덱스별로 곱하고 더함 (행렬 곱)

        client_socket.send(str(result).encode("utf-8"))

client_socket.close()
