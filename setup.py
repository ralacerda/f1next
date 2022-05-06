import pathlib
from setuptools import setup

# This configuration file is based on:
# https://realpython.com/pypi-publish-python-package/

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="f1next",
    version="0.1.0",
    license="MIT",
    author="Renato Lacerda",
    author_email="renato.ac.lacerda@gmail.com",
    py_modules=["f1next"],
    description="Simple python script to get information about the next Formula 1 Grand Pix",
    long_description=README,
    long_description_content_type="text/markdown",
    install_requires=["click", "requests-cache", "appdirs", "python-dateutil"],
    url="https://github.com/ralacerda/f1next",
    entry_points={
        "console_scripts": [
            "f1next = f1next:f1next",
        ],
    },
)
