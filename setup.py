# setup.py

from setuptools import setup, find_packages

setup(
    name='codegen',
    version='0.01',
    packages=find_packages(),
    install_requires=[
        # List your package dependencies here
    ],
    author='Zeeshan Amjad',
    author_email='zeeshan.amjad@gmail.com',
    description='A sample Python package to create DTO and CRUD method in Go from SQL Create table statement',
    url='https://github.com/zamjad/codegen',  
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
