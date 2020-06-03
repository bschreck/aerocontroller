from setuptools import setup, find_packages
from kojifier import __version__

extras_require={
    'rpi': [
        'RPi.GPIO',
    ],
    'test': [
        'pytest',
        'fake_rpi'
    ]
}

setup(
    name='kojifier',
    version=__version__,
    author='bschreck',
    description='Software to control a fermentation incubator',
    packages=find_packages(),
    install_requires=[
        'python-periphery',
        'gpiozero',
        'python-crontab',
        'fire',
        'w1thermsensor',
        'twilio',
        'python-dotenv',
        'pyyaml',
        'simple-pid',
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
            'kojify_adjust = kojifier.incubator:cli',
            'kojify_schedule = kojifier.schedule:schedule',
            'auto_fermenter = kojifier.auto_fermenter:cli'
        ],
    }
)

