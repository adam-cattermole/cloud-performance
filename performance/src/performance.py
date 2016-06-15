from azure import *
from azure.servicemanagement import *

from VMInteractionThread import VMInteractionThread
import threading
import time
import re
import os
import errno
import datetime

import paramiko

DEBUG_LEVEL = 0

LOCATION = 'East US'
NAME = 'cloudbm'
USERNAME = 'azureuser'
LAUNCH_DELAY = 180
RETRY_DELAY = 300
MULTI_TEST_DELAY = 600
MULTI_TEST_COUNT = 6
ITERATION_COUNT = 5

ATTEMPT_LIMIT = 1000

FREE_SLOTS = 15

# VM_SIZES = [#'Basic_A3', 'Basic_A4']
#             'Standard_D1', 'Standard_D2',
#             'Standard_D3', 'Standard_D4',
#             'Standard_D11', 'Standard_D12', 'Standard_D13', 'Standard_D14']

VM_SIZES = {#'Basic_A3': 2,
            # 'Basic_A4': 4,
            'Standard_D1': 1,
            'Standard_D1_v2': 1,
            # 'Standard_D2': 1,
            # 'Standard_D2_v2': 1,
            # 'Standard_D3': 4,
            # 'Standard_D3_v2': 4,

            # still need to run
            # 'Standard_D4': 8,
            # 'Standard_D4_v2': 8,

            # 'Standard_D11_v2': 2,
            # 'Standard_D12_v2': 8,
            # 'Standard_D13_v2': 16,
            # 'Standard_D14': 16
            }

VM_ITERATIONS = {
                # 'Basic_A4': 1,
                'Standard_D1': 5,
                'Standard_D1_v2': 5,
                # 'Standard_D2': 5,
                # 'Standard_D2_v2': 5,
                # 'Standard_D3': 5,
                # 'Standard_D3_v2': 5,

                # still need to run
                #  'Standard_D4': 3,
                #  'Standard_D4_v2': 3,

                #  'Standard_D11_v2': 1,
                #  'Standard_D12_v2': 1,
                #  'Standard_D13_v2': 5,
                #  'Standard_D14': 5
                 }

# subscription_id = '1e40465f-9230-44d1-a955-e69d2f7fe9f8'

subscription_id = '15c807f8-f7cd-43fc-af62-9b7d0395ce6b'
certificate_path = os.path.normpath('../azure.pem')

sms = ServiceManagementService(subscription_id, certificate_path)

dict_lock = threading.Lock()
virtual_machines = {}

def output_locations():
    result = sms.list_locations()
    for location in result:
        print(location.name)
    print('')

def output_services():
    result = sms.list_hosted_services()

    for hosted_service in result:
        print('Service name: ' + hosted_service.service_name)
        print('Management URL: ' + hosted_service.url)
        print('Location: ' + hosted_service.hosted_service_properties.location)
        print('')

def output_operating_systems():
    result = sms.list_operating_system_families()

    for family in result:
        print('Family: ' + family.label)
        for os in family.operating_systems:
            if os.is_active:
                print('OS: ' + os.label)
                print('Version: ' + os.version)
        print('')

def output_operating_system_images():
    result = sms.list_os_images()

    for image in result:
        if image.os == 'Linux' and 'specvm' in image.name:
            print('Name: ' + image.name)
            print('Label: ' + image.label)
            print('OS: ' + image.os)
            print('Category: ' + image.category)
            print('Description: ' + image.description)
            print('Location: ' + image.location)
            print('Media link: ' + image.media_link)
            print('')

def output_virtual_machine_images():
    result = sms.list_vm_images()

    for image in result:
        print('Name: ' + image.name)
        print('Label: ' + image.label)
        print('Category: ' + image.category)
        print('Location: ' + image.location)
        print('')

def output_role_sizes():
    result = sms.list_role_sizes()

    for role in result:
        print('Name: {}'.format(role.name))
        print('Label: {}'.format(role.label))
        print('Cores: {}'.format(role.cores))
        print('Memory: {}'.format(role.memory_in_mb))
        print('')

