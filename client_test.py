import socket
IP = "localhost"
port = 8080

my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # делаем переменную, ссылающуюся на сокет сервера
my_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # отключаем создание крупных пакетов
# отключение алгоритма Нейгла
my_socket.connect((IP, port))

while True:
    my_socket.send('connected'.encode())

    data = my_socket.recv(1024)
    data = data.decode()
    print("получено", data)

