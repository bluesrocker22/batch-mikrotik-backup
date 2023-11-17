import netmiko
import getpass
import datetime
import os
import time

import logging
logging.basicConfig(filename='test.log', level=logging.DEBUG)
logger = logging.getLogger("netmiko")

from netmiko import ConnectHandler

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

if not os.path.exists(folder_name):
    os.makedirs(folder_name)
    print(f"Folder '{folder_name}' created successfully.")
else:
    print(f"Folder '{folder_name}' already exists.")

username_full = f'{username}+ct'
addr_list = 'addresses_v6.txt'  # Replace with your file path
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
    'global_cmd_verify': True,
    'global_delay_factor': 4,
  #  'global_read_timeout': 800,
  #  'conn_timeout': 1000,
  #  'session_timeout': 1000,
    'fast_cli': False,
    'username': username_full,
    "password": passwd, # Log in password from getpass
    "secret": passwd # Enable password from getpass
  }
  device_list.append(device)
for each_device in device_list:
  sshCli = ConnectHandler(**each_device)
  getname = sshCli.send_command("/system identity print", read_timeout=500.0)
  search_phrase = 'name: '
  mktname = getname.split(search_phrase, 1)[-1]  # Split the string by 'name: ' and get the part after it
  print(mktname)
  exportcommand = "/export"
  exportconfig = sshCli.send_command(exportcommand, read_timeout=500.0)
  time.sleep(5)
  print(exportconfig),
  current_time = datetime.datetime.now()
  timestamp = current_time.strftime("%Y-%m-%d_%H-%M-%S")
  file_name = f"{mktname}_{timestamp}.rsc"
  backup_path = os.path.join(folder_name, file_name)
  with open(backup_path, 'w') as file:
    file.write(exportconfig)
    file.close()
  sshCli.disconnect()
