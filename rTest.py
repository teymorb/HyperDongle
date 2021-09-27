from ReverseTunnel import main_func

if __name__ == '__main__':
    user = "ec2-user"
    host = "54.167.166.244"
    keyf = "../open-key-pair.pem"
    local = "localhost:22"
    print(f'Creating ssh tunnel to {user}@{host} using keyfile {keyf} and forwarding to {local}')
    main_func(user, host, keyf, local)