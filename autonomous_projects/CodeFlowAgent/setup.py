from setuptools import setup, find_packages

# Define the required packages and their versions
REQUIRED_PACKAGES = [
    'autopep8==1.5.4',
    'pylint==2.11.1',
    'pytest==6.2.4',
    'jsonschema==3.2.0'
]

# Setup configuration
setup(
    name='CodeFlowAgent',
    version='0.1.0',
    description='A lightweight, efficient, and secure tool for developers to enhance their coding flow by automating repetitive tasks.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/CodeFlowAgent',
    packages=find_packages(),
    install_requires=REQUIRED_PACKAGES,
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'codeflowagent=code_flow_agent:main',
        ],
    },
)