
from AWSInteraction import AWSInteractionThread
from AzureInteraction import AzureInteractionThread

FREE_SLOTS = 15

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

if __name__ == '__main__':
    main()
