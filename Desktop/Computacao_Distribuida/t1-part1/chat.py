from bottle import run, get, post, view, request, redirect, route

messages = [("Nobody", "Hello!")]
nick = "Nobody"
n = ''

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
    messages.append([n, m])
    redirect('/'+n)


run(host='localhost', port=8080)

