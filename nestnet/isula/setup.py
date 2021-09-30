from setuptools import setup

setup(
    name="isulapy",
    version="0.0.2",
    author="zbc",
    url="https://github.com/baixi123",
    author_email="1426221905@qq.com",
    long_description="The pypi library is used by python to call the isula interface to implement container management. The essence is realized by using Grpc technology to call the isula CRI interface.",
    packages=['isulapy'],
    install_requires=['grpcio'],
    entry_points={
    }
)
