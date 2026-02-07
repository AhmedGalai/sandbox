from setuptools import setup, find_packages

setup(
    name="vse_py",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "dearpygui>=1.10.0",
        "typing-extensions>=4.8.0",
    ],
    python_requires=">=3.8",
    author="VSE Team",
    description="Visual Scripting Environment for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
)
