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



def recv_client_choice_lottery(ticket_list1, client_num1, ticket_list2, client_num2):

    if len(ticket_list1) == 0 and len(ticket_list2) == 0:
        return (-1, -1, -1, -1)

    choice_ticket = random.choice(ticket_list1 + ticket_list2) # client1이 가지고있는 티켓 [1, 2, 3, 4]와 client2가 가지고있는 티켓 [5, 6, 7, 8]중에 하나 선택
    
    if choice_ticket in ticket_list1: # 선택한 티켓이 누가 가진 티켓인지 검사
        ticket_list1.remove(choice_ticket) #뽑혔던 티켓 없애기
        return (client_num1, ticket_list1, client_num2, ticket_list2) 
    else:
        ticket_list2.remove(choice_ticket)
        return (client_num2, ticket_list2, client_num1, ticket_list1)

def empty_check(idx, matrix):
    empty_space = [] 
    for m in range(0, 10):
        for n in range(0, 10):
            if matrix[idx][m][n] == -1:
                empty_space.append([m, n])
    
    random_mat = random.choice(empty_space)

    return random_mat

def Send(group, send_queue):
    global result_matrix, matrix, case, dic, c_list, result_matrix_count
    
    print('Thread Send Start')

    msg = "first_connected " + str(len(group))
    group[-1].send(bytes(msg.encode()))

    matrix_counting = 0


    while True:
        try:
            recv = send_queue.get()

            #새롭게 추가된 클라이언트가 있을 경우 Send 쓰레드를 새롭게 만들기 위해 루프를 빠져나감
            if recv == 'Group Changed':
                break

            #print(matrix)
            type_name, pair_mul, data, recv_client_num, rc, rc_num, etc = recv[0].split()
            
            if type_name == "matrix": # 클라이언트에게 행렬을 받아왔다면
                time.sleep(0.03)
                recv_client = group[int(recv_client_num)-1] # 연산을 해야하는 클라이언트에게 메시지 전송
                msg = recv_client_num + " calculating " + pair_mul + " " + data + "|" + rc + "|" + rc_num + "|" + etc
                #print("클라이언트" + recv_client_num + "에게 행렬" + rc + "보냄")
                recv_client.send(bytes(msg.encode())) #메시지 전송

            elif type_name == "cal_result":
                time.sleep(0.02)

                #다시 행렬을 받을 (연산역할) 클라이언트를 랜덤으로 선정
                recv_client_t = recv_client_num
                
                recv_client_ticket, not_recv_client, not_recv_client_ticket = etc.split("|")

                if recv_client_ticket == "[]" and not_recv_client_ticket == "[]":
                    recv_client_ticket = []
                    not_recv_client_ticket = []
                
                elif recv_client_ticket == "[]" or not_recv_client_ticket == "[]":
                    if recv_client_ticket == "[]":
                        recv_client_ticket = []
                        not_recv_client_ticket = list(map(int, not_recv_client_ticket.split(",")))
                    if not_recv_client_ticket == "[]":
                        not_recv_client_ticket = []
                        recv_client_ticket = list(map(int, recv_client_ticket.split(",")))
                
                else:
                    # 연산할 클라이언트 2명이 가지고 있는 티켓 리스트로
                    recv_client_ticket = list(map(int, recv_client_ticket.split(",")))
                    not_recv_client_ticket = list(map(int, not_recv_client_ticket.split(",")))
                

                # 클라이언트 2명 중 한명 선택
                recv_client_t, recv_client_ticket, not_recv_client, not_recv_client_ticket = recv_client_choice_lottery(recv_client_ticket, int(recv_client_t), not_recv_client_ticket, int(not_recv_client))

                idx = dic[pair_mul]
                matrix[idx][int(rc)][int(rc_num)] = int(data) # idx: case 인덱스, rc: 행, rc_num:열
                #print("행렬에 연산결과 저장됨")


                # 실행시켜보면 티켓의 수가 둘다 0이 되면 끝남. 즉 100번 실행하면 끝난다는 소리
       
                
                complete = 1

                for m_row in matrix[idx]:
                    if -1 in m_row:
                        complete = 0
                        break
                
                if complete == 0:
                    #Recv에 있던거랑 똑같음
                    if len(recv_client_ticket) == 0:
                        str_recv_client_ticket = "[]"
                    else:
                        str_recv_client_ticket = ','.join(map(str, recv_client_ticket))

                    if len(not_recv_client_ticket) == 0:
                        str_not_recv_client_ticket = "[]"
                    else:
                        str_not_recv_client_ticket = ','.join(map(str, not_recv_client_ticket))

                    
                    random_mat = empty_check(idx, matrix) # 랜덤 빈 좌표
                    add_msg = ' matrix ' + ','.join(map(str, case[idx])) + " " + str(recv_client_t) + "|" + str_recv_client_ticket + "|" + str(not_recv_client) + "|" + str_not_recv_client_ticket
                    for j, m in zip(case[idx], random_mat): # 메시지 전송
                        #print("클라이언트" + str(j) + "에게 행렬을 보내달라 말함")
                        msg = str(j) + "=" + str(m) + " " + add_msg
                        group[j-1].send(bytes(msg.encode())) #group에는 들어온 클라이언트가 하나씩 순서대로 쌓여있기때문에 인덱스로 골라서 send
                        msg = add_msg
                
                else:
                    print("행렬 하나 완성")
                    matrix_counting += 1
                    print(matrix_counting)

                    if matrix_counting == 6:
                        result_matrix_count += 1
                        result_matrix.append(matrix)

                        if result_matrix_count == 100:
                            print(result_matrix)
                            msg = "round_over"
                            for con in group:
                                con.send(bytes(msg.encode()))
                            #server_sock.close()
                            print("100번 연산 완료")
                            print("접속 종료")
                            break
                        #print(matrix)

                        print("모든 행렬 연산 완료")
                        print("넣기")
                        msg = "make_new_matrix"
                        for con in group:
                            con.send(bytes(msg.encode()))
                        matrix = np.full((6, 10, 10), -1)
                        matrix_counting = 0
                        for i in case: # 클라이언트에게 행렬을 달라고 알리는 메시지 전송
                            ticket_list1 = [ i for i in range(50)] #각 경우의 수 마다 연산할 클라이언트에게 티켓 주기
                            ticket_list2 = [ i for i in range(50, 100)]
                            complement = list(set(c_list) - set(i)) #행렬을 받을 클라이언트 둘
                            pair_mul = i[0] * i[1] # 결과 행렬 구분할 변수
                            idx = dic[str(pair_mul)]
                            #행렬을 받을 클라이언트 랜덤으로 선택 ( 선택된 클라이언트 번호, 선택된 클라이언트가 가진 티켓, 선택되지않은 클라이언트 번호, 선택되지않은 클라이언트가 가진 티켓 )
                            recv_client, recv_client_ticket, not_recv_client, not_recv_client_ticket = recv_client_choice_lottery(ticket_list1, complement[0], ticket_list2, complement[1])
                            
                            random_mat = empty_check(idx, matrix) # 랜덤 빈 좌표
                            
                            #나중에 티켓정보가 필요하기 때문에 메시지 주고받을때 계속해서 붙여줌
                            add_msg = ' matrix ' + ','.join(map(str, i)) + " " + str(recv_client) + "|" + ','.join(map(str, recv_client_ticket)) + "|" + str(not_recv_client) + "|" + ','.join(map(str, not_recv_client_ticket))
                            for j, m in zip(i, random_mat): # 메시지 전송 (클라이언트 번호, 좌표)
                                time.sleep(0.01)
                                # 여기서 빈 공간(-1)을 좌표로 모아서 해당 클라이언트에게 보냄
                                #print("클라이언트" + str(j) + "에게 행렬을 보내달라 말함")
                                msg = str(j) + "=" + str(m) + " " + add_msg # 클라이언트 번호, 좌표 (차례대로 행, 열 보내짐) + 위에 만든 메시지
                                group[j-1].send(bytes(msg.encode()))
                                msg = add_msg
                        
        except:
            pass

    if result_matrix_count == 100:
        server_sock.close()
        

    
