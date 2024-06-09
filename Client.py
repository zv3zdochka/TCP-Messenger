import threading
import socket
import datetime
import functools
import sys
from colorama import Fore, Style

flag = False
stop_flag = False


def handle_connection_reset(func):
    if stop_flag:
        sys.exit()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ConnectionResetError, IndexError, ConnectionRefusedError):
            print(Fore.RED + Style.BRIGHT + "Connection Error")
            sys.exit()

    return wrapper


@handle_connection_reset
def keyboard_input(s):
    global flag
    if stop_flag:
        sys.exit()
    while True:
        if flag:
            c_t = datetime.datetime.now().strftime("%H:%M:%S")
            user_input = input()
            print('\033[A\033[K', end='')
            print(Fore.GREEN + f'[ I | {c_t}] {user_input}')
            s.sendall(user_input.encode())
        else:
            user_input = input()
            s.sendall(user_input.encode())


def receive_messages(s):
    global flag
    if stop_flag:
        sys.exit()
    try:
        while True:
            data = s.recv(1024).decode()
            if data == 'Now you can use the chat.' or 'Now you can use the chat again.':
                flag = True
            if 'Incorrect input.' == data or 'Your first and second passwords are different.' == data or 'You password is wrong.' == data:
                exit(f'{data}')
            else:
                if data[0:3] == "Sys":
                    print(Fore.BLUE + data)
                elif data[0] == '[':
                    print(Fore.MAGENTA + data)
                else:
                    print(Fore.YELLOW + Style.BRIGHT + data)
    except (ConnectionResetError, ConnectionRefusedError, KeyboardInterrupt, IndexError):
        print(Fore.RED + Style.BRIGHT + "Connection Error")
        sys.exit()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 7777))

input_thread = threading.Thread(target=keyboard_input, args=(s,))
input_thread.daemon = True
input_thread.start()

receive_thread = threading.Thread(target=receive_messages, args=(s,))
receive_thread.daemon = True
receive_thread.start()

input_thread.join()
receive_thread.join()
