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
    choice_ticket = random.choice(ticket_list1 + ticket_list2)
    
    if choice_ticket in ticket_list1:
        ticket_list1.remove(choice_ticket)
        return (client_num1, ticket_list1, client_num2, ticket_list2)
    else:
        ticket_list2.remove(choice_ticket)
        return (client_num2, ticket_list2, client_num1, ticket_list1)


def Send(group, send_queue):
    global result_matrix
    
    print('Thread Send Start')

    msg = "first_connected " + str(len(group))
    group[-1].send(bytes(msg.encode()))

    
    matrix_counting = 0
    matrix = np.full((6, 10, 10), -1)

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
                msg = recv_client_num + " calculating " + pair_mul + " " + data + "|" + rc + "|" + rc_num + "|" + etc  #행번호 열번호 보내줘 보미 했던거 
                print("클라이언트" + recv_client_num + "에게 행렬" + rc + "보냄")
                recv_client.send(bytes(msg.encode())) #메시지 전송

            elif type_name == "cal_result":
                time.sleep(0.02)
                case = [[1,2], [1,3], [1,4], [2,3], [2,4], [3,4]]
                dic = {'2': 0, '3': 1, '4': 2, '6': 3, '8': 4, '12': 5}

                #다시 행렬을 받을 (연산역할) 클라이언트를 랜덤으로 선정
                recv_client_t = recv_client_num
                recv_client_ticket, not_recv_client, not_recv_client_ticket = etc.split("|")                
                
                recv_client_ticket = list(map(int, recv_client_ticket.split(",")))
                not_recv_client_ticket = list(map(int, not_recv_client_ticket.split(",")))

                recv_client_t, recv_client_ticket, not_recv_client, not_recv_client_ticket = recv_client_choice_lottery(recv_client_ticket, int(recv_client_t), not_recv_client_ticket, int(not_recv_client))

                idx = dic[pair_mul]
                matrix[idx][int(rc)][int(rc_num)] = int(data) # idx: case 인덱스, rc: 행, rc_num:열
                print("행렬에 연산결과 저장됨")

                print(case[idx], len(recv_client_ticket), len(not_recv_client_ticket))
                
                
                complete = 1

                for m_row in matrix[idx]:
                    if -1 in m_row:
                        complete = 0
                        break
                
                if complete == 0:
                    add_msg = ' matrix ' + ','.join(map(str, case[idx])) + " " + str(recv_client_t) + "|" + ','.join(map(str, recv_client_ticket)) + "|" + str(not_recv_client) + "|" + ','.join(map(str, not_recv_client_ticket))
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
                        break


                    
        except:
            pass

    print("모든 행렬 연산 완료")
    result_matrix.append(matrix)




# 서버가 받는 경우
#- 행렬 받기
#- 연산결과 받기

def Recv(conn, count, send_queue, group):
    print('Thread Recv' + str(count) + ' Start')
    if count == 4:
        case = [[1,2], [1,3], [1,4], [2,3], [2,4], [3,4]]
        c_list = [1, 2, 3, 4]

        for i in case: # 클라이언트에게 행렬을 달라고 알리는 메시지 전송
            ticket_list1 = [ i for i in range(50)]
            ticket_list2 = [ i for i in range(50, 100)]
            complement = list(set(c_list) - set(i)) #행렬을 받을 클라이언트 둘
            
            #행렬을 받을 클라이언트 랜덤으로 선택
            recv_client, recv_client_ticket, not_recv_client, not_recv_client_ticket = recv_client_choice_lottery(ticket_list1, complement[0], ticket_list2, complement[1])
            
            add_msg = ' matrix ' + ','.join(map(str, i)) + " " + str(recv_client) + "|" + ','.join(map(str, recv_client_ticket)) + "|" + str(not_recv_client) + "|" + ','.join(map(str, not_recv_client_ticket))
            for j in i: # 메시지 전송
                time.sleep(0.01)
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
    group, result_matrix = [], [] #연결된 클라이언트의 소켓정보를 리스트로 묶기 위함
    

    server_file = open("server_log.txt", "w", encoding="UTF-8")

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