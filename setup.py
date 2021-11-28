from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="myenergi_api",
    version="0.1.1",
    description="API for MyEnergi devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/claytonn/myenergi_api",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=["requests>=2.22.0", "packaging>=20.0"],
)
