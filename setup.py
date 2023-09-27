from setuptools import setup, find_packages

setup(
    name='awsume-1password-plugin-simosca',
    version='1.0.5',
    description='Automates awsume MFA and AWS KEYS via 1Password CLI.',
    entry_points={
        'awsume': [
            '1password = awsume_1password_plugin.1password'
        ]
    },
    author='Inodracs',
    author_email='inodracs.enomis@gmail.com',
    url='https://github.com/SimoSca/awsume-1password-plugin/tree/inodracs',
    py_modules=['1password'],
    packages=find_packages(),
)
