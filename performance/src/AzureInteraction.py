from azure import *
from azure.servicemanagement import *

from VMInteractionThread import VMInteractionThread

import time
import re
import os
import errno
import datetime
from urllib.parse import urlparse
import logging

import paramiko

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s.%(msecs)-3d] %(levelname)-8s '
                    '(%(threadName)-22s) %(message)s',
                    datefmt='%X')

DEBUG_LEVEL = 0

LOCATION = 'East US'

USERNAME = 'azureuser'
LAUNCH_DELAY = 180
RETRY_DELAY = 300
MULTI_TEST_DELAY = 600
MULTI_TEST_COUNT = 6

ATTEMPT_LIMIT = 1000

subscription_id = '15c807f8-f7cd-43fc-af62-9b7d0395ce6b'
certificate_path = os.path.normpath('../azure.pem')

sms = ServiceManagementService(subscription_id, certificate_path)


class AzureInteractionThread(VMInteractionThread):

    def __init__(self, name, size, mem, iteration):
        VMInteractionThread.__init__(self, name, size, mem, iteration)
        self.vm_name = name.split('.')[1].lower().replace('_', '')
        self.location = LOCATION
        self.deployment = None

    def run(self):
        # self.tPrint('started')
        logging.info('started')
        attempt = 0
        while not self.complete and attempt < ATTEMPT_LIMIT:
            create_virtual_machine(self.vm_name, self.location,
                                   self.size, self.iteration)
            self.deployment = sms.get_deployment_by_name(self.vm_name,
                                                         self.vm_name)
            # self.tPrint('vm created - waiting')
            logging.info('vm created - waiting')
            while self.deployment.status != 'Running':
                time.sleep(LAUNCH_DELAY)
                self.deployment = sms.get_deployment_by_name(self.vm_name,
                                                             self.vm_name)
            try:
                # self.tPrint('running benchmark')
                logging.info('running benchmark')
                results = start_benchmark(urlparse(self.deployment.url).netloc,
                                          self.size, self.mem, self.iteration,
                                          single_threaded=False,
                                          multiple_run=False)
                # self.tPrint('run complete')
                logging.info('run complete')
                self.complete = True
            except Exception as e:
                logging.error(str(e))
            finally:
                attempt += 1
                if self.complete or attempt == ATTEMPT_LIMIT:
                    delete_virtual_machine(self.vm_name)
                    # self.tPrint('vm deleted')
                    logging.info('vm deleted')
                else:
                    time.sleep(RETRY_DELAY)
        if attempt == ATTEMPT_LIMIT:
            # self.tPrint('exiting after {} attempts'.format(ATTEMPT_LIMIT))
            logging.info('exiting after {} attempts'.format(ATTEMPT_LIMIT))
        # self.tPrint('finished')
        logging.info('finished')
        clear_thread(self.size, self.iteration)


def create_virtual_machine(name, location, size, iteration):
    result = sms.list_hosted_services()
    exists = False
    for hosted_service in result:
        if hosted_service.service_name == name \
                and hosted_service.hosted_service_properties.location == \
                location:
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
    endpoint1 = ConfigurationSetInputEndpoint(
        name='SSH', protocol='tcp',
        port='22', local_port='22',
        load_balanced_endpoint_set_name=None,
        enable_direct_server_return=False)

    endpoint_config.input_endpoints.input_endpoints.append(endpoint1)

    try:
        result = sms.create_virtual_machine_deployment(
            service_name=name,
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
        logging.error('AZURE ERROR: %s' % str(e))


def start_benchmark(hostname, size, mem, iteration,
                    single_threaded=False, multiple_run=False):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy())
    ssh_client.connect(hostname=hostname, username=USERNAME)
    # ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(cmd)
    if not multiple_run:
        if single_threaded:
            cmd = ('cd specjvm2008; '
                   'java -Xmx{}g -jar SPECjvm2008.jar '
                   '-Dspecjvm.benchmark.threads=1 all').format(mem)
        else:
            # cmd = 'cd specjvm2008; \
            # java -Xmx{}g -jar SPECjvm2008.jar'.format(mem)
            cmd = ('cd specjvm2008; '
                   'java -jar SPECjvm2008.jar '
                   '-wt 5s -it 5s -bt 2 compress')
        path = 'results/{}/result_{}'.format(size.lower(), iteration)
        execute_benchmark(ssh_client, cmd, path)
    else:
        cmd = 'cd specjvm2008; java -Xmx{}g -jar SPECjvm2008.jar'.format(mem)
        path = 'results/{}/result_{}'.format(size.lower(), iteration)
        execute_multiple(ssh_client, cmd, path)
    ssh_client.close()


def execute_multiple(ssh_client, cmd, path):
    cmd = '{} compress'.format(cmd)
    for i in range(1, MULTI_TEST_COUNT+1):
        if i != 1:
            time.sleep(MULTI_TEST_DELAY)
        current_path = '{}/{}.txt'.format(path, datetime.datetime.now()
                                          .strftime('%H-%M-%S'))
        status = execute_benchmark(ssh_client, cmd, current_path, i)


def execute_benchmark(ssh_client, cmd, path, iteration=1):
    ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(cmd)

    if DEBUG_LEVEL > 0:
        for line in iter(lambda: ssh_stdout.readline(2048), ""):
            if 'Benchmark:' in line:
                logging.debug(line, end="")
    # blocks until the command has finished executing
    status = ssh_stdout.channel.recv_exit_status()

    try:
        os.makedirs(os.path.dirname(path))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            logging.error('Error occurred in result writing, no results saved')
            return

    sftp_client = ssh_client.open_sftp()
    sftp_client.get('specjvm2008/results/SPECjvm2008.{0:0>3}/SPECjvm2008'
                    '.{0:0>3}.txt'.format(iteration), '{}.txt'.format(path))
    sftp_client.get('specjvm2008/results/SPECjvm2008.{0:0>3}/SPECjvm2008'
                    '.{0:0>3}.raw'.format(iteration), '{}.raw'.format(path))
    sftp_client.close()

    return status


def write_results(size, iteration, results):
    path = 'results/{}/result_{}.txt'.format(size.lower(), iteration)
    try:
        os.makedirs(os.path.dirname(path))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            logging.error('Error occurred in result writing, no results saved')
            return
    f = open(path, 'w')
    for test in results.keys():
        f.write('{}: {}\n'.format(test, results[test]))
    f.close()


def delete_virtual_machine(name):
    sms.delete_hosted_service(service_name=name, complete=True)


def clear_thread(size, iteration):
    with dict_lock:
        key = '{}-{}'.format(size, iteration)
        virtual_machines.pop(key)
