import select
import sys
import signal
import argparse

from communication import *

SERVER_HOST = 'localhost'


class ChatServer(object):
    """initialize attributes"""

    def __init__(self, port, backlog=5):
        self.clients = 0
        self.clientmap = {}
        self.outputs = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((SERVER_HOST, port))
        self.server.listen(backlog)

        signal.signal(signal.SIGINT, self.erase_connection)

        print(f'Server listening to port: {port} ...')

    """initialize functions"""

    def erase_connection(self, signum, frame):
        """Erasing client connections"""
        print('Shutting down server...')

        # Close existing client sockets
        for output in self.outputs:
            output.close()

        self.server.close()

    def get_client_name(self, client):
        """ Return the name of the client """
        info = self.clientmap[client]
        host, name = info[0][0], info[1]
        return '@'.join((name, host))

    def run(self):
        inputs = [self.server]
        self.outputs = []
        running = True
        while running:
            try:
                readable, writeable, exceptional = select.select(
                    inputs, self.outputs, [])
            except select.error as e:
                break

            for sock in readable:
                sys.stdout.flush()
                if sock == self.server:
                    # handle the server socket
                    client, address = self.server.accept()
                    print(
                        f'Chat server: got connection {client.fileno()} from {address}')
                    # Read the login name
                    cname = receive(client).split('NAME: ')[1]

                    # Compute client name and send back
                    self.clients += 1
                    send(client, f'CLIENT: {str(address[0])}')
                    inputs.append(client)

                    self.clientmap[client] = (address, cname)
                    # Send joining information to other clients
                    msg = f'\n(Connected: New client ({self.clients}) from {self.get_client_name(client)})'
                    for output in self.outputs:
                        send(output, msg)
                    self.outputs.append(client)

                else:
                    # handle all other sockets
                    try:
                        data = receive(sock)
                        if data:
                            # Send as new client's message...
                            msg = f'\n#[{self.get_client_name(sock)}]>> {data}'

                            # Broadcast message to other clients
                            for output in self.outputs:
                                if output != sock:
                                    send(output, msg)
                        else:
                            print(f'Chat server: {sock.fileno()} hung up')
                            self.clients -= 1
                            sock.close()
                            inputs.remove(sock)
                            self.outputs.remove(sock)

                            # Sending client leaving information to others
                            msg = f'\n(Now hung up: Client from {self.get_client_name(sock)})'

                            for output in self.outputs:
                                send(output, msg)
                    except socket.error as e:
                        inputs.remove(sock)
                        self.outputs.remove(sock)

        self.server.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Socket server for assignment 2')
    parser.add_argument('--name', action="store", dest="name", required=True)
    parser.add_argument('--port', action="store",
                        dest="port", type=int, required=True)
    given_args = parser.parse_args()
    port = given_args.port
    name = given_args.name

    server = ChatServer(port)
    server.run()
