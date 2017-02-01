import boto3
import paramiko

from VMInteractionThread import VMInteractionThread

import os
import time
import errno
import datetime
import logging

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s.%(msecs)-3d] %(levelname)-8s '
                    '(%(threadName)-22s) %(message)s',
                    datefmt='%X')

ec2 = boto3.resource('ec2')


class AWSInteractionThread(VMInteractionThread):

    def __init__(self, name, size, mem, iteration):
        VMInteractionThread.__init__(self, name, size, mem, iteration)
        self.instance = None

    def run(self):
        logging.info('started')
        self.instance = create_virtual_machine(self.size)[0]
        logging.info('vm created - waiting')
        while self.instance.state['Code'] != 16:
            self.instance.load()
            time.sleep(LAUNCH_DELAY)
        try:
            logging.info('running benchmark')
            start_benchmark(self.instance.public_dns_name, AWS_USERNAME,
                            self.size, self.mem, self.iteration)
            logging.info('run complete')
            self.complete = True
        except Exception as e:
            logging.error(str(e))
        finally:
            delete_virtual_machine(self.instance)
        logging.info('finished')
        clear_thread(self.size, self.iteration)


def create_virtual_machine(size):
    image_id = 'ami-8b68e0f8'
    result = ec2.create_instances(ImageId=image_id,
                                  InstanceType=size,
                                  MinCount=1,
                                  MaxCount=1,
                                  KeyName='spot-key',
                                  SecurityGroups=['launch-wizard-2'])
    return result


def start_benchmark(hostname, username, size, mem, iteration=1,
                    single_threaded=False):
    if single_threaded:
        cmd = ('cd specjvm2008; '
               'java -Xmx{}g -jar SPECjvm2008.jar '
               '-Dspecjvm.benchmark.threads=1 all').format(mem)
    else:
        cmd = ('cd specjvm2008; '
               'java -Xmx{}g -jar SPECjvm2008.jar').format(mem)
        # cmd = ('cd specjvm2008; '
        #    'java -jar SPECjvm2008.jar '
        #    '-wt 5s -it 5s -bt 2 compress')
    pkey = paramiko.RSAKey.from_private_key_file('../spot-key.pem')
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy())
    ssh_client.connect(hostname=hostname, username=username, pkey=pkey)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(cmd)

    path = 'results/{}/result_{}.txt'.format(size.lower(), iteration)
    try:
        os.makedirs(os.path.dirname(path))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            logging.error('Error occurred in result writing, no results saved')
            return

    # blocks until the command has finished executing
    status = ssh_stdout.channel.recv_exit_status()
    # ssh_stdout.readlines()
    scp_client = ssh_client.open_sftp()
    scp_client.get('specjvm2008/results/SPECjvm2008.{0:0>3}/SPECjvm2008'
                   '.{0:0>3}.txt'.format(iteration), path)
    scp_client.get('specjvm2008/results/SPECjvm2008.{0:0>3}/SPECjvm2008'
                   '.{0:0>3}.raw'.format(iteration), path)
    # TODO: Find out Why this is here twice..
    scp_client.close()
    ssh_client.close()


def delete_virtual_machine(instance):
    ids = [instance.id]
    ec2.instances.filter(InstanceIds=ids).stop()
    ec2.instances.filter(InstanceIds=ids).terminate()


def clear_thread(size, iteration):
    with dict_lock:
        key = '{}-{}'.format(size, iteration)
        virtual_machines.pop(key)
