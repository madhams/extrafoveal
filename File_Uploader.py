import paramiko
from scp import SCPClient
import time

def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

# Need to read file to check if it has changed and then upload file with scp
start_time = time.time()
server = 'raspberrypi.local'
server = '168.5.172.140'
port = 22
user = 'foveal'
password = 'extrafoveal'
ssh = createSSHClient(server, port, user, password)
scp = SCPClient(ssh.get_transport())
scp.put('test.txt', '/home/foveal/Senior_Design/Compass/test.txt')
end_time = time.time()
print(end_time-start_time)
