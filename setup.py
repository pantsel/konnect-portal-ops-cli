from setuptools import setup, find_packages

version = {}
with open("src/kptl/__init__.py") as f:
    exec(f.read(), version)

setup(
    name="kptl",
    version=version["__version__"],
    description="A rather opinionated CLI for managing API Products in Kong Konnect.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Panagis Tselentis",
    author_email="tselentispanagis@gmail.com",
    url="https://github.com/pantsel/konnect-portal-ops-cli",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "PyYAML==6.0.2",
        "requests==2.32.3",
    ],
    extras_require={
        "dev": ["pytest"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "kptl=kptl.main:main",
        ]
    },
)
