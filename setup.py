from setuptools import setup

setup(
    name='f1next',
    version='0.1.0',
    py_modules=['f1next'],
    install_requires=[
        'click',
        'requests-cache',
        'appdirs'
    ],
    entry_points={
        'console_scripts': [
            'f1next = f1next:f1next',
        ],
    },
)
