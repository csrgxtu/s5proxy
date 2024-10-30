import socket
import threading
import select
import traceback
import logging


logging.basicConfig(level=logging.DEBUG)
SOCKS_VERSION = 5


class Proxy:
    def __init__(self) -> None:
        self.username = 'username'
        self.password = 'password'
        self.logger = logging.getLogger('Proxy')

    def handle_client(self, connection, client_addr):
        # greeting header
        # read and unpack 2 bytes from a client
        #          +----+----------+----------+
        #          |VER | NMETHODS | METHODS  |
        #          +----+----------+----------+
        #          | 1  |    1     | 1 to 255 |
        #          +----+----------+----------+
        version, nmethods = connection.recv(2)
        self.logger.info(f'Greeting from client version->{version} nmethods->{nmethods}')

        # get available methods [0, 1, 2]
        methods = [ord(connection.recv(1)) for _ in range(nmethods)]
        self.logger.info(f'Greeting methods->{set(methods)}')

        # accept only USERNAME/PASSWORD auth
        if 2 not in set(methods):
            # clone connection
            self.logger.info(f'Client not support Username/Password method, terminate!')
            connection.close()
            return

        # send welcome message
        connection.sendall(bytes([SOCKS_VERSION, 2]))
        self.logger.info(f'Server Greeting back to client')

        # verify Username/Password
        if not self.verify_credentials(connection):
            self.logger.info(f'Credential verify failed')
            return

        # request (version = 5)
        version, cmd, _, address_type = connection.recv(4)
        self.logger.info(f'Debug: address_type {address_type}')

        if address_type == 1:  # IPV4
            data = connection.recv(4)
            address = socket.inet_ntoa(data)
            self.logger.info(f'IPV4 data to Target Address {data} -> {address}')
            # address = '142.250.69.206'
            address = '108.177.125.139'
        elif address_type == 3:  # Domain name
            domain_length = connection.recv(1)[0]
            address = connection.recv(domain_length)
            self.logger.info(f'Debug: {domain_length} -> {address}')
            address = socket.gethostbyname(address)
            self.logger.info(f'DomainName to Target Address {address}')
            address = '108.177.125.139'

        # convert bytes to unsigned short array
        port = int.from_bytes(connection.recv(2), 'big', signed=False)
        self.logger.info(f'Target Port {port}')

        self.logger.info(f'CMD: {cmd}')
        try:
            if cmd == 1:  # CONNECT
                remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote.connect((address, port))
                bind_address = remote.getsockname()
                self.logger.info(f'Connected to {address} {port}')
            else:
                connection.close()

            addr = int.from_bytes(socket.inet_aton(bind_address[0]), 'big', signed=False)
            port = bind_address[1]
            self.logger.info(f'Proxy Sock {bind_address[0]}:{port}')

            reply = b''.join([
                SOCKS_VERSION.to_bytes(1, 'big'),
                int(0).to_bytes(1, 'big'),
                int(0).to_bytes(1, 'big'),
                int(1).to_bytes(1, 'big'),
                addr.to_bytes(4, 'big'),
                port.to_bytes(2,'big')
            ])
        except Exception as e:
            self.logger.info(traceback.format_exc())

            reply = self.generate_failed_reply(address_type, 5)

        connection.sendall(reply)

        # establish data exchange
        self.logger.info(f'reply[1]: {reply[1]} cmd: {cmd}')
        if reply[1] == 0 and cmd == 1:
            self.exchange_loop(connection, remote)

        remote.close()
        connection.close()
        self.logger.info(f'connection closed {client_addr}')

    def verify_credentials(self, connection):
        version = ord(connection.recv(1))  # should be 1

        username_len = ord(connection.recv(1))
        username = connection.recv(username_len).decode('utf-8')
    
        password_len = ord(connection.recv(1))
        password = connection.recv(password_len).decode('utf-8')

        if username == self.username and password == self.password:
            # success, status = 0
            response = bytes([version, 0])
            connection.sendall(response)
            return True

        # failure, status != 0
        response = bytes([version, 0xFF])
        connection.sendall(response)
        connection.close()
        return False

    def generate_failed_reply(self, address_type, error_number):
        return b''.join([
            SOCKS_VERSION.to_bytes(1, 'big'),
            error_number.to_bytes(1, 'big'),
            int(0).to_bytes(1, 'big'),
            address_type.to_bytes(1, 'big'),
            int(0).to_bytes(4, 'big'),
            int(0).to_bytes(4, 'big')
        ])

    def exchange_loop(self, client, remote):
        while True:
            # wait until client or remote is available for read
            r, w, e = select.select([client, remote], [], [])
            if e:
                self.logger.info(f'Exceptions: {e}')

            if client in r:
                try:
                    data = client.recv(4096)
                    self.logger.info(f'Read {len(data)} bytes from client')
                except ConnectionResetError as ex:
                    self.logger.error(f'Client connection reseted: {ex}')
                    break

                try:
                    sent_size = remote.send(data)
                    self.logger.info(f'Sent {sent_size} bytes to remote')
                    if sent_size <= 0:
                        break
                except ConnectionResetError as ex:
                    self.logger.error(f'Remote connection reseted {ex}')
                    break

            if remote in r:
                try:
                    data = remote.recv(4096)
                    self.logger.info(f'Read {len(data)} bytes from remote')
                except ConnectionResetError as ex:
                    self.logger.error(f'Remote connection reseted {ex}')
                    break

                try:
                    sent_size = client.send(data)
                    self.logger.info(f'Sent {sent_size} bytes to client')
                    if sent_size <= 0:
                        break
                except ConnectionResetError as ex:
                    self.logger.error(f"Client connection reseted {ex}")
                    break

    def run(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()

        self.logger.info(f'Socks5 proxy server is running on {host}:{port}')

        while True:
            conn, addr = s.accept()
            self.logger.info(f'* new connection from {addr}')
            t = threading.Thread(target=self.handle_client, args=(conn, addr))
            t.start()


if __name__ == '__main__':
    proxy = Proxy()
    proxy.run('0.0.0.0', 3000)