def capture_vm_image():
    # replace the below three parameters with actual values
    hosted_service_name = 'benchmarkvm8734'
    deployment_name = 'benchmarkvm8734'
    vm_name = 'benchmarkvm'

    image_name = 'cloudbenchvmimage'
    image = CaptureRoleAsVMImage('Specialized',
        image_name,
        image_name + 'label',
        image_name + 'description',
        'english')

    result = sms.capture_vm_image(
        hosted_service_name,
        deployment_name,
        vm_name,
        image)

def num_hosted_services():
    result = sms.list_hosted_services()
    return len(result)

class AzureInteractionThread(VMInteractionThread):
    def __init__(self, name, location, size, mem, iteration):
        VMInteractionThread.__init__(self, name, size, mem, iteration)
        self.location = location
        self.hostname = '{}.cloudapp.net'.format(name)

    def run(self):
        self.tPrint('started')
        attempt = 0
        while not self.complete and attempt < ATTEMPT_LIMIT:
            create_virtual_machine(self.name, self.location, self.size, self.iteration)
            self.tPrint('vm created - waiting')
            time.sleep(LAUNCH_DELAY)
            try:
                self.tPrint('running benchmark')
                results = start_benchmark(self.hostname, self.size, self.mem, self.iteration, single_threaded=False, multiple_run=False)
                self.tPrint('run complete')
                self.complete = True
            except Exception as e:
                self.tPrint(str(e))
            finally:
                attempt += 1
                if self.complete or attempt == ATTEMPT_LIMIT:
                    delete_virtual_machine(self.name)
                    self.tPrint('vm deleted')
                else:
                    time.sleep(RETRY_DELAY)
        if attempt == ATTEMPT_LIMIT:
            self.tPrint('exiting after {} attempts'.format(ATTEMPT_LIMIT))
        self.tPrint('finished')
        clear_thread(self.size, self.iteration)


def create_virtual_machine(name, location, size, iteration):
    result = sms.list_hosted_services()
    exists = False
    for hosted_service in result:
        if hosted_service.service_name == name \
            and hosted_service.hosted_service_properties.location == location:
            exists = True

    if not exists:
        # We don't have service created
        sms.create_hosted_service(service_name=name,
            label=name,
            location=location)

    # Name of an os image as returned by list_os_images
    image_name = 'cloudbenchvmimage'

    endpoint_config = ConfigurationSet()
    endpoint_config.configuration_set_type = 'NetworkConfiguration'
    endpoint1 = ConfigurationSetInputEndpoint(name='SSH', protocol='tcp', port='22', local_port='22', load_balanced_endpoint_set_name=None, enable_direct_server_return=False)

    endpoint_config.input_endpoints.input_endpoints.append(endpoint1)

    try:
        result = sms.create_virtual_machine_deployment(service_name=name,
            deployment_name=name,
            deployment_slot='production',
            label=name,
            role_name=name,
            system_config=None,
            network_config=endpoint_config,
            os_virtual_hard_disk=None,
            role_size=size,
            vm_image_name=image_name)

    except Exception as e:
        print('AZURE ERROR: %s' % str(e))

