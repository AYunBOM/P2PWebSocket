import socket
import threading
from queue import Queue
import numpy as np
import time


# 시간을 출력 형식에 맞게 변환
def real_time(time):
    m = time // 60
    h = m // 60
    m = m % 60
    s = time % 60


    second = "{}".format(s)
    minute = "{}".format(m)
    hour = "{}".format(h)
    result = "{}:{}:{}".format(hour.zfill(2), minute.zfill(2), second.zfill(2))
    # 예) 3초 => 00:03 / 100초 => 01:40
    return result

def Send(client_sock, send_queue):
    global pair_check, data_row, data_col, done, result_matrix, cal_matrix
    
    while True:
        try:
            #새롭게 추가된 클라이언트가 있을 경우 Send 쓰레드를 새롭게 만들기 위해 루프를 빠져나감
            if done == 1:
                break

            recv = send_queue.get()

            thread_num, type_name, pair, etc, system_clock = recv[0].split()

            system_clock = int(system_clock)

            if type_name == 'matrix':
                time.sleep(0.02)
                thread_num, random_dir = thread_num.split("=")
                pair = list(map(int, pair.split(","))) # [1, 2]
                recv_client, recv_client_ticket, not_recv_client, not_recv_client_ticket = etc.split("|")

                pair_mul = pair[0] * pair[1]
                
                system_clock += 1
                system_clock_formating = real_time(system_clock)

                if int(thread_num) == min(pair):
                    time.sleep(0.008)
                    #행렬의 가로
                    mtx = ",".join(map(str, matrix[int(random_dir)]))
                    msg = "matrix " + str(pair_mul) + " " + mtx + " " + str(recv_client) + " row " + str(random_dir) + " " + recv_client_ticket + "|" + not_recv_client + "|" + not_recv_client_ticket
                    
                    client_file.write("{} [client {}] '행'의 정보를 전달합니다.\n".format(system_clock_formating, thread_num))
                    #print("가로 전달")
                    client_sock.send(bytes(msg.encode()))
                else:
                    time.sleep(0.005)
                    #행렬의 세로
                    mtx = ",".join(map(str, matrix[:, int(random_dir)]))
                    msg = "matrix " + str(pair_mul) + " " + mtx + " " + str(recv_client) + " col " + str(random_dir) + " " + recv_client_ticket + "|" + not_recv_client + "|" + not_recv_client_ticket
                    client_file.write("{} [client {}] '열'의 정보를 전달합니다.\n".format(system_clock_formating, thread_num))
                    #print("세로 전달")
                    client_sock.send(bytes(msg.encode()))
            
            elif type_name == 'calculating':
                time.sleep(0.03)
                #system_clock += 1
                pair_cal = int(pair) # 연산할 클라이언트 번호 곱 계산 했던거
                data, rc, rc_num, recv_client_ticket_t, not_recv_client_t, not_recv_client_ticket_t = etc.split("|") # 연산할 행이나 열, 행인지 열인지, 자신이 가진 행이나 열의 번호
                
                data = list(map(int, data.split(","))) # ,로 구분해서 나눈 다음 리스트로 만들기
                
                pair_check.append(pair_cal) # pair_cal 저장 [2]
                
                
                # 왜 row랑 col 리스트를 나눴냐면 나중에 연산하고 값을 넘겨줄 때 자신이 행인지 열인지 알 수 없어 그래서 구분했음
                if rc == "row":
                    time.sleep(0.008)
                    data_row.append([pair_cal, rc_num, data]) # [2, 6, [1, 2, 3, 4, 5]] 데이터 저장
                    system_clock += 1
                    system_clock_formating = real_time(system_clock)
                    client_file.write("{} [client {}] '행'의 정보를 받았습니다.\n".format(system_clock_formating, thread_num, data))
                else:
                    time.sleep(0.008)
                    data_col.append([pair_cal, rc_num, data]) # [2, 6, [1, 2, 3, 4, 5]] 데이터 저장
                    system_clock += 1
                    system_clock_formating = real_time(system_clock)
                    client_file.write("{} [client {}] '열'의 정보를 받았습니다.\n".format(system_clock_formating, thread_num, data))
                if pair_check.count(pair_cal) == 2: # 가로 세로 행이 2개 다 들어왔으면
                    
                    x, y = 0, 0 # pop할 위치 정할 변수들
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
                    result = sum(x * y for x, y in zip(cal_row, cal_col))
                    msg = "cal_result " + str(pair_cal) + " " + str(result) + " " + thread_num + " " + str(cal_row_dir) + " " + str(cal_col_dir)+ " " + recv_client_ticket_t + "|" + not_recv_client_t + "|" + not_recv_client_ticket_t
                    pair_check = [x for x in pair_check if x != pair_cal]
                    system_clock += 1
                    system_clock_formating = real_time(system_clock)
                    client_file.write("{} [client {}] 연산합니다.\n".format(system_clock_formating, thread_num))
                    cal_matrix.append(result)
                    system_clock += 1
                    system_clock_formating = real_time(system_clock)
                    client_file.write("{} [client {}] 연산 결과를 전달합니다.\n".format(system_clock_formating, thread_num, result))
                    print("연산 전달")
                    client_sock.send(bytes(msg.encode()))
        except:
            pass
    client_sock.close()

