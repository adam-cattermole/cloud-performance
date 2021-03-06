from setuptools import setup

setup(name = 'cloud_benchmark',
      version = 0.1,
      description = 'Tool to run performance benchmarks on cloud infrastructure',
      url = None,
      author = 'Adam Cattermole',
      author_email = 'a.cattermole@newcastle.ac.uk',
      packages = ['src'],
      install_requires = [
        'boto3',
        'awscli',
        'azure',
        'paramiko',
        'requests<2.12.*'
      ],
      zip_safe = False
      )
