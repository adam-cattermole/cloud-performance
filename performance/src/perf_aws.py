import boto3
import paramiko

from VMInteractionThread import VMInteractionThread

import os
import time
import threading
import errno
import datetime

VM_SIZES = {
            # 't2.micro': 1,
            # 't2.small': 1,
            # 't2.medium': 2,
            # 't2.large': 4,
            # 'm4.large': 4,
            # 'm4.xlarge': 8,
            'm4.2xlarge': 16,
            # 'm4.4xlarge': 32,
            # 'c4.large': 2,
            # 'c4.xlarge': 4,
            'c4.2xlarge': 8,
            # 'c4.4xlarge': 16
            }

VM_ITERATIONS = {
                # 't2.micro': 5,
                # 't2.small': 1,
                # 't2.medium': 3,
                # 't2.large': 4,
                # 'm4.large': 4,
                # 'm4.xlarge': 8,
                'm4.2xlarge': 5,
                # 'm4.4xlarge': 5,
                # 'c4.large': 2,
                # 'c4.xlarge': 1,
                'c4.2xlarge': 5,
                # 'c4.4xlarge': 5
                }
# NUM_ITERATIONS = 5

AWS_USERNAME = 'ubuntu'
LAUNCH_DELAY = 180
FREE_SLOTS = 25

ec2 = boto3.resource('ec2')

dict_lock = threading.Lock()
virtual_machines = {}



class AWSInteractionThread(VMInteractionThread):

    def __init__(self, name, size, mem, iteration):
        VMInteractionThread.__init__(self, name, size, mem, iteration)
        self.instance = None

    def run(self):
        self.tPrint('started')
        self.instance = create_virtual_machine(self.size)[0]
        self.tPrint('vm created - waiting')
        while self.instance.state['Code'] != 16:
            self.instance.load()
            time.sleep(LAUNCH_DELAY)
        try:
            self.tPrint('running benchmark')
            start_benchmark(self.instance.public_dns_name, AWS_USERNAME, self.size, self.mem, self.iteration)
            self.tPrint('run complete')
            self.complete = True
        except Exception as e:
            self.tPrint(str(e))
        finally:
            delete_virtual_machine(self.instance)
        self.tPrint('finished')
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

def start_benchmark(hostname, username, size, mem, iteration, single_threaded=False):
    if single_threaded:
        cmd = 'cd specjvm2008; java -Xmx{}g -jar SPECjvm2008.jar -Dspecjvm.benchmark.threads=1 all'.format(mem)
    else:
        cmd = 'cd specjvm2008; java -Xmx{}g -jar SPECjvm2008.jar'.format(mem)
        # cmd = 'cd specjvm2008; java -jar SPECjvm2008.jar -wt 5s -it 5s -bt 2 compress'
    pkey = paramiko.RSAKey.from_private_key_file('/Users/Adam/root/stage4/cloud_computing/spot-key.pem')
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy())
    ssh_client.connect(hostname=hostname, username=username, pkey=pkey)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(cmd)

    path = 'results/{}/result_{}.txt'.format(size.lower(), iteration)
    try:
        os.makedirs(os.path.dirname(path))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            print('Error occurred in result writing, no results saved')
            return

    # blocks until the command has finished executing
    status = ssh_stdout.channel.recv_exit_status()
    # ssh_stdout.readlines()
    scp_client = ssh_client.open_sftp()
    scp_client.get('specjvm2008/results/SPECjvm2008.001/SPECjvm2008.001.txt', path)
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

def main():
    for size in sorted(VM_SIZES.keys()):
        for i in range(0, VM_ITERATIONS[size]):
            key = '{}-{}'.format(size, i+1)
            success = False
            while not success:
                if len(virtual_machines) < FREE_SLOTS:
                    virtual_machines[key] = AWSInteractionThread('awsthread.{}-{}'.format(size, i+1), size, VM_SIZES[size], i+1)
                    virtual_machines[key].start()
                    success = True
                else:
                    time.sleep(60)



main()
