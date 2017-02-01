
from AWSInteraction import AWSInteractionThread
from AzureInteraction import AzureInteractionThread

import threading

AWS_VM = {
            # 't2.micro': 1,
            # 't2.small': 1,
            # 't2.medium': 2,
            # 't2.large': 4,
            # 'm4.large': 4,
            # 'm4.xlarge': 8,
            # 'm4.2xlarge': 16,
            # 'm4.4xlarge': 32,
            # 'c4.large': 2,
            # 'c4.xlarge': 4,
            # 'c4.2xlarge': 8,
            # 'c4.4xlarge': 16
            }

AZURE_VM = {'Basic_A1': 1,
            # 'Basic_A3': 2,
            # 'Basic_A4': 4,
            # 'Standard_D1': 1,
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


VM_ITERATIONS = {'Basic_A1': 2,
                 'Standard_D1_v2': 1}

AZURE_SLOTS = 15
AWS_SLOTS = 15

aws_virtual_machines = {}
azure_virtual_machines = {}


class InitiateThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        if self.name == 'aws':
            virtual_machines = aws_virtual_machines
            vm_types = AWS_VM
            free_slots = AWS_SLOTS
            object_type = AWSInteractionThread

        elif self.name == 'azure':
            virtual_machines = azure_virtual_machines
            vm_types = AZURE_VM
            free_slots = AZURE_SLOTS
            object_type = AzureInteractionThread

        for vm_type in sorted(vm_types.keys()):
            if vm_type in VM_ITERATIONS:
                for i in range(0, VM_ITERATIONS[vm_type]):
                    key = '{}-{}'.format(vm_type, i+1)
                    success = False
                    while not success:
                        if len(virtual_machines) < free_slots:
                            virtual_machines[key] = object_type(
                                '{}.{}-{}'.format(self.name, vm_type, i+1),
                                vm_type,
                                vm_types[vm_type],
                                i+1)
                            virtual_machines[key].start()
                            success = True
                        else:
                            time.sleep(60)

    def purge_complete(self, virtual_machines):
        print("purge")


def main():
    service_providers = ['aws', 'azure']

    initiated_threads = {}
    for provider in service_providers:
        initiated_threads[provider] = InitiateThread(provider)
        initiated_threads[provider].start()


if __name__ == '__main__':
    main()
