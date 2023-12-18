
from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='plus',
    version='0.1.3',
    description='Plus is a library for managing c++ projects',
    long_description=readme,
    author='Daril Rodriguez',
    author_email='darilrodriguez.2@gmail.com',
    url='https://github.com/darilrt/plus',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)