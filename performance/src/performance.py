from azure import *
from azure.servicemanagement import *

import threading
import time
import re
import os
import errno
import datetime

import paramiko

LOCATION = 'East US'
NAME = 'cloudbm'
USERNAME = 'azureuser'
LAUNCH_DELAY = 180
RETRY_DELAY = 300
ITERATION_COUNT = 5
ATTEMPT_LIMIT = 1000

FREE_SLOTS = 15

# VM_SIZES = [#'Basic_A3', 'Basic_A4']
#             'Standard_D1', 'Standard_D2',
#             'Standard_D3', 'Standard_D4',
#             'Standard_D11', 'Standard_D12', 'Standard_D13', 'Standard_D14']

VM_SIZES = {#'Basic_A3': 2,
            # 'Basic_A4': 4,
            'Standard_D1_v2': 1,
            # 'Standard_D2_v2': 1,
            # 'Standard_D3_v2': 4,
            # 'Standard_D4': 8,
            # 'Standard_D11_v2': 2,
            # 'Standard_D12_v2': 8,
            # 'Standard_D13': 8,
            # 'Standard_D14': 16
            }

VM_ITERATIONS = {
                # 'Basic_A4': 1,
                'Standard_D1_v2': 1,
                # 'Standard_D2_v2': 5,
                # 'Standard_D3_v2': 5,
                #  'Standard_D4': 5,
                # 'Standard_D11_v2': 5,
                # 'Standard_D12_v2': 5,
                #  'Standard_D13': 1,
                #  'Standard_D14': 5
                 }

subscription_id = '1e40465f-9230-44d1-a955-e69d2f7fe9f8'
certificate_path = os.path.normpath('/Users/Adam/root/stage4/cloud_computing/azure.pem')

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
    hosted_service_name = 'cloudbenchvm'
    deployment_name = 'cloudbenchvm'
    vm_name = 'cloudbenchvm'

    image_name = vm_name + 'image'
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

class VMInteractionThread(threading.Thread):
    def __init__(self, name, location, size, mem, iteration):
        threading.Thread.__init__(self)
        self.name = name
        self.location = location
        self.size = size
        self.mem = mem
        self.iteration = iteration
        self.hostname = '{}.cloudapp.net'.format(name)
        self.complete = False

    def tPrint(self, string):
        print('{}: Thread azure.{}: {}'.format(datetime.datetime.time(datetime.datetime.now()),self.name, string))

    def run(self):
        self.tPrint('started')
        attempt = 0
        while not self.complete and attempt < ATTEMPT_LIMIT:
            create_virtual_machine(self.name, self.location, self.size, self.iteration)
            self.tPrint('vm created - waiting')
            time.sleep(LAUNCH_DELAY)
            try:
                self.tPrint('running benchmark')
                results = start_benchmark(self.hostname, self.size, self.mem, self.iteration)
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
    # full_name ='{}{}-{}'.format(name, size.lower().replace('_',''), iteration)

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
    # image_name = 'specvm'
    image_name = 'cloudbenchvmimage'
    # media_location = 'https://cloudbench.blob.core.windows.net/vhds'

    # Destination storage account container/blob where the VM disk will be created
    # media_link = 'https://07portalvhdsq3zhkfyqx6x2.blob.core.windows.net/vhds/%s.vhd' % name
    # os_hd = OSVirtualHardDisk(image_name, media_link)

    # Linux VM configuration, you can use WindowsConfigurationSet
    # for a Windows VM instead
    # linux_config = LinuxConfigurationSet(name, 'azureuser', 'y7Z38xJ3', False)

    endpoint_config = ConfigurationSet()
    endpoint_config.configuration_set_type = 'NetworkConfiguration'
    # endpoint1 = azure.servicemanagement.ConfigurationSetInputEndpoint(name='HTTP', protocol='tcp', port='80', local_port='80', load_balanced_endpoint_set_name=None, enable_direct_server_return=False)
    endpoint2 = ConfigurationSetInputEndpoint(name='SSH', protocol='tcp', port='22', local_port='22', load_balanced_endpoint_set_name=None, enable_direct_server_return=False)

    # endpoint_config.input_endpoints.input_endpoints.append(endpoint1)
    endpoint_config.input_endpoints.input_endpoints.append(endpoint2)

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

        # print(result)
        # print(result.request_id)

    except Exception as e:
        print('AZURE ERROR: %s' % str(e))

def start_benchmark(hostname, size, mem, iteration):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy())
    ssh_client.connect(hostname=hostname, username=USERNAME)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command('cd specjvm2008; java -Xmx{}g -jar SPECjvm2008.jar'.format(mem))
    # ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command('cd specjvm2008; java -jar SPECjvm2008.jar -wt 5s -it 5s -bt 2 compress')
    path = 'results/{}/result_{}.txt'.format(size.lower(), iteration)
    try:
        os.makedirs(os.path.dirname(path))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            print('Error occurred in result writing, no results saved')
            return
    # blocks until the command has finished executing
    status = ssh_stdout.channel.recv_exit_status()

    for line in iter(lambda: stdout.readline(2048), ""):
        print(line, end="")
    # ssh_stdout.readlines()
    sftp_client = ssh_client.open_sftp()
    sftp_client.get('specjvm2008/results/SPECjvm2008.001/SPECjvm2008.001.txt', path)
    sftp_client.close()
    ssh_client.close()

    # output = ''
    # for line in ssh_stdout.readlines():
    #     output += line
    # score_pattern = re.compile('Score on ([a-z]+): (.+)\n')
    # overall_pattern = re.compile('composite result: (.+)\n', flags=re.IGNORECASE)
    # results = dict(score_pattern.findall(output))
    # overall = overall_pattern.search(output)
    # if overall:
    #     results['overall'] = overall.group(1)
    # return results

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
                    virtual_machines[key] = VMInteractionThread('{}-{}'.format(size.lower().replace('_', ''), i+1), LOCATION, size, VM_SIZES[size], i+1)
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
