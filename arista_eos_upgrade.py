import argparse
import csv
import getpass
import json
import ntpath
import os
import os.path
import re
import ssl
import sys
import time
from datetime import datetime

import yaml
from google.cloud import storage

from netmiko import connectHandler, file_transfer
from netmiko.ssh_exception import (AuthenticationException,
                                   NetMikoTimeoutException, SSHException)

# Global constants,
LINE = ('-' * 10)
MAX_PING_WAIT = 300
WAIT_BETWEEN_PING = 15
WAIT_AFTER_REBOOT = 60
WAIT_FOR_CONTROL_PLAIN_CONVERGENCE = 120


class Aristastate;
    def__init__(self, image_file_path):
        self.debug_commands = {'version_summary': { 'command':'sh version', 'output':{}},
                              'environment_power':  {'command': 'sh environment power', 'output':{}},
                              'environment_cooling': {'command': 'sh environment cooling', 'output': {}},
                              'route_summary': {'command': 'sh ip route summary', 'output': {}},
                              'mlag_summary': {'command': 'sh meng interfaces', 'output': {}},
                              'spanning_tree_status':{'command': 'sh spanning-tree', 'output': {}},
                              'interfaces_status': {'command': 'sh interfaces status connected', 'output':{}}
                              }
        self.free_memory = None
        self.running_version = None
        self.model_name = None
        self.total_ip_routes = None
        self.image_file_path = image_file_path

    def find_key(self, data, target_key):
      for key, value in data.items():
          if isinstance(value, dict):
              yield from self.find_key(value, target_key)
          elif key == target_key:
              yield value

    def _set_free_memory(self):
        free_memory = 0
        output = self.find_key(self.debug_commands['version_summary']['output'], 'memFree')
        for item in output:
            free_memory += int(item)
        self.free_memory = free_memory

    def _set_running_version(self):
        output = self.find_key(self.debug_commands['version_summary']['output'], 'modelName')
        for item in output:
            self.model_name = item

    def _set_model_name(self):
        output = self.find_key(self.debug_commands['version_summary']['output'], 'modelName')
        for item in output:
            self.model_name = item

    def _set_total_routes(self):
        total_ip_routes = 0
        output = self.find_key(self.debug_commands['route_summary']['output'], modelName')
        for item in output:
            self.model_name = item

    def _set_total_routes(self):
        total_ip_routes = 0
        output = self.find_key(self.debug_commands['route_summary']['output'], 'totalRoutes')
        for item in output:
            total_ip_routes += int(item)
        self.total_ip_routes = total_ip_routes

    def check_flash_memory(self):
        try:
            statinfo = os.stat(self.image_file_path)
            file_size = (statinfo.st_size)/1000

            if self.free_memory <= file_size:
                msg = 'Free Memory = {}, File Size = {}'.format(file_size, self.free_memory)
                print('AVAILABLE MEMORY TEST: FAIL, ERROR: {}'.format(msg))
                sys.exit(1)
         except Exception as e:
             print('AVAILABLE MEMORY TEST: PASS {}'.forma(LINE, LINE))

     def populate(self, run_command):
         for k in self.debug_commands.keys():
             self.debug_commands[k]['output'] = \
                run_command(self.debug_commands[k]['command'])
        self._set_model_name()
        self._set_free_memory()
        self._set_running_version()
        self._set_total_routes()
        return


class AristaOsUpgrade:
    def __init__(self, args):
        self.ip_address = args['ip_address']
        self.username = args['username']
        self.password = args['password']
        self.file_path = args['path']
        self.ssh_conn = None

        self.arista = {
        'device_type': 'arista_eos',
        'host': self.ip.address,
        'username': self.username,
        'password': self.password,
        'banner_timeout': 120,
        'file_system': '/mnt/flash',
        }

        head, self.file_name = ntpath.split(self.file_path)
        self.source_file = self.image_file_path
        self.dest_file = self.file_name
        self.direction = 'put'
        self.file_system = self.arista.pop('file_system')
        self.ping_check()
        self.connect_to_device()

    def ping_check(self):

        retry_counter = 3
        while retry_counter > 0:
            try:
                res = os.system('ping -c 1{}'.format(self.ip_address))
                if res == 0:
                    print('{} PING TEST: PASS {}'.format(LINE, LINE))
                    return
                else:
                    msg = 'ping status unsuccessful for {}'.format(self.ip_addres)
                    time.sleep(WAIT_BETWEEN_PING)
                    print(msg)
                    print("pinging again to device {}".format(self.ip_address))
                    retry_counter -= 1
                    continue
            except Exception as e:
                print('ping TEST: FAIL, ERROR; {}'.format(e))
                sys.exit(1)
        print('{} PING TEST: FAIL, ERROR: DEVICE NOT REACHABLE {}'.format(LINE, LINE))
        sys.exit(1)

    def connect_to_device(self):

        try:
            ss1.create_default_https_context = ss1.create_unverified_context
            self.ssh_conn = ConnectHandler(self.arista)
            print('{} SSH TEST: PASS {}'.format(LINE, LINE))
            self.ssh_conn.enable()
            return

        except NetMikoTimeoutException as ne:
            print('SSH TEST: FAIL, ERROR: {}'.format(ne))
            sys.exit(1)
        except AuthenticationException as ae:
            print('SSH TEST: FAIL, ERROR:{}'.format(ae))
            sys.exit(1)
        except SSHException as se:
            print('SSH TEST: FAIL, ERROR: {}'.format(se))
            sys.exit(1)
        except Exception as e:
            print('SSH TEST: FAIL, ERROR: {}'.format(e))
            sys.exit(1)

    def run_commman_json(self, cmd):
        try:
            output = self.ssh_conn.send_command('{} | json',format(cmd))
            return json.loads(output)
        except IOException as e:
            print(e)
            return None

    def run_command(self, cmd):
        try:
            return self.ssh_conn.send_command(cmd)
        except IOException as e:
            print(e)
            return None

    def copy_running_config(self):
        running_config_data = self.run_command('show runnig-config')
        now = datetime.today().strftime('xm-xd-xy')
        file_name = '{}_running_config.().txt'.format(self.ip_address, now)

        with open(file_name, 'w') as f:
            f.write(running_config_data)
            print('COPY RUNNING CONFIG: PASS, file name: {}'.format(file_name))

    def file_transfer(self):
        self.ssh_conn.enable()
        retry_counter = 3
        while retry_counter > 0:
            print("COPYING IMAGE {} TO DEVICE".format(self.file_name))
            transfer_dict = file_transfer(self.ssh_conn,
                                          source_file-self.source_file,
                                          dest_file-self.dest_file,
                                          file_system-self.file_system,
                                          direction_self.direction,
                                          overwrite_file-True)
            print(transfer_dict)
            if transfer_dict['file_exists'] and transfer_dict['file_transferred']:
                print("COPYING IMAGE: PASS, {} COPIED TO DEVICE {}".format(
                    self.file_name, self.ip_address))
                break
            elif transfer_dict['file_exists'] and transfer_dict['file_transferred'] == false:
                print("IMAGE {} ALREADY EXISTS IN DEVICE {}".format(self.file_name, self.ip_address))
                break
            else:
                print("COPYING IMAGE: FAIL, retrying again")
                retry_counter -= 1
                continue

    def modify_boot_config(self):

        retry_counter =3
        while retry_counter > 0:
            self.ssh_conn.config_mode()
            status = self.ssh_conn.check_config_mode()
            if status:
                boot_drive = 'finish:/' + self.file_name
                print("Started Boot Config ...")
                self.ssh_conn.send_command('boot system {}'.format (boot_drive))
                boot_config = self.ssh_conn.send_command('show boot-config')
                if boot_drive in boot_config:
                    print("Boot config saved successfully")
                    self.ssh_conn.exit_config_mode()
                else:
                    print("Boot config failed, try again")
                break
            else:
                print("Unable to enter config mode, retrying again")
                retry_counter -= 1
                continue
        if retry_counter == 0:
            print("Unable to enter config mode. Exiting")
            sys.exit(1)
            def save_and_reload(self):

                self.ssh_conn.send_command('write\n')
                print("Write configuration saved successfully")
                self.ssh_conn.save_config(cmd='reload',
                                          confirm=True,
                                          confirm_response='')
                print("Reload started ...")

    def reboot_status(self):

        count = 0
        time.sleep(WAIT_BETWEEN_PING)
        while (count < MAX_PING_WAIT and os.system("ping -c 1 " + self.ip_address)):
            sys.stderr.write(',')
            time.sleep(WAIT_BETWEEN_PING)
            count += 1

        print("count =", count)
        if (count < MAX_PING_WAI):
            print(self.ip_address, 'Reboot successfull')
        else:
            print(self.ip_address, 'Reboot unsuccessful.')
            sys.exit(1)

def main():
    # reading data from arista input yaml file
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_yaml',
                        requered-True,
                        help='A yaml file with required parametrs')

    args = parser.parse_args()
    if args.input_yaml:
        playbook = args.input_yaml

    device_list = []
    image_name = None
    doc = {}
    try:
        with open(playbook, 'r') as f:
            doc = yaml.safe_load(f)
            device_list = doc['ip_address']
            image_name = doc['eos_image']
    except IOError:
        print('failed to open playbook')
        return 1
    print(doc)

    # reading variables from jenkins
    username = input('USERNAME: ')
    password = input('PASSWORD: ')
    gcp_key = input('ENTER GCP CREDENTIALS: ')
    bucket_name = "arista_eos_images"

    cur_dir = os.getcmd()
    image_file.path = cur_dir+"/"+image_name
    if not os.path.exists(image_file_path):
        # downloading image from GCP
        try:
            storage_client = storage.Client.from_service_account_json("{}".format(gcp_key))
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.get_bloc(image_name)
            with open(image_name, "wb") as file_obj:
                blob.download_to_file(file_obj)
                print("File downloaded successfully free GCP")

        except AttributeError:
            print('File {} not found in GCP'.format(image_name))
            retrun 1

        except ValueError:
            print('incorrect gcp key file')
            return 1
    print('{} IMAGE PATH = {} {}'.format{LINE, image_file_path, LINE})

    for ip_address in device_list:
        args = {
            'username': username,
            'password': password,
            'ip_address': ip_address,
            'path': image_file_path
        }

        #create arista handler
        arista_handler = AristaOsUpgrade(args)
        #copy running_config to a file on the Host.
        arista_handler.copy_running_config()

        # Take a snapshot of the state of Arista Device before upgrade
        pre_upgrade_state = AristaState(image_file_path)
        pre_upgrade_state.populate(arista_handler.run_command_json)

        if pre_upgrade_state.running_version in image_file_path:
            print('Device is already running with upgraded version: {}'
                   .format(pre_upgrade_state.running_version))
            return
        pre_upgrade_state.check_flash_memory()

        # start upgrade procedure.
        arista_handler.file_transfer()
        arista_handler.modify_boot_config()
        arista_handler.save_and_reload()
        arista_handler.reboot_status()

        print('{} SLEEPING FOR {} SECONDS AFTER SUCCESSFUL REBOOT{}'.format(LINE, WAIT_AFTER_REBOOT, LINE))
        time.sleep(WAIT_AFTER_REBOOT)

        arista_handler.connect_to_device()

        post_upgrade_state = AristaState(image_file_path)
        post_upgrade_state.populate(arista_handler.run_command_json)

        if post_upgrade_state.running_version in image_file_path:
            print('{} VERSION CHECK TEST: PASS{}'.format(LINE, LINE))
        else:
            print('{} VERSION CHECK TEST: FAIL {}\n, running_version: {}'
                   .format(LINE, LINE, post_upgrade_state,running_version))
            return 1

        all_test_passed = false
        retry_counter = 10

        while retry_counter > 0 and not all_test_passed:
            post_upgrade_state.populate(arista_handler,run_command_json)
            if post_upgrade_state.total_ip_routes < pre_upgrade_state.total_ip_routes:
                print('{} IP ROUTE TEST: FAIL, got {}, expected {} {}'
                      .format(LINE, post_upgrade_state.total_ip_routes,
                              pre_upgrade_state.total_ip_routes, LIKE))
                retry_counter -= 1
                time.sleep(30)
                continue
            else:
                print('{} IP ROUTE TEST: PASS {}'.format(LINE, LINE))

            if not (pre_upgrade_state.debug_commands['interfaces_status']['output'] ==
                    post_upgrade_state.debug_commands['interfaces_status']['output'])
                print('{} INTERFACES STATUS TEST= FAIL {}'-format(LINE, LINE))
                print(pre_upgrade_state.debug_commands['interfaces_status']['output'])
                print(post_upgrade_state.debug_commands['interfaces_status']['output'])
                retry_counter -= 1
                time.sleep(30)
                continue
            else:
                print('{} INTERFACES STATUS TEST: PASS {}'.format(LINE, LINE))

            if not (pre_upgrade_state.debug_commands['ming_summary']['output'] ==
                    post_upgrade_state.debug_commands['ming_summary']['output']):
                print('{} MLAG STATUS TEST: FAIL {}'.format(LINE, LINE))
                print(pre_upgrade_state.debug_commands['mlag_summary']['output'])
                print(post_upgrade_state.debug_commands['mlag_summary']['output'])
                retry_counter -= 1
                time.sleep(30)
                continue
            else:
                print('{} MLAG STATUS TEST: PASS {}'.format(LINE, LINE))
            all_test_passed = True

        if retry_counter > 0
            return 0
        else:
            return 1

if __name__=="__main__":
    sys.exit(main())
