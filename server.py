import socket
import threading
from queue import Queue
import numpy as np
import random
import time

# 서버가 보내는 경우
#- 클라이언트 랜덤으로 선택해서 역할 정해주기
#- 행렬 보내주기

"""
연산 하는거까지 끝나면
while 100번
lottery 짜기
system_clock 넣기
로그 넣기
"""
server_file = open("server_log.txt", "w", encoding="UTF-8")

system_clock = 0  # 서버 0~600초 누적시간
system_clock_formating = ""  # 누적시간 형태 변환할 문자열
round = 1

# 시간을 출력 형식에 맞게 변환
def real_time(time):
    minute = "{}".format(time // 60)
    second = "{}".format(time % 60)
    result = "{}:{}".format(minute.zfill(2), second.zfill(2))
    # 예) 3초 => 00:03 / 100초 => 01:40
    return result


system_clock_formating = real_time(system_clock)

def Send(group, send_queue):
    global round
    print('Thread Send Start')

    """
    이 위에서 while 100번
    while 100:
        if go == 2:
            다시 case별로 클라이언트에게 누가 행렬 보내는 아이인지 메시지로 알려주기
        while True:
    """

    matrix_counting = 0

    while True:

        try:
            recv = send_queue.get()

            #새롭게 추가된 클라이언트가 있을 경우 Send 쓰레드를 새롭게 만들기 위해 루프를 빠져나감
            if recv == 'Group Changed':
                break


            type_name, pair_mul, data, recv_client_num, rc, rc_num = recv[0].split()
            
            

            if type_name == "matrix": # 클라이언트에게 행렬을 받아왔다면
                time.sleep(0.02)
                recv_client = group[int(recv_client_num)-1] # 연산을 해야하는 클라이언트에게 메시지 전송
                msg = recv_client_num + " calculating " + pair_mul + " " + data + "|" + rc + "|" + rc_num #행번호 열번호 보내줘 보미 했던거 
                print("클라이언트" + recv_client_num + "에게 행렬" + rc + "보냄")
                recv_client.send(bytes(msg.encode())) #메시지 전송

            elif type_name == "cal_result":
                time.sleep(0.01)
                case = [[1,2], [1,3], [1,4], [2,3], [2,4], [3,4]]
                dic = {'2': 0, '3': 1, '4': 2, '6': 3, '8': 4, '12': 5}
                idx = dic[pair_mul]
                matrix[idx][int(rc)][int(rc_num)] = int(data) # idx: case 인덱스, rc: 행, rc_num:열
                print("행렬에 연산결과 저장됨")
                server_file.write("{} [server] '클라이언트 {}'의 연산결과 '{}' 값이 matrix[{},{}] 에 저장되었습니다.\n".format(system_clock_formating, recv_client_num, data, rc, rc_num))
                #다시 행렬을 받을 (연산역할) 클라이언트를 랜덤으로 선정
                c_list = [1, 2, 3, 4]
                complement = list(set(c_list) - set(case[idx])) #행렬을 받을 클라이언트 둘
                recv_client = random.choice(complement) #행렬을 받을 클라이언트 랜덤으로 선택

                complete = 1

                for m_row in matrix[idx]:
                    if -1 in m_row:
                        complete = 0
                        break
                
                if complete == 0:
                    add_msg = ' matrix ' + ','.join(map(str, case[idx])) + " " +str(recv_client)
                    for j in case[idx]: # 메시지 전송
                        print("클라이언트" + str(j) + "에게 행렬을 보내달라 말함")
                        msg = str(j) + add_msg
                        group[j-1].send(bytes(msg.encode()))
                        msg = add_msg
                
                else:
                    print("행렬 하나 완성")
                    print(matrix)
                    matrix_counting += 1
                    print(matrix_counting)
                    if matrix_counting == 6:
                        server_file.write("라운드 {} 연산 완료".format(round))
                        print("라운드 " + str(round) + " 연산 완료") # 이건 로그에 안찍힘 왤까
                        round += 1
                        print(round)
                        if round > 2:
                            break


            """
            if matrix 6개가 다 찬다면:
                go = 2
                break
            """
                    
        except:
            pass

    print("모든 행렬 연산 완료")




# 서버가 받는 경우
#- 행렬 받기
#- 연산결과 받기

def Recv(conn, count, send_queue, group):
    print('Thread Recv' + str(count) + ' Start')
    if count == 4:
        case = [[1,2], [1,3], [1,4], [2,3], [2,4], [3,4]]
        c_list = [1, 2, 3, 4]
        for i in case: # 클라이언트에게 행렬을 달라고 알리는 메시지 전송
            complement = list(set(c_list) - set(i)) #행렬을 받을 클라이언트 둘
            recv_client = random.choice(complement) #행렬을 받을 클라이언트 랜덤으로 선택

            add_msg = ' matrix ' + ','.join(map(str, i)) + " " +str(recv_client)
            for j in i: # 메시지 전송
                print("클라이언트" + str(j) + "에게 행렬을 보내달라 말함")
                msg = str(j) + add_msg
                group[j-1].send(bytes(msg.encode()))
                msg = add_msg

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
    matrix = np.full((6, 10, 10), -1)
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