# 서버가 받는 경우
#- 행렬 받기
#- 연산결과 받기

def Recv(conn, count, send_queue, group):
    global case, dic, c_list, result_matrix_count

    matrix = np.full((6, 10, 10), -1)

    print('Thread Recv' + str(count) + ' Start')
    if count == 4: #처음 클라이언트 4명이 다 들어오면 실행

        for i in case: # 클라이언트에게 행렬을 달라고 알리는 메시지 전송
            ticket_list1 = [ i for i in range(50)] #각 경우의 수 마다 연산할 클라이언트에게 티켓 주기
            ticket_list2 = [ i for i in range(50, 100)]
            complement = list(set(c_list) - set(i)) #행렬을 받을 클라이언트 둘
            pair_mul = i[0] * i[1] # 결과 행렬 구분할 변수
            idx = dic[str(pair_mul)]
            #행렬을 받을 클라이언트 랜덤으로 선택 ( 선택된 클라이언트 번호, 선택된 클라이언트가 가진 티켓, 선택되지않은 클라이언트 번호, 선택되지않은 클라이언트가 가진 티켓 )
            recv_client, recv_client_ticket, not_recv_client, not_recv_client_ticket = recv_client_choice_lottery(ticket_list1, complement[0], ticket_list2, complement[1])
            
            random_mat = empty_check(idx, matrix) # 랜덤 빈 좌표
            
            #나중에 티켓정보가 필요하기 때문에 메시지 주고받을때 계속해서 붙여줌
            add_msg = ' matrix ' + ','.join(map(str, i)) + " " + str(recv_client) + "|" + ','.join(map(str, recv_client_ticket)) + "|" + str(not_recv_client) + "|" + ','.join(map(str, not_recv_client_ticket))
            for j, m in zip(i, random_mat): # 메시지 전송 (클라이언트 번호, 좌표)
                time.sleep(0.01)
                # 여기서 빈 공간(-1)을 좌표로 모아서 해당 클라이언트에게 보냄
                #print("클라이언트" + str(j) + "에게 행렬을 보내달라 말함")
                msg = str(j) + "=" + str(m) + " " + add_msg # 클라이언트 번호, 좌표 (차례대로 행, 열 보내짐) + 위에 만든 메시지
                group[j-1].send(bytes(msg.encode()))
                msg = add_msg

    while True:
        
        if result_matrix_count == 100:
            break

        data = conn.recv(1024).decode()
        send_queue.put([data, conn, count]) #각각의 클라이언트의 메시지, 소켓정보, 쓰레드 번호를 send로 보냄
    
    server_sock.close()

# TCP Echo Server
if __name__ == '__main__':
    
    send_queue = Queue()
    HOST = ''  # 수신 받을 모든 IP를 의미
    PORT = 9000  # 수신받을 Port
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP Socket
    server_sock.bind((HOST, PORT))  # 소켓에 수신받을 IP주소와 PORT를 설정
    server_sock.listen(5)  # 소켓 연결, 여기서 파라미터는 접속수를 의미
    count, result_matrix_count = 0, 0
    group, result_matrix = [], [] #연결된 클라이언트의 소켓정보를 리스트로 묶기 위함
    case = [[1,2], [1,3], [1,4], [2,3], [2,4], [3,4]]
    c_list = [1, 2, 3, 4]
    dic = {'2': 0, '3': 1, '4': 2, '6': 3, '8': 4, '12': 5}
    matrix = np.full((6, 10, 10), -1)

    server_file = open("server_log.txt", "w", encoding="UTF-8")

    while True:
        try:
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

            
        except:
            exit(0)
