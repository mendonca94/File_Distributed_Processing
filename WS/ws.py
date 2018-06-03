#Projeto de redes 2017/2018
#
#Grupo 048
#
#Andre Mendonca - 82304
#Tomas Oliveira - 82335
#Ricardo Nunes - 71015

import socket
import sys
import os, signal

HOST = socket.gethostbyname('localhost')
PORT_UDP = 21568
PORT_TCP = 59000
ADDRESS = (HOST,PORT_UDP) #Endereco de ligacao WS-CS
ADDRESS2 = (HOST,PORT_TCP) #Endereco de Ligacao CS-WS
NAMEFILE = 0 #Nome do ficheiro
KEYWORDS = ['WCT','UPP','LOW','FLW']

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Criacao do socket UDP
#hostname = socket.getfqdn()
#ip = socket.gethostbyname(hostname)
ip = '127.0.0.1' 
msg = 'REG UPP LOW FLW WCT ' + ip + ' ' + str(PORT_UDP) #Mensagem de protocolo para CS
protocol = msg.split()
try:
	if protocol[0] == 'REG':
		ptcList = []
		for i in protocol:
			if i in KEYWORDS:
				ptcList.append(i)
		protocolMsg = protocol[0] + ' ' 
		for j in ptcList:
			protocolMsg = protocolMsg + j + ' '

		protocolMsg = protocolMsg + protocol[-2] + ' ' + protocol[-1] + '\n'
		s.sendto(protocolMsg, (HOST, PORT_UDP)) #Envio do protocolo para registar
		CSreply = s.recvfrom(1024)
		if CSreply[0] == 'RAK OK\n':
			print CSreply[0]
		elif CSreply[0] == 'RAK NOK\n':
			print CSreply[0]
	c = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Criacao do socket TCP
	c.bind(ADDRESS2)
	c.listen(5)
	while True:
		CS_socket,CS_addr = c.accept()
		NAMEFILE = NAMEFILE + 1
		filepathIN = os.path.join('input_files', str(NAMEFILE) + '.txt') #Guarda ficheiro na diretoria input_files
		if not os.path.exists('input_files'):
			os.makedirs('input_files')
		f = open(filepathIN, 'w+')
		text = CS_socket.recv(1024) #Recebe ficheiro a tratar
		f.write(text)

		f.seek(0)
		content = f.read()
		f.close()
		uppertext = content.upper() #Realiza UPP sobvre o texto recebido
		filepathOUT = os.path.join('output_files', str(NAMEFILE) + '.txt') #Guarda ficheiro na diretoria output_files
		if not os.path.exists('output_files'):
			os.makedirs('output_files')
		g = open(filepathOUT, 'w+')
		g.write(uppertext)
		g.seek(0)
		textsend = g.read(1024)
		while(textsend):
			CS_socket.send(textsend) #Envia ficheiro tratado
			textsend = g.read(1024)
		g.close()
except KeyboardInterrupt: #Deteccao do uso do CTRL-C para desregisto
	print '\n'
	protocolMsg2 = 'UNR ' + ' ' + protocol[-2] + ' ' + protocol[-1] + '\n'
	s.sendto(protocolMsg2, (HOST, PORT_UDP))
	CSreply = s.recvfrom(1024)
	if CSreply[0] == 'ERR':
		print 'UAK ' + CSreply[0] + '\n'
	elif CSreply[0] == 'OK':
		print 'UAK ' + CSreply[0] + '\n'
	sys.exit(0)
s.close()
