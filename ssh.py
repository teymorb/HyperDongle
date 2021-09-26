import select
import threading
import socket
import paramiko
import sys
import time

def handler(chan, host, port):
    sock = socket.socket()
    try:
        sock.connect((host, port))
    except Exception as e:
        print("Forwarding request to %s:%d failed: %r" % (host, port, e))
        return

    print(
        "Connected!  Tunnel open %r -> %r -> %r"
        % (chan.origin_addr, chan.getpeername(), (host, port))
    )
    while True:
        r, w, x = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            chan.send(data)
        if chan in r:
            data = chan.recv(1024)
            if len(data) == 0:
                break
            sock.send(data)
    chan.close()
    sock.close()
    print("Tunnel closed from %r" % (chan.origin_addr,))


def reverse_forward_tunnel(server_port, remote_host, remote_port, transport):
    transport.request_port_forward("", server_port)
    while True:
        chan = transport.accept(1000)
        if chan is None:
            continue
        thr = threading.Thread(
            target=handler, args=(chan, remote_host, remote_port)
        )
        thr.setDaemon(True)
        thr.start()


if __name__ == "__main__":
    host = "54.167.166.244" if len(sys.argv) < 2 else sys.argv[1]
    user = "ec2-user" if len(sys.argv) < 3 else sys.argv[2]
    print(f"{user}@{host}")
    exit()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, key_filename="../open-key-pair.pem", username=user)
    client.get_transport().open_session()

    # port = client.get_transport().request_port_forward("", 43022)
    # print(f'Port allocated is {port}')

    reverse_forward_tunnel(43022, "localhost", "22", client.get_transport())

    # client.invoke_shell()
    # print(f"Welcome to {host}")
    # open = True
    # command = input(f"{user}@{host}: ")
    # while open:
    #     # print(f"Running {command} on remote host {host}")
    #     (stdin, stdout, stderr) = client.exec_command(command)
    #     time.sleep(3)
    #     print("Output of command:\t" + str(stdout.read()))
    #     print("Errors from command:\t" + str(stderr.read()))
    #     stdout = stdout.read()
    #     stderr = stderr.read()
    #     command = input(f"{user}@{host}: ")
    #     if command.lower() == "exit" or command.lower() == "logout":
    #         open = False
    # print("Logout successful")
    # client.get_transport().close()
    # client.close()