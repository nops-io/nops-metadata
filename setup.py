import time
from datetime import datetime

import setuptools

now = datetime.now()

setuptools.setup(
    name="metadata_producer",
    version=f"{now.year}.{now.month}.{now.day}.{now.hour}_{now.minute}",
    author="Nikita Zagorskiy",
    author_email="nikita@nops.io",
    description="Package to pull metadata from all the supported sources.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=["boto3>1.21.0", "pyrsistent>0.18.0"],
)
