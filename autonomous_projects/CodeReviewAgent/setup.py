from setuptools import setup, find_packages

setup(
    name='CodeReviewAgent',
    version='0.1.0',
    description='Automated code review and feedback for Python code',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/your-repo/code-review-agent',
    packages=find_packages(),
    install_requires=[
        'astroid==2.6.6',
        'isort==5.10.1',
        'mccabe==0.6.1',
        'pylint==2.11.1',
        'pytest==6.2.4',
        'pytest-mock==3.6.1',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'code_review_agent=cli:run_cli',
        ],
    },
)