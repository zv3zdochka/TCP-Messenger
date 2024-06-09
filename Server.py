import random
import socket
import threading
import datetime
import functools
import hashlib
import signal
import pickle
import sys
import os
from colorama import Fore, Style

filename = "server_data.pickle"
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 7777))
client_sockets = []
base = {}
di = {}  # log = hash_pass
rooms = {'Base': []}
room_pin = {}
logins = set()
names = set()


def save_data():
    data = {
        "di": di,
        "room_pin": room_pin,
        "logins": logins
    }
    with open(filename, "wb") as file:
        pickle.dump(data, file)


def load_data():
    if os.path.exists(filename):
        with open(filename, "rb") as file:
            data = pickle.load(file)
            return data
    return None


def shutdown_server(signum, frame):
    print(Fore.RED + Style.BRIGHT + "Saving data, disconnecting clients, and stopping server.")
    save_data()
    for sock in client_sockets:
        sock.close()
    server_socket.close()
    sys.exit(Fore.RED + Style.BRIGHT + 'Server Stopped, data saved, sockets closed.')


def remove_key(d, key):
    r = dict(d)
    del r[key]
    return r


def handle_connection_reset(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConnectionResetError:
            try:
                msg = str(base.get(str(args[1]))[0]) + ' disconnected'
                remove_key(base, str(args[1]))
                printer(f"{msg}", client_socket, True)
                client_sockets.remove(args[0])
                broadcast(msg, args[0], base.get(str(args[1]))[-1], True)
                names.remove(base.get(str(args[1]))[0])
            except:
                pass

    return wrapper


def broadcast(msg, sender_socket, room, prop=False):
    global base, rooms
    if prop:
        for client_sockete in rooms.get(str(room)):
            if client_sockete != sender_socket:
                current_time = datetime.datetime.now().strftime("%H:%M:%S")
                client_sockete.send(f"System: [{current_time}] {msg}".encode())
    else:
        cl_sock = rooms.get(str(room))
        if cl_sock:
            for client_sockete in cl_sock:
                if client_sockete != sender_socket:
                    client_addresss = sender_socket.getpeername()
                    log = base.get(str(client_addresss))[0]
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    client_sockete.send(f"[{log} | {current_time}] {msg}".encode())


def printer(msg, log, phase=False):
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    if phase:
        print(Fore.BLUE + f"System: [{current_time}] {msg}")
    else:
        print(Fore.BLUE + f"System: [{log} | {current_time}] {msg}")


@handle_connection_reset
def handle_client(client_socket, client_address):
    client_socket.send("Hello, enter your login and password separated by a space.".encode())
    data = client_socket.recv(1024).decode().split()
    if len(data) != 2:
        client_socket.send("Incorrect input.".encode())
        client_socket.close()
        return
    else:
        if data[0] in names:
            client_socket.send("You are online from other device".encode())
            client_socket.close()
            return
        if data[0] not in logins:
            client_socket.send("Hello new user, please enter your password one more time.".encode())
            o_pa = client_socket.recv(1024).decode()
            if o_pa != data[1]:
                client_socket.close()
                client_socket.send("Your first and second passwords are different.".encode())
                return
            else:
                hash_pas = hashlib.sha1(bytes(data[1], "UTF-8"))
                hash_pass = hash_pas.hexdigest()
                log, pas = data[0], data[1]
                client_socket.send("Here is your login and password.".encode())
                base[str(client_address)] = [log, hash_pass, client_socket, 'Base']
                di[str(log)] = hash_pass
                client_socket.send(f'Login: {data[0]}\n'.encode())
                client_socket.send(f'Password: {data[1]}\n'.encode())
                client_socket.send("Now you can use the chat.".encode())
                printer(f'New connection from {log}', log, True)
                broadcast(f"New connection from {log}", client_socket, base.get(str(client_address))[-1], True)
                logins.add(log)
                names.add(log)
                bf = rooms.get("Base")
                bf.append(client_socket)
                rooms['Base'] = bf

        else:
            try:
                log = data[0]
                if di.get(log) != hashlib.sha1(bytes(data[1], "UTF-8")).hexdigest():
                    client_socket.send("You password is wrong.".encode())
                    client_socket.close()
                    return
                else:
                    client_socket.send(f'Login: {data[0]} '.encode())
                    client_socket.send(f'Password: {data[1]}\n'.encode())
                    client_socket.send("Now you can use the chat again.\n".encode())
                    printer(f'New connection from {log}', log, True)
                    broadcast(f"New connection from {log}", client_socket, True)
                    base[str(client_address)] = [log, hashlib.sha1(bytes(data[1], "UTF-8")).hexdigest(), client_socket,
                                                 'Base']
                    names.add(log)
                    bf = rooms.get("Base")
                    bf.append(client_socket)
                    rooms['Base'] = bf
            except:
                client_socket.close()
                printer("System: Strange error in registration", client_socket, True)
                return

        client_sockets.append(client_socket)

    while True:
        msg = client_socket.recv(1024).decode()
        if '/create' in msg:

            ms = msg.split()
            if len(ms) != 2:
                client_socket.send("System: Incorrect input with /create. You must use this: /create <name>".encode())
                continue
            else:
                if rooms.get(ms[1]) is None:
                    rooms[str(ms[1])] = [client_socket]
                    t_r = base.get(str(client_address))[-1]
                    room_members = rooms.get(str(t_r))
                    room_members.remove(client_socket)
                    g = base.get(str(client_address))
                    g[-1] = ms[1]
                    base[str(client_address)] = g
                    pin = random.randrange(1000, 9999)
                    hash_pas = hashlib.sha1(bytes(str(pin), "UTF-8"))
                    hash_pass = hash_pas.hexdigest()
                    room_pin[str(ms[1])] = hash_pass
                    client_socket.send(f'System: This is password from your room: {pin}'.encode())
                    log = base.get(str(client_address))[0]
                    printer(f"{log} created room {ms[1]}", log, True)
                    continue
                else:
                    client_socket.send("System: A room with the same name is already exists".encode())
                    continue

        elif '/join' in msg:
            ms = msg.split()
            if len(ms) != 3:
                client_socket.send("System: Incorrect input. Use this scheme: /join <name> <password>".encode())
                continue
            else:
                if room_pin.get(ms[1]) is None:
                    client_socket.send('System: There is not any room with this name'.encode())
                    continue
                else:
                    n_p = room_pin.get(ms[1])
                    hash_pas = hashlib.sha1(bytes(str(ms[2]), "UTF-8"))
                    t_p = hash_pas.hexdigest()
                    if n_p != t_p:
                        client_socket.send('System: Incorrect password'.encode())
                        continue
                    else:
                        room_name = ms[1]
                        base[str(client_address)][-1] = room_name
                        rooms[room_name].append(client_socket)
                        rooms['Base'].remove(client_socket)
                        printer(f"{base[str(client_address)][0]} joined {room_name}", client_socket, True)
                        client_socket.send(f'System: You are join the room: {room_name}'.encode())



        elif '/exit' in msg:
            ms = msg.split()
            if len(ms) != 1:
                client_socket.send("System: Incorrect input. Use this scheme: /exit".encode())
                continue
            room_name0 = base[str(client_address)][-1]
            if room_name0 == 'Base':
                pass
                continue
            room_name = "Base"
            base[str(client_address)][-1] = "Base"
            rooms[room_name].append(client_socket)
            rooms[str(room_name0)].remove(client_socket)
            printer(f"{base[str(client_address)][0]} exited from {room_name0} and joined {room_name}", client_socket,
                    True)
            client_socket.send(f'System: You exited from {room_name0} and joined {room_name}'.encode())
            continue
        print(Fore.YELLOW + Style.BRIGHT + f"[{log} | {datetime.datetime.now().strftime('%H:%M:%S')}] {msg}")
        broadcast(msg, client_socket, base.get(str(client_address))[-1])


signal.signal(signal.SIGINT, shutdown_server)
loaded_data = load_data()
if loaded_data:
    di = loaded_data["di"]
    room_pin = loaded_data["room_pin"]
    logins = loaded_data["logins"]
                                                                                                                                                                                                                                                                                                                                                                                                                    
server_socket.listen(1)
print(Fore.BLUE + Style.BRIGHT + "SERVER IS READY")
while True:
    client_socket, client_address = server_socket.accept()
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.daemon = True
    client_thread.start()
