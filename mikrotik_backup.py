import getpass
import datetime
import os
import sys

from netmiko import ConnectHandler
from paramiko.proxy import ProxyCommand
from termcolor import colored

addr_list = 'addresses.txt'  # Replace with your file path
folder_main = 'backups' #main folder for backups

def monkey_patch_paramiko():
    """Win support
    Credits: https://github.com/JulianEberius/paramiko/commit/bb1f795db46891961b6a816df3c59e132de7f211"""
    def recv_patched(self, size):
        return os.read(self.process.stdout.fileno(), size)

    if sys.platform == 'win32':
        ProxyCommand.recv = recv_patched


while True:
    username = input('Please enter the username: ')
    if not username:
        print('You need to print username to login')
    else:
        break

passwd = getpass.getpass('Please enter the password: ')
sshport = input('Please enter ssh port for connections or press Enter to use default port (22): ')
folder_name = input('Please enter the folder name (will be created in the backups folder): ') 

if not sshport:
    sshport = '22'

# process is starting here
monkey_patch_paramiko()

if not os.path.exists(os.path.join(folder_main, folder_name)):
    os.makedirs(os.path.join(folder_main, folder_name))
    print(f'Folder "{os.path.join(folder_main, folder_name)}" created successfully.')
else:
    print(f'Folder "{os.path.join(folder_main, folder_name)}" already exists.')

result_list = []

with open(addr_list, 'r') as file:
    # Read the entire content of the file
    content = file.read()
    # Split the content based on commas and/or newline characters
    my_devices = [item.strip() for item in content.replace('\n', ',').split(',') if item.strip()]

device_list = []  # create an empty list to use it later

for device_ip in my_devices:
    device = {
        'device_type': 'mikrotik_routeros',
        'host': device_ip,
        'port': sshport,
        'username': f'{username}+ct',
        'password': passwd,  # Log in password from getpass
        'secret': passwd,  # Enable password from getpass
        'global_cmd_verify': True,
        'fast_cli': False,
        'global_delay_factor': 4,
    }
    device_list.append(device)

for each_device in device_list:
    sshCli = ConnectHandler(**each_device)
    # Split the string by 'name: ' and get the part after it
    mktname = sshCli.send_command('/system identity print').split('name: ', 1)[-1]
    print(colored(mktname, 'magenta'))
    routerinfo = sshCli.send_command('/system resource print').split('\n')
    pattern = 'version: '
    for line in routerinfo:
        if pattern in line:
            version = line.split(pattern, 1)[-1]
            break
    else:
        raise ValueError(f'No version line in "{routerinfo}"')

    if version[0] == '7':
        exportcommand = '/export show-sensitive'
    else:
        exportcommand = '/export'

    print('Command will be used for ROS', version, ':')
    print(colored(exportcommand, 'green'))

    exportconfig = sshCli.send_command(exportcommand)
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime('%Y-%m-%d_%H-%M-%S')
    file_name = f'{mktname}_{timestamp}.rsc'
    backup_path = os.path.join(folder_main, folder_name, file_name)

    with open(backup_path, 'w') as file:
        file.write(exportconfig)
        file.close()
        print(f'File {backup_path} is saved')

    sshCli.disconnect()
