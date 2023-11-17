import netmiko
import getpass
import datetime
import os
import termcolor

from netmiko import ConnectHandler
from termcolor import colored

#print colored('hello', 'red'), colored('world', 'green')

addr_list = 'addresses.txt'  # Replace with your file path

while True:
  username = input('Please enter the username: ')
  if not username:
    print('You need to print username to login')
  else:
    break
passwd = getpass.getpass('Please enter the password: ')
folder_name = input('Please enter the folder name (or press Enter to use "backups" folder): ')
if not folder_name:
  folder_name = 'backups'

# process is starting here
if not os.path.exists(folder_name):
    os.makedirs(folder_name)
    print(f"Folder '{folder_name}' created successfully.")
else:
    print(f"Folder '{folder_name}' already exists.")

result_list = []

with open(addr_list, 'r') as file:
    # Read the entire content of the file
    content = file.read()
    # Split the content based on commas and/or newline characters
    my_devices = [item.strip() for item in content.replace('\n', ',').split(',') if item.strip()]

device_list = list() #create an empty list to use it later

for device_ip in my_devices:
  device = {
    'device_type': 'mikrotik_routeros',
    'host': device_ip,
    'port': '22',
    'username': f'{username}+ct',
    'password': passwd, # Log in password from getpass
    'secret': passwd, # Enable password from getpass
    'global_cmd_verify': True,
    'fast_cli': False,
    'global_delay_factor': 4,
  }
  device_list.append(device)
for each_device in device_list:
  sshCli = ConnectHandler(**each_device)
  mktname = colored(sshCli.send_command("/system identity print").split('name: ', 1)[-1], 'magenta')  # Split the string by 'name: ' and get the part after it
  print (mktname)
  routerinfo = sshCli.send_command('/system resource print').split('\n')
  pattern = 'version: '
  for line in routerinfo:
    if pattern in line:
      version = line.split(pattern, 1)[-1]
      break
  if version[0] == '7':
    exportcommand = '/export show-sensitive'
  else:
    exportcommand = '/export'

  print('Command will be used for ROS',version,':')
  colored_export_command = colored(exportcommand, 'green')
  print(colored_export_command)

  exportconfig = sshCli.send_command(exportcommand)
  current_time = datetime.datetime.now()
  timestamp = current_time.strftime("%Y-%m-%d_%H-%M-%S")
  file_name = f"{mktname}_{timestamp}.rsc"
  backup_path = os.path.join(folder_name, file_name)
  with open(backup_path, 'w') as file:
    file.write(exportconfig)
    file.close()
  sshCli.disconnect()
