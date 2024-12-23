from setuptools import setup, find_packages

# Dynamically fetch version from kptl/__init__.py
version = {}
with open("src/kptl/__init__.py") as f:
    exec(f.read(), version)

setup(
    name="kptl",  # Replace with your package name
    version=version["__version__"],  # Dynamically fetch version from src/__init__.py
    description="A rather opinionated CLI for managing API Products in Kong Konnect.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Panagis Tselentis",
    author_email="tselentispanagis@gmail.com",
    url="https://github.com/pantsel/konnect-portal-ops-examples",  # Update with your repository URL
    packages=find_packages(where="src"),  # Finds packages in src/
    package_dir={"": "src"},  # src/ is the root for the package
    include_package_data=True,
    install_requires=[
        # List your dependencies here
        "PyYAML==6.0.2",
        "requests==2.32.3",
    ],
    extras_require={
        "dev": ["pytest"],  # Development dependencies
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",  # Specify minimum Python version
    entry_points={
        "console_scripts": [
            "kptl=kptl.main:main",  # CLI command 'kptl' runs kptl.main.main()
        ]
    },
)
