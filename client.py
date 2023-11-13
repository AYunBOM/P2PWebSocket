import socket
import threading
from queue import Queue
import numpy as np
import time


system_clock = 0  # 서버 0~600초 누적시간
system_clock_formating = ""  # 누적시간 형태 변환할 문자열

# 시간을 출력 형식에 맞게 변환
def real_time(time):
    minute = "{}".format(time // 60)
    second = "{}".format(time % 60)
    result = "{}:{}".format(minute.zfill(2), second.zfill(2))
    # 예) 3초 => 00:03 / 100초 => 01:40
    return result

def Send(client_sock, send_queue):
    global pair_check, data_row, data_col, done
    while True:
        try:
            #새롭게 추가된 클라이언트가 있을 경우 Send 쓰레드를 새롭게 만들기 위해 루프를 빠져나감
            if done == 1:
                break

            recv = send_queue.get()
    
            thread_num, type_name, pair, etc = recv[0].split()

            if type_name == 'matrix':
                time.sleep(0.02)
                thread_num, random_dir = thread_num.split("=")
                pair = list(map(int, pair.split(","))) # [1, 2]
                recv_client, recv_client_ticket, not_recv_client, not_recv_client_ticket = etc.split("|")

                pair_mul = pair[0] * pair[1]

                if int(thread_num) == min(pair):
                    time.sleep(0.008)
                    #행렬의 가로
                    mtx = ",".join(map(str, matrix[int(random_dir)]))
                    msg = "matrix " + str(pair_mul) + " " + mtx + " " + str(recv_client) + " row " + str(random_dir) + " " + recv_client_ticket + "|" + not_recv_client + "|" + not_recv_client_ticket
                    print("가로 행렬 서버에게 보냄")
                    #system_clock += 1
                    client_file[thread_num-1].write("{} [client {}] 서버에게 '행'을 전달합니다.\n".format(system_clock_formating, thread_num))
                    client_file[thread_num-1].write("행 '{}' > {}".format(random_dir, mtx))
                    client_sock.send(bytes(msg.encode()))
                else:
                    time.sleep(0.005)
                    #행렬의 세로
                    mtx = ",".join(map(str, matrix[:, int(random_dir)]))
                    msg = "matrix " + str(pair_mul) + " " + mtx + " " + str(recv_client) + " col " + str(random_dir) + " " + recv_client_ticket + "|" + not_recv_client + "|" + not_recv_client_ticket 
                    print("세로 행렬 서버에게 보냄")
                    #system_clock += 1
                    client_file[thread_num-1].write("{} [client {}] 서버에게 '열'을 전달합니다.\n".format(system_clock_formating, thread_num))
                    client_file[thread_num-1].write("열 '{}' > {}".format(random_dir, mtx))
                    client_sock.send(bytes(msg.encode()))
            
            elif type_name == 'calculating':
                time.sleep(0.03)
                print("연산함")
                #system_clock += 1
                pair_cal = int(pair) # 연산할 클라이언트 번호 곱 계산 했던거
                data, rc, rc_num, recv_client_ticket_t, not_recv_client_t, not_recv_client_ticket_t = etc.split("|") # 연산할 행이나 열, 행인지 열인지, 자신이 가진 행이나 열의 번호
                
                data = list(map(int, data.split(","))) # ,로 구분해서 나눈 다음 리스트로 만들기
                
                pair_check.append(pair_cal) # pair_cal 저장 [2]
                
                
                # 왜 row랑 col 리스트를 나눴냐면 나중에 연산하고 값을 넘겨줄 때 자신이 행인지 열인지 알 수 없어 그래서 구분했음
                if rc == "row":
                    time.sleep(0.009)
                    data_row.append([pair_cal, rc_num, data]) # [2, 6, [1, 2, 3, 4, 5]] 데이터 저장
                    #system_clock += 1
                    client_file[thread_num-1].write("{} [client {}] 행의 정보를 전달받았습니다.\n".format(system_clock_formating, thread_num))
                    client_file[thread_num-1].write("전달받은 행 정보: {}".format(data_row))
                else:
                    time.sleep(0.012)
                    data_col.append([pair_cal, rc_num, data]) # [2, 6, [1, 2, 3, 4, 5]] 데이터 저장
                    #system_clock += 1
                    client_file[thread_num-1].write("{} [client {}] 열의 정보를 전달받았습니다.\n".format(system_clock_formating, thread_num))
                    client_file[thread_num-1].write("전달받은 열 정보: {}".format(data_col))
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
                    #system_clock += 1
                    client_file[thread_num-1].write("{} [client {}] 연산을 합니다.\n".format(system_clock_formating, thread_num))
                    client_file[thread_num-1].write("연산 결과 : {}\n".format(result))
                    #system_clock += 1
                    client_file[thread_num-1].write("{} [client {}] 연산 결과를 전달합니다.\n".format(system_clock_formating, thread_num))
                    client_sock.send(bytes(msg.encode()))
        except:
            pass
    client_sock.close()

#클라이언트가 받는 경우
#- 처음 서버한테 자기가 행렬(가로, 세로)를 주는 아인지 받는 아인지 확인
#- 행렬을 받음

def Recv(client_sock, send_queue):
    global client_file, matrix, done, system_clock, system_clock_formating, i
    while True:
        try:
            recv_data = client_sock.recv(1024).decode()  # Server -> Client 데이터 수신
            
            if recv_data.split()[0] == 'first_connected':
                i = recv_data.split()[1]
                file_name = "client" + str(i) + "_log.txt"
                client_file.append(open(file_name, "w", encoding="UTF-8"))
                client_file[i-1].write("{} [client {}] 서버에 연결되었습니다.\n".format(system_clock_formating, i))
                

            elif recv_data.split()[0] == 'make_new_matrix':
                matrix = np.random.randint(0, 101, (10, 10)) # 10X10 행렬 만들기 
                client_file[i-1].write("{} [client {}] 10X10 행렬을 생성합니다.\n".format(system_clock_formating, i))
                client_file[i-1].write(str(matrix))

            elif recv_data.split()[0] == 'round_over':
                print("접속 종료")
                done = 1
                break

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
    system_clock_formating = real_time(system_clock)
    
    print("서버 연결 완료")
    done = 0
    matrix = np.random.randint(0, 101, (10, 10)) # 10X10 행렬 만들기 
    pair_check, data_row, data_col, client_file = [], [], [], [] # 짝만 맞출 리스트, data를 저장해놓을 리스트

    #Client의 메시지를 보낼 쓰레드
    thread1 = threading.Thread(target=Send, args=(client_sock, send_queue))
    thread1.start()

    #Server로 부터 다른 클라이언트의 메시지를 받을 쓰레드
    thread2 = threading.Thread(target=Recv, args=(client_sock, send_queue))
    thread2.start()