#클라이언트가 받는 경우
#- 처음 서버한테 자기가 행렬(가로, 세로)를 주는 아인지 받는 아인지 확인
#- 행렬을 받음

def Recv(client_sock, send_queue):
    global client_file, matrix, done, system_clock, system_clock_formating, cal_matrix, result_matrix
    while True:
        try:
            recv_data = client_sock.recv(1024).decode()  # Server -> Client 데이터 수신
            type_name, idx, rnd, system_clock = recv_data.split()[0], recv_data.split()[1], recv_data.split()[2], recv_data.split()[-1]

            system_clock = int(system_clock)
            system_clock_formating = real_time(system_clock)

            if type_name == 'first_connected':
                file_name = "client" + idx + "_log.txt"
                client_file = open(file_name, "w", encoding="UTF-8")
                client_file.write("{} [client {}] 서버에 연결되었습니다.\n".format(system_clock_formating, idx))
                client_file.write("{} [client {}] 10X10 행렬을 생성합니다.\n".format(system_clock_formating, idx))
                client_file.write("{}\n".format(matrix))
                client_file.write("{} [client {}] '라운드 {}' 시작\n".format(system_clock_formating, idx, rnd))
                
            elif type_name == 'make_new_matrix':
                print(2)
                matrix = np.random.randint(0, 101, (10, 10)) # 10X10 행렬 만들기 
                client_file.write("{} [client {}] 10X10 행렬을 생성합니다.\n".format(system_clock_formating, idx))
                client_file.write("{}\n".format(matrix))
                client_file.write("{} [client {}] '라운드 {}' 시작\n".format(system_clock_formating, idx, rnd))

            elif type_name == 'round_pass':
                print("라운드 하나 완료")
                client_file.write("{} [client {}] '라운드 {}' 완료.\n".format(system_clock_formating, idx, rnd))
                print(1)
                result_matrix.append(cal_matrix)
                cal_matrix = []

            elif type_name == 'round_over':
                client_file.write("{} [client {}] 모든 라운드가 실행되었습니다\n".format(system_clock_formating, idx))
                
                for i, mtx in zip(range(1,3),result_matrix):
                    mtx = np.array(mtx)
                    client_file.write("Round {} calculation\n {}\n".format(i, mtx.reshape(15,10)))
                done = 1
                break
            else:
                send_queue.put([recv_data])
        except:
            exit(0)
    send_queue.put("1")
    client_sock.close()
    
#TCP Client
if __name__ == '__main__':
    send_queue = Queue()
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket
    Host = 'localhost' #통신할 대상의 IP 주소
    Port = 9000  #통신할 대상의 Port 주소
    client_sock.connect((Host, Port)) #서버로 연결시도    

    print("서버 연결 완료")
    done = 0
    cal_matrix = []
    result_matrix = []


    matrix = np.random.randint(0, 101, (10, 10)) # 10X10 행렬 만들기 

    pair_check, data_row, data_col, client_file = [], [], [], [] # 짝만 맞출 리스트, data를 저장해놓을 리스트

    #Client의 메시지를 보낼 쓰레드
    thread1 = threading.Thread(target=Send, args=(client_sock, send_queue))
    thread1.start()

    #Server로 부터 다른 클라이언트의 메시지를 받을 쓰레드
    thread2 = threading.Thread(target=Recv, args=(client_sock, send_queue))
    thread2.start()