"""
Name: Kenniel Torres

- Notes -
> Requires PLY package. For more information: https://www.dabeaz.com/ply/
> For installation: pip3 install ply
> Developed with all files in the same directory
> To run: python3 Assignment4

* Read report for use and commands. *

"""

from ply import lex
import ply.yacc as yacc
import sys
import socket
import threading

reserved = {
            'START_SERVER':'START_SERVER',
            'SET_SERVPORT':'SET_SERVPORT',
            'GET_SERVPORT':'GET_SERVPORT',
            'START_CLIENT':'START_CLIENT',
            'SET_CLIPORT':'SET_CLIPORT',
            'GET_CLIPORT':'GET_CLIPORT',
            'CLOSE_SESSION':'CLOSE_SESSION',
            'CLOSE':'CLOSE'
            }

operators = {'+': 'SUM',
            '-': 'MINUS',
            '~': 'NEGATION',
            '*': 'MULT',
            '/': 'DIV',
            '=': 'EQUALS',
            '<': 'LESSTHAN',
            '>': 'GREATERTHAN',
            '&': 'AND',
            '|': 'OR'}

tokens = ['ID','NUMBER','PERIOD','DELIMITERS','LPAREN','RPAREN',
            'LBRACKET','RBRACKET','COMMA','SEMICOLON','OPERATORS',
            'DUALOPERATORS','GREATEROREQUAL','ASSIGN','NOTEQUAL',
            'LESSOREQUAL']

tokens += list(reserved.values()) + list(operators.values())

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  #Check for reserved words
    return t

t_PERIOD = r'\.'

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_DELIMITERS(t):
    r'\( | \) | \[ | \] | \, | \;'
    if t.value == '(':
        t.type = 'LPAREN'
    elif t.value == ')':
        t.type = 'RPAREN'
    elif t.value == '[':
        t.type = 'LBRACKET'
    elif t.value == ']':
        t.type = 'RBRACKET'
    elif t.value == ',':
        t.type = 'COMMA'
    elif t.value == ';':
        t.type = 'SEMICOLON'
    return t

def t_OPERATORS(t):
    r'\+ | \- | \~ | \* | \/ | \= | \< | \> | \& | \| '
    if t.value in operators: #Check for operators list
        t.type = operators[t.value]
    return t

def t_DUALOPERATORS(t):
    r'\<\= | \>\= | \:\= | \!\= '
    if t.value == '>=':
        t.type = 'GREATEROREQUAL'
    elif t.value == ':=':
        t.type = 'ASSIGN'
    elif t.value == '!=':
        t.type = 'NOTEQUAL'
    elif t.value == '<=':
        t.type = 'LESSOREQUAL'
    return t

t_ignore = ' \t'

def t_newline(t):
    r'\n'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print("Illegal character")
    t.lexer.skip(1)

lexer = lex.lex() #Initializes lex

#Parsing
def p_start_server(p):
    'start : START_SERVER'
    execute('server')

def p_get_servport(p):
    'start : GET_SERVPORT'
    print(getServerPort())

def p_set_servport(p):
    'start : SET_SERVPORT NUMBER'
    setServerPort(p[2])
    print("Server port changed! New server port:",getServerPort())

def p_start_client(p):
    'start : START_CLIENT'
    execute('client')

def p_set_cliport(p):
    'start : SET_CLIPORT NUMBER'
    setClientPort(p[2])
    print("Client port changed! New client port:",getClientPort())

def p_get_cliport(p):
    'start : GET_CLIPORT'
    print(getClientPort())

def p_close(p):
    'start : CLOSE'
    sys.exit(0)

def p_error(p):
    print("Syntax error in input!")

parser = yacc.yacc() #Initializes the parser


#Server & Client Code
serverPort = 8000
clientPort = 8000
bufferSize = 1024
serverSocketFamily = socket.AF_INET
serverSocketType = socket.SOCK_STREAM
clientSocketFamily = socket.AF_INET
clientSocketType = socket.SOCK_STREAM
running = False

def setServerPort(p):
    if p < 1024:
        print("Port value must be greater than 1023")
        sys.exit(0)
    elif not running:
        global serverPort
        serverPort = p
    else:
        print("Unable to change port while server is running!")
        sys.exit(0)

def setClientPort(p):
    global clientPort
    clientPort = p

