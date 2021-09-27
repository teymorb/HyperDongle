import getpass
import socket
import select
import sys
import threading
from optparse import OptionParser
import paramiko

SSH_PORT = 22
DEFAULT_PORT = 4000

g_verbose = True


def handler(chan, host, port):
    sock = socket.socket()
    try:
        verbose(f"Attempting to connect to {host}:{port}")
        sock.connect((host, port))
    except Exception as e:
        verbose("Forwarding request to %s:%d failed: %r" % (host, port, e))
        return

    verbose(
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
    verbose("Tunnel closed from %r" % (chan.origin_addr,))


def reverse_forward_tunnel(remote_host, remote_port, transport, server_port=0):
    try:
        p = transport.request_port_forward("", server_port)
        print(f"FORWARDING REQUEST SUCCESSFUL: all traffic from server port {p} will be forwarded to {remote_host}:{remote_port}")
    except paramiko.ssh_exception.SSHException:
        print(f"TCP Port forwarding request denied on port {remote_port} of server, allowing server to decide port")
        p = transport.request_port_forward("", 0)
        print(f"FORWARDING REQUEST SUCCESSFUL: all traffic from server port {p} will be forwarded to {remote_host}:{remote_port}")
    while True:
        chan = transport.accept(1000)
        if chan is None:
            continue
        thr = threading.Thread(
            target=handler, args=(chan, remote_host, remote_port)
        )
        thr.setDaemon(True)
        thr.start()


def verbose(s):
    if g_verbose:
        print(s)


HELP = """\
Set up a reverse forwarding tunnel across an SSH server, using paramiko. A
port on the SSH server (given with -p) is forwarded across an SSH session
back to the local machine, and out to a remote site reachable from this
network. This is similar to the openssh -R option.
"""


def get_host_port(spec, default_port):
    "parse 'hostname:22' into a host and port, with the port optional"
    if ":" in spec:
        (host, port) = spec.split(":")
        return host, int(port)
    else:
        return spec, 22


def parse_options():
    global g_verbose

    parser = OptionParser(
        usage="usage: %prog [options] <ssh-server>[:<server-port>]",
        version="%prog 1.0",
        description=HELP,
    )
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        default=True,
        help="squelch all informational output",
    )
    parser.add_option(
        "-p",
        "--remote-port",
        action="store",
        type="int",
        dest="port",
        default=DEFAULT_PORT,
        help="port on server to forward (default: %d)" % DEFAULT_PORT,
    )
    parser.add_option(
        "-u",
        "--user",
        action="store",
        type="string",
        dest="user",
        default=getpass.getuser(),
        help="username for SSH authentication (default: %s)"
        % getpass.getuser(),
    )
    parser.add_option(
        "-K",
        "--key",
        action="store",
        type="string",
        dest="keyfile",
        default=None,
        help="private key file to use for SSH authentication",
    )
    parser.add_option(
        "",
        "--no-key",
        action="store_false",
        dest="look_for_keys",
        default=True,
        help="don't look for or use a private key file",
    )
    parser.add_option(
        "-P",
        "--password",
        action="store_true",
        dest="readpass",
        default=False,
        help="read password (for key or password auth) from stdin",
    )
    parser.add_option(
        "-r",
        "--remote",
        action="store",
        type="string",
        dest="remote",
        default=None,
        metavar="host:port",
        help="remote host and port to forward to",
    )
    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error("Incorrect number of arguments.")
    if options.remote is None:
        parser.error("Remote address required (-r).")

    g_verbose = options.verbose
    server_host, server_port = get_host_port(args[0], SSH_PORT)
    remote_host, remote_port = get_host_port(options.remote, SSH_PORT)
    return options, (server_host, server_port), (remote_host, remote_port)

# Function to create reverse ssh tunnel available to import into other scripts
def main_func(user, server, keyfile, remote="localhost:22", port=4000):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())

    verbose(f"Connecting to ssh host {server}:22 ...")
    try:
        client.connect(
            hostname=server,
            username=user,
            key_filename=keyfile,
            look_for_keys=False
        )
    except Exception as e:
        print(f"*** Failed to connect to {server}:22: {e}")
        sys.exit(1)

    verbose(
        f"Now attempting to forward remote port {port} to {remote} ..."
    )

    [remote_host, remote_port] = remote.split(":")

    try:
        reverse_forward_tunnel(
            remote_host, int(remote_port), client.get_transport(), server_port=port
        )
    except KeyboardInterrupt:
        print("C-c: Port forwarding stopped.")
        sys.exit(0)

# Function to create reverse ssh tunnel with several options when this script is run from command line
def main_cmd():
    options, server, remote = parse_options()
    print(server[0])
    password = None
    if options.readpass:
        password = getpass.getpass("Enter SSH password: ")

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())

    verbose("Connecting to ssh host %s:%d ..." % (server[0], server[1]))
    try:
        client.connect(
            hostname=server[0],
            username=options.user,
            key_filename=options.keyfile,
            look_for_keys=options.look_for_keys,
            password=password,
        )
    except Exception as e:
        print("*** Failed to connect to %s:%d: %r" % (server[0], server[1], e))
        sys.exit(1)

    verbose(
        "Now forwarding remote port %d to %s:%d ..."
        % (options.port, remote[0], remote[1])
    )

    try:
        reverse_forward_tunnel(
            remote[0], remote[1], client.get_transport(), server_port=options.port
        )
    except KeyboardInterrupt:
        print("C-c: Port forwarding stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main_cmd() #Create ssh reverse tunnel with options passed through the command line
