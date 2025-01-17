from setuptools import setup, find_packages  # type: ignore

setup(
    name='eprpy',
    version='0.9.0a2',
    description="A Python library for working with EPR spectroscopic data.",
    long_description=open("README.md").read(),  
    long_description_content_type="text/markdown",  
    python_requires=">=3.9, <3.13.1",  
    author="Davis Thomas Daniel",  
    author_email="davisthomasdaniel@gmail.com",  
    url="https://github.com/davistdaniel/EPRpy",  
    classifiers=[
        "Development Status :: 3 - Alpha",  
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "License :: OSI Approved :: MIT License",  
    ],
    install_requires=[
        'numpy>=1.25.1,<=1.26.4',
        'matplotlib',
        'tqdm'
    ],
    packages=find_packages(),
    project_urls={
        "Bug Tracker": "https://github.com/davistdaniel/EPRpy/issues",
        "Documentation": "https://davistdaniel.github.io/EPRpy/",
        "Source Code": "https://github.com/davistdaniel/EPRpy",
    },
)
