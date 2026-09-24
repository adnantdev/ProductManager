from setuptools import setup, find_packages
import sys
import os

with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

with open('README.md', 'r', encoding='utf-8') as f:
    long_descriptions = f.read()


setup(
    name='ProductManagerPro',
    version='3.0.0',
    author='Your Company Name',
    author_email='support@yourcompany.com',
    description='Professional Product Management System for Businesses',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://yourcompany.com/productmanager',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Office/Business',
        'Topic :: Database',
        'Topic :: Desktop Environment',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'productmanager=src.main:main',
        ],
    },
    include_package_data=True,
    package_data={
        'src': ['resources/*', 'resources/**/*'],
    },
)