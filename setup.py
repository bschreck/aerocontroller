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
        'gpiozero',
        'python-crontab',
        'fire',
        'w1thermsensor'
    ],
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
        ],
    }
)

