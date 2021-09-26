import subprocess
from threading import Thread


def connect(user, host):
    subprocess.run(f"ssh -R 43022:localhost:22 -i ../open-key-pair.pem {user}@{host}")


if __name__ == "__main__":
    host = "54.167.166.244"
    user = "ec2-user"
    connect(user, host)