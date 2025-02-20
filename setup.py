from setuptools import setup, find_packages

setup(
    name="adventureai",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "fastapi",
    ],
)
