from bottle import run, get, post, view, request, redirect, route
import requests
import json
from threading import Thread
import time
import sys
from urllib3.exceptions import MaxRetryError

messages = set([("Nobody", "Hello!")])
nick = "Nobody"
n = ''

#lista de servidores conhecidos
#list_servers = set(['localhost:8080' , 'localhost:8081', 'localhost:8082'])
list_servers = set(['localhost:8080' , 'localhost:8081'])

@route('/<name>')
@view('index')
def index(name=n):
	return {'messages': messages, 'nick': name}

@get('/')
@view('index')
def index():
	return {'messages': messages, 'nick': nick}

@post('/send')
def sendMessage():
    m = request.forms.get('message')
    n = request.forms.get('nick')
    messages.add((n, m))
    redirect('/'+n)

#retorna a lista de mensagens em formato json
@get('/messages') 
def getMessage(): 
	json_info=json.dumps(list(messages))
	return json_info

#Faz o loop principal para o envio e recebimento das mensagens
def executeMessages():
	while True:
		time.sleep(5)
		N = set([])
		global messages
		for url in list_servers:
			setText = syncMessages(url)
			if setText.difference(messages):
				N = N.union(setText.difference(messages))
		messages = messages.union(N)

#Faz a conexão e sincronização das mensagens			
def syncMessages(url):
	link = "http://" + url + "/messages"
	try:	
		r = requests.get(link)	
		if r.status_code == 200:
			p = json.loads(r.text)
			setText = set((value1, value2) for [value1, value2] in p)
			return setText
	except MaxRetryError:
		print ("Problemas na conexao, número maximo de tentativas!")
	except requests.exceptions.ConnectionError:
		print ("Problemas na conexao nas mensagens")
	return set([])	
			

@get('/peers')# get peers retorna a lista de conhecidos em formato json
def getPeers(): 
	json_info=json.dumps(list(list_servers))
	return json_info
		
#Faz o loop principal para a sincronização dos peers
def executePeers():
	while True:
		time.sleep(1)
		global list_servers
		N = set([])
		for url in list_servers:
			setP = syncPeers(url)
			if setP.difference(list_servers):
				N = N.union(p.difference(list_servers))
		list_servers = list_servers.union(N)


#Faz a sincronização dos peers
def syncPeers(url):
	link = "http://" + url + "/peers"
	try:
		r = requests.get(link)
		if r.status_code == 200:
			p = json.loads(r.text)
			return set(p)

	except MaxRetryError:
		print ("Problemas na conexao, número maximo de tentativas!")
				
	except requests.exceptions.ConnectionError:
		print ("Problemas na conexao do servidores")
	
	return set([])
			


#Inicializa a thread para sincronização dos peers
threadPeers = Thread(None, executePeers, (), {}, None)
threadPeers.start()
#Inicializa a thread para a sincronização das mensagens
threadMessages = Thread(None, executeMessages, (), {}, None)
threadMessages.start()


run(host='localhost', port=int(sys.argv[1]))

