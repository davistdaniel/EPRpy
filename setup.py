from setuptools import setup,find_packages # type: ignore

setup(
    name='eprpy',
    version='0.9.0',
    description="A python library for working with EPR spectroscopic DATA.",
    python_requires=">=3.9, <3.13.1",
    author_email="davisthomasdaniel@gmail.com",
    install_requires=[
        'numpy>1.25.1,<=1.26.4',
        'matplotlib'
    ],
    packages=find_packages()
)