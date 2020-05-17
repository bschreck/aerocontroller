from setuptools import setup, find_packages
from kojifier import __version__

setup(
    name='kojifier',
    version=__version__,
    author='bschreck',
    description='Software to control a fermentation incubator',
    packages=find_packages(),
    install_requires=[
        'python-periphery',
        'RPi-GPIO'
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.7"
    ],
    package_data={"": ["*.txt", "*.yml", "*.yaml", "*.json"]},
    include_package_data=True,
    entrypoints={
    'console_scripts': [
            'kojify = kojifier.incubator:incubate',
        ],
    }
)

