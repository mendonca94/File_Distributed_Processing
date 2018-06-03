#Projeto de redes 2017/2018
#
#Grupo 048
#
#Andre Mendonca - 82304
#Tomas Oliveira - 82335
#Ricardo Nunes - 71015

import socket
import sys, os
	#tejo.tecnico.ulisboa.pt
SERVER_ADDRESS = socket.gethostbyname('localhost')
SERVER_PORT = 58048
BUFSIZE = 1024
NAMEFILE = 11110

def transform_msg(data): #Protocolo de envio para o CS
	file_size = str(os.path.getsize(data[2]))
	msg = 'REQ ' + data[1] + ' ' + file_size + ' ' + file_size + '\n'
	return msg

while True:
	msg = raw_input()
	c = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Criacao da socket TCP
	c.connect((SERVER_ADDRESS, SERVER_PORT))

	fw = msg.split()	
	if fw[0] == 'list':
		req = 'LST' + '\n'
		c.send(req)
		CSreply = c.recv(BUFSIZE)
		if CSreply == 'ERR':
			print 'FTP ' + CSreply + '\n'
		else:
			print CSreply
		c.close()
	elif fw[0] == 'request':
		req = transform_msg(fw)
		c.send(req) #Envia protocolo
		f = open('teste.txt','r')
		text = f.read(BUFSIZE)
		while(text):
			c.send(text) #ENvio do ficheiro a tratar
			text = f.read(BUFSIZE)
		f.close()
		CSreply = c.recv(BUFSIZE) #Recebe ficheiro
		if CSreply == 'ERR':
			print 'REP ' + CSreply + '\n'
		else:
			print CSreply
			textRet = CSreply.split()
			textFile = ' '.join(textRet[3:])
			NAMEFILE = NAMEFILE + 1
			g = open(str(NAMEFILE)+".txt", "w+")
			g.write(textFile)
			g.close()
		c.close()
	elif fw == 'exit':
		sys.exit()