def start_benchmark(hostname, size, mem, iteration, single_threaded=False, multiple_run=False):
    # if single_threaded:
    #     cmd = 'cd specjvm2008; java -Xmx{}g -jar SPECjvm2008.jar -Dspecjvm.benchmark.threads=1 all'.format(mem)
    # else:
    #     cmd = 'cd specjvm2008; java -Xmx{}g -jar SPECjvm2008.jar'.format(mem)
        # cmd = 'cd specjvm2008; java -jar SPECjvm2008.jar -wt 5s -it 5s -bt 2 compress'
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy())
    ssh_client.connect(hostname=hostname, username=USERNAME)
    # ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(cmd)
    if not multiple_run:
        if single_threaded:
            cmd = 'cd specjvm2008; java -Xmx{}g -jar SPECjvm2008.jar -Dspecjvm.benchmark.threads=1 all'.format(mem)
        else:
            # cmd = 'cd specjvm2008; java -Xmx{}g -jar SPECjvm2008.jar'.format(mem)
            cmd = 'cd specjvm2008; java -jar SPECjvm2008.jar -wt 5s -it 5s -bt 2 compress'
        path = 'results/{}/result_{}.txt'.format(size.lower(), iteration)
        execute_benchmark(ssh_client, cmd, path)
    else:
        cmd = 'cd specjvm2008; java -Xmx{}g -jar SPECjvm2008.jar'.format(mem)
        path = 'results/{}/result_{}'.format(size.lower(), iteration)
        execute_multiple(ssh_client, cmd, path)
    # run_benchmark(ssh_client, path, single_threaded, multiple_run)

    # path = 'results/{}/result_{}.txt'.format(size.lower(), iteration)
    # try:
    #     os.makedirs(os.path.dirname(path))
    # except OSError as exception:
    #     if exception.errno != errno.EEXIST:
    #         print('Error occurred in result writing, no results saved')
    #         return
    #
    # for line in iter(lambda: ssh_stdout.readline(2048), ""):
    #     if 'Benchmark:' in line:
    #         print(line, end="")
    # # blocks until the command has finished executing
    # status = ssh_stdout.channel.recv_exit_status()

    # ssh_stdout.readlines()
    # sftp_client = ssh_client.open_sftp()
    # sftp_client.get('specjvm2008/results/SPECjvm2008.001/SPECjvm2008.001.txt', path)
    # sftp_client.close()
    ssh_client.close()

def execute_multiple(ssh_client, cmd, path):
    cmd = '{} compress'.format(cmd)
    for i in range(1, MULTI_TEST_COUNT+1):
        if i != 1:
            time.sleep(MULTI_TEST_DELAY)
        current_path = '{}/{}.txt'.format(path, datetime.datetime.now().strftime('%H-%M-%S'))
        status = execute_benchmark(ssh_client, cmd, current_path, i)


def execute_benchmark(ssh_client, cmd, path, iteration=1):
    ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(cmd)

    if DEBUG_LEVEL > 0:
        for line in iter(lambda: ssh_stdout.readline(2048), ""):
            if 'Benchmark:' in line:
                print(line, end="")
    # blocks until the command has finished executing
    status = ssh_stdout.channel.recv_exit_status()

    try:
        os.makedirs(os.path.dirname(path))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            print('Error occurred in result writing, no results saved')
            return

    sftp_client = ssh_client.open_sftp()
    sftp_client.get('specjvm2008/results/SPECjvm2008.{0:0>3}/SPECjvm2008.{0:0>3}.txt'.format(iteration), path)
    sftp_client.close()

    return status


def write_results(size, iteration, results):
    path = 'results/{}/result_{}.txt'.format(size.lower(), iteration)
    try:
        os.makedirs(os.path.dirname(path))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            print('Error occurred in result writing, no results saved')
            return
    f = open(path, 'w')
    for test in results.keys():
        f.write('{}: {}\n'.format(test, results[test]))
    f.close()

def delete_virtual_machine(name):
    # full_name ='{}{}-{}'.format(name, size.lower().replace('_',''), iteration)
    sms.delete_hosted_service(service_name=name, complete=True)

def clear_thread(size, iteration):
    with dict_lock:
        key = '{}-{}'.format(size, iteration)
        virtual_machines.pop(key)

def main():
    for size in sorted(VM_SIZES.keys()):
        for i in range(0, VM_ITERATIONS[size]):
            key = '{}-{}'.format(size, i+1)
            success = False
            while not success:
                if len(virtual_machines) < FREE_SLOTS:
                    virtual_machines[key] = AzureInteractionThread('{}-{}'.format(size.lower().replace('_', ''), i+1), LOCATION, size, VM_SIZES[size], i+1)
                    virtual_machines[key].start()
                    success = True
                else:
                    time.sleep(60)

# output_locations()
# output_services()
# print(num_hosted_services())
# output_operating_systems()
# output_operating_system_images()
# output_virtual_machine_images()
# output_role_sizes()
main()

# create_virtual_machine('cloudbench', 'East US', 'Basic_A1', 1)

# create_service('myhostedservice', 'myhostedservice', 'my hosted service', 'East US')
# create_virtual_machine('cloudbench', 'East US', 'Small')
# capture_vm_image()