def setServerSocketFamily(socketFamily):
    if not running:
        global serverSocketFamily
        serverSocketFamily = socketFamily
    else:
        print("Unable to change socket family while server is running!")
        sys.exit(0)

def setServerSocketType(socketType):
    global serverSocketType
    serverSocketType = socketType

def setClientSocketFamily(socketFamily):
    global clientSocketFamily
    clientSocketFamily = socketFamily

def setClientSocketType(socketType):
    global clientSocketType
    clientSocketType = socketType

def getServerPort():
    global serverPort
    return serverPort

def getClientPort():
    global clientPort
    return clientPort

def getServerSocketFamily():
    global serverSocketFamily
    return serverSocketFamily

def getServerSocketType():
    global serverSocketType
    return serverSocketType

def getClientSocketFamily():
    global clientSocketFamily
    return clientSocketFamily

def getClientSocketType():
    global clientSocketType
    return clientSocketType


class Server:
    sock = socket.socket(serverSocketFamily, serverSocketType)
    connections = []

    def __init__(self):
        global running
        running = True
        self.sock = socket.socket(serverSocketFamily, serverSocketType)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0',serverPort))
        self.sock.listen(1)
        print("Server running.", self.sock.getsockname())
        print("<-TO TERMINATE THE SERVER, CLOSE THE TERMINAL OR")
        print("PRESS CTRL+C TO RETURN TO THE MAIN PROGRAM")
        print("AND TYPE \'CLOSE\' TO TERMINATE THE MAIN PROGRAM->")

    def run(self):
        while True:
            c, a = self.sock.accept()
            cThread = threading.Thread(target=self.handler, args=(c, a))
            cThread.daemon = True
            cThread.start()
            self.connections.append(c)
            print(str(a[0])+':'+str(a[1]), "connected")
            print("Waiting for message...")

    def handler(self, c, a):
        T = False
        while True:
            data = c.recv(bufferSize)
            for connection in self.connections:
                if str(data, 'utf-8') == "CLOSE_SESSION" and connection == c:
                    T = True
                    break
            if not data or T:
                print(str(a[0])+':'+str(a[1]), "disconnected")
                self.connections.remove(c)
                c.close()
                break

            print('From client '+str(a[0])+':'+str(a[1])+' >', str(data,'utf-8')) #Data received from client
            c.sendall(b'Waiting for message...')
            data = input('') #Data input from server
            c.sendall(b'From server > '+data.encode()) #Send server data to client
            print("Waiting for message...")


    def sendExit(self):
        for connection in self.connections:
            connection.send(b'\x11')


class Client:
    eCode = ""
    sock = socket.socket(clientSocketFamily, clientSocketType)
    def sendMsg(self):
        while True:
            try:
                t = input('')
                self.sock.send(bytes(t, 'utf-8'))
            except OSError:
                pass
            if t == 'CLOSE_SESSION' or self.eCode == 'CLOSE_SESSION':
                self.sock.close()
                break

    def __init__(self, address):
        self.eCode = ""
        self.sock = socket.socket(clientSocketFamily, clientSocketType)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((address, clientPort))
        iThread = threading.Thread(target=self.sendMsg)
        iThread.daemon = True
        iThread.start()
        print('Connected:')
        while True:
            data = self.sock.recv(bufferSize)
            if not data:
                break
            if data == b'\x11':
                self.eCode = 'CLOSE_SESSION'
                self.sock.close()
                break
            else:
                print(str(data, 'utf-8'))



def execute(t):
    print("Trying to connect.")
    if(t == 'client'):
        try:
            client = Client('0.0.0.0') #Displays IP 127.0.0.1
        except KeyboardInterrupt:
            pass
        except:
            print("Could not establish connection with server!")
    else:
        try:
            server = Server()
            server.run()
        except KeyboardInterrupt:
            server.sendExit()
            pass
        except:
            print("Could not start up the server!")


#Main Program
def main():
    print('Welcome!\n* Note: Server and Client Ports must be changed before starting.')
    while True:
        try:
            console = input('Console >>> ')
        except EOFError:
            break
        except KeyboardInterrupt:
            break
        if not console:
            continue
        result = parser.parse(console)
        if not result == None:
            print(result)


if __name__ == "__main__":
    main()
