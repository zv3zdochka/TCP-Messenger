# TCP Chat Server and Client

---

This project is a client-server application for exchanging messages with support for chats and rooms. The server and client communicate via the TCP protocol.

## Key Features

### Server

- **User Authentication**:
    - Connecting new users with registration.
    - Login of registered users with password verification.
    - Storing passwords as SHA-1 hashes.

- **General Chat and Rooms**:
    - Maintaining a general chat.
    - Creating rooms and connecting to them.
    - Exchanging messages within rooms.
    - Switching between rooms and the general chat.

- **Commands**:
    - `/create <name>` — creating a new room with password generation.
    - `/join <name> <password>` — connecting to a room using a password.
    - `/exit` — exiting a room and returning to the general chat.

- **Data Persistence**:
    - Saving user and room data upon server shutdown.
    - Restoring data upon server restart.

### Client

- **Connection to the Server**:
    - Entering a login and password for authentication.
    - Sending and receiving messages in real-time.
    - Handling system commands and messages.

## Installation and Usage

### Server

1. Ensure you have Python 3.8 or higher installed.
2. Install the necessary dependencies:
   ```bash
   pip install requirements.txt
   ```
3. Run the server:
   ```bash
   python Server.py
   ```

### Client

1. Ensure you have Python 3.8 or higher installed.
2. Install the necessary dependencies:
   ```bash
   pip install requirements.txt
   ```
3. Run the client application:
   ```bash
   python client.py
   ```

## File Descriptions

### `Server.py`

This file contains the implementation of the server-side of the application. Key functions include:

- Handling client connections.
- User authentication.
- Managing the general chat and supporting rooms.
- Saving and restoring data upon server shutdown and restart.

Key functions and variables:

- `save_data()`, `load_data()` — functions for saving and loading data.
- `handle_client()` — function for handling messages from the client.
- `broadcast()` — function for sending messages to all clients.
- `shutdown_server()` — signal handler for gracefully shutting down the server.

### `Client.py`

This file contains the implementation of the client-side of the application. Key functions include:

- Connecting to the server.
- Authenticating with login and password input.
- Sending messages to and receiving messages from the server.
- Handling chat commands and system messages.

Key functions and variables:

- `keyboard_input()` — function for sending messages inputted by the user.
- `receive_messages()` — function for receiving and displaying messages from the server.

## Usage

1. Start the server-side as described above.
2. Launch the client application, specifying the server's IP address and port.
3. After successful connection, enter your login and password. If it's a new login, you'll need to enter the password twice for registration.
4. After authentication, you can use chat commands or simply communicate with other users.

### Example Commands

- Create a room:
  ```
  /create myroom
  ```
- Join a room:
  ```
  /join myroom 1234
  ```
- Exit a room and return to the general chat:
  ```
  /exit
  ```

## Data Persistence

The server saves user and room data upon normal shutdown (Ctrl+C). This data will be loaded upon the next server restart.

## System Requirements

- Python 3.8 or higher
- Libraries: `socket`, `threading`, `datetime`, `functools`, `sys`, `colorama`, `hashlib`, `signal`, `pickle`, `os`.

## License

This project is licensed under the [Apache 2.0](LICENSE) license.