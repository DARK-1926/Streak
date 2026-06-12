from setuptools import setup, find_packages

setup(
    name='campus_dumpster_monitor',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask==3.0.3',
        'torch==2.3.0',
        'torchvision==0.18.0',
        'pillow==10.4.0',
        'pytest==8.2.2',
    ],
    entry_points={
        'console_scripts': [
            'run-demo=scripts.run_demo:main',
        ],
    },
)
