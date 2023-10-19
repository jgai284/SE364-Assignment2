import argparse
import sys
import threading

import select

from communication import *

SERVER_HOST = 'localhost'

stop_thread = False


def get_and_send(client):
    while not stop_thread:
        data = sys.stdin.readline().strip()
        if data:
            send(client.sock, data)


class ChatClient():
    """ Initialize client attributes """

    def __init__(self, name, port, host=SERVER_HOST):
        self.name = name
        self.connected = False
        self.host = host
        self.port = port

        # Initial prompt
        self.prompt = f'[{name}@{socket.gethostname()}]> '

        # Connect to server at port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, self.port))
            print(f'Now connected to chat server@ port {self.port}')
            self.connected = True

            # Send client name
            send(self.sock, 'NAME: ' + self.name)
            data = receive(self.sock)

            # Set client address
            addr = data.split('CLIENT: ')[1]
            self.prompt = '[' + '@'.join((self.name, addr)) + ']> '

            threading.Thread(target=get_and_send, args=(self,)).start()

        except socket.error as e:
            print(f'Failed to connect to chat server @ port {self.port}')
            sys.exit(1)

    def cleanup(self):
        """Erase connection"""
        self.sock.close()

    def run(self):
        """ Chat client main loop """
        while self.connected:
            try:
                sys.stdout.write(self.prompt)
                sys.stdout.flush()

                # Wait for input from stdin and socket
                readable, writeable, exceptional = select.select(
                    [self.sock], [], [])

                for sock in readable:
                    if sock == self.sock:
                        data = receive(self.sock)
                        if not data:
                            print('Client shutting down.')
                            self.connected = False
                            break
                        else:
                            sys.stdout.write(data + '\n')
                            sys.stdout.flush()

            except KeyboardInterrupt:
                print(" Client interrupted. " "")
                stop_thread = True
                self.cleanup()
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', action="store", dest="name", required=True)
    parser.add_argument('--port', action="store",
                        dest="port", type=int, required=True)
    given_args = parser.parse_args()

    port = given_args.port
    name = given_args.name

    client = ChatClient(name=name, port=port)
    client.run()
