# -*- coding: utf-8 -*-

import socket
import threading

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


# 시간을 출력 형식에 맞게 변환
def real_time(time):
    minute = "{}".format(time // 60)
    second = "{}".format(time % 60)
    result = "{}:{}".format(minute.zfill(2), second.zfill(2))
    # 예) 3초 => 00:03 / 100초 => 01:40
    return result



def client_handler(client_socket):
    global system_clock, result_sum, count

    


# 클라이언트와 연결 수락
while True:
    client_socket, client_address = server_socket.accept()
    client_thread = threading.Thread(
        target=client_handler, args=(client_socket)
    )
    client_thread.start()