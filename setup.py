from setuptools import setup, find_packages
from aerocontroller import __version__

extras_require={
    'rpi': [
        'RPi.GPIO',
    ],
    'test': [
        'pytest',
        'fake_rpi'
    ],
    'opt': [
        'torch',
        'torchvision'
    ]
}

setup(
    name='aerocontroller',
    version=__version__,
    author='bschreck',
    description='Software to control an aeroponics rig',
    packages=find_packages(),
    install_requires=[
        'python-periphery',
        'gpiozero',
        'python-crontab',
        'fire',
        'twilio',
        'python-dotenv',
        'pyyaml',
        'pandas'
    ],
    extras_require=extras_require,
    tests_require=extras_require['test'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.7"
    ],
    package_data={"": ["*.txt", "*.yml", "*.yaml", "*.json"]},
    include_package_data=True,
    entry_points={
    'console_scripts': [
            'start_aerocontroller = aerocontroller.controller:main',
        ],
    }
)

