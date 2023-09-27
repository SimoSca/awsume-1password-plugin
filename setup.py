from setuptools import setup

setup(
    name='awsume-1password-plugin-simosca',
    version='1.0.0',
    description='Automates awsume MFA and AWS KEYS via 1Password CLI.',
    entry_points={
        'awsume': [
            '1password = 1password'
        ]
    },
    author='Inodracs',
    author_email='inodracs.enomis@gmail.com',
    url='https://github.com/SimoSca/awsume-1password-plugin/tree/inodracs',
    py_modules=['1password'],
)
