#Projeto de redes 2017/2018
#
#Grupo 048
#
#Andre Mendonca - 82304
#Tomas Oliveira - 82335
#Ricardo Nunes - 71015

import socket, os, sys
from select import select

HOST = socket.gethostbyname('localhost')
PORT = 58048
PORT_UDPWS = 21568
PORT_TCPWS = 59000
BUFSIZE = 1024
ADDRESS = (HOST, PORT) #Endereco deLigacao User-CS
ADDRESS2 = (HOST, PORT_UDPWS) #Endereco de Ligacao WS-CS
ADDRESS3 = (HOST, PORT_TCPWS) #Endereco de Ligacao CS-WS
KEYWORDS = ['WCT','UPP','LOW','FLW']
NAMEFILE = 11110 #Nome do ficheiro recebido

tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Criacao socket TCP
tcpSerSock.bind(ADDRESS)
tcpSerSock.listen(5)

udpSerSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Criacao socket UDP
udpSerSock.bind(ADDRESS2)
udpSerSock.setblocking(0)

socket_list = [tcpSerSock,udpSerSock]

def checklist(word): #Verificacao de PTC
    taskf = open('file_processing_tasks.txt','r')
    text = taskf.read()
    taskf.close()
    words = text.split()
    for i in words:
        if i == word: 
            return True
    return False

def replyUser(rt,size,data):
    if rt in ['WCT', 'FLW']:
        return 'REP ' + 'R ' + size + " " + data
    elif rt in ['UPP', 'LOW']:
        return 'REP ' + 'F ' + size + " " + data

def read_tcp(s): #Aceitar ligacoes
    client,addr = s.accept()
    data = client.recv(1024)
    return data,client,addr

def unr_ws(data): #Desregisto do WS
    port = data[-1]
    ip = data[-2]
    fin = open('file_processing_tasks.txt','r')
    lines = fin.readlines()
    fin.close()
    fout = open('file_processing_tasks.txt','w')
    for line in lines:
        if port not in line:
            fout.write(line)
    fout.close()

def reg_ws(data): #Registo do WS
    a = data[0].split()
    flag = 0
    taskf = open('file_processing_tasks.txt','a')
    for i in a:
        if i in KEYWORDS: 
            taskf.write(i + ' ' + a[-2] + ' ' + a[-1] + '\n')
            flag = flag + 1
    taskf.close()
    if(flag==0):
    	return 'RAK NOK' + '\n'
    else:
    	return 'RAK OK' + '\n'


def makeList(data): #Lista de PTC
	j = 1
	lista = ''
	keywords = []
	for i in range(0,len(data)):
		if data[i][:3] not in keywords:
			keywords.append(data[i][:3])
			if data[i][:3] == 'UPP':
				lista = lista + str(j) + '- ' + data[i][:3] + ' - ' + 'convert to upper case' + '\n'
			elif data[i][:3] == 'LOW':
  				lista = lista + str(j) + '- ' + data[i][:3] + ' - ' + 'convert to lower case' + '\n'
 			elif data[i][:3] == 'WCT':
  				lista = lista + str(j) + '- ' + data[i][:3] + ' - ' + 'word count' + '\n'
  			elif data[i][:3] == 'FLW':
  				lista = lista + str(j) + '- ' + data[i][:3] + ' - ' + 'find longest word' + '\n'
  			j = j + 1
	return lista

while True:
    inputready,outputready,exceptready = select(socket_list,[],[])
    for s in inputready:
        if s is tcpSerSock:
            client_input,client_socket,addr = read_tcp(tcpSerSock)
            req = client_input.split()
            socket_list.append(client_socket)
            if req[0] == 'LST':
                taskf = open('file_processing_tasks.txt','r')
                d = taskf.readlines()
                if not d:
                    client_socket.send('FPT EOF' + '\n')
                    taskf.close()
                else:
                    lista = makeList(d)
                    client_socket.send(lista)
                    taskf.close()
            elif req[0] == 'REQ':
                flag = checklist(req[1])
                if  flag == False:
                    client_socket.send('REP EOF' + '\n')
                else:
                    NAMEFILE = NAMEFILE + 1
                    child_pid=os.fork() #Criacao de processo filho
                    if child_pid==0:
                        filepath = os.path.join('input_files', str(NAMEFILE) + '.txt') #Guarda ficheiro na diretoria input_files
                        if not os.path.exists('input_files'):
                            os.makedirs('input_files')
                        f = open(filepath, "w+")
                        text = client_socket.recv(BUFSIZE)
                        f.write(text)
                        f.seek(0)
                        l = f.read(1024)
                        WS_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        WS_Socket.connect(ADDRESS3)
                        f.seek(0)
                        textsend = f.read(1024)
                        while(textsend):
                            WS_Socket.send(textsend)
                            textsend = f.read(1024)
                            WS_Socket.send(textsend)
                        f.close()
                        filepathOUT = os.path.join('output_files', str(NAMEFILE) + '.txt') #Guarda ficheiro na diretoria output_files
                        if not os.path.exists('output_files'):
                            os.makedirs('output_files')
                        g = open(filepathOUT, 'w+')
                        replyWS = WS_Socket.recv(BUFSIZE)
                        g.write(replyWS)
                        g.seek(0)
                        returnData = g.read() 
                        g.close()
                        textReplyUser = replyUser(req[1],req[2],returnData)
                        client_socket.send(textReplyUser) 
                        sys.exit()
            else:
            	client_socket.send("ERR")

        elif s is udpSerSock:
            d = udpSerSock.recvfrom(1024); #Ligacao UDP
            data = d[0].split()
            if data[0] == 'REG':
                status = reg_ws(d)
                udpSerSock.sendto(status,d[1]) #Envia status para (IP,PORT) especifico
            elif data[0] == 'UNR':
            	unr_ws(data)
            	udpSerSock.sendto('OK',d[1])
            else:
            	udpSerSock.sendto('ERR',d[1])
        else:
            s.close()
            socket_list.remove(s)