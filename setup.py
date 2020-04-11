import setuptools

with open("README.md", "r") as rm:
    long_description = rm.read()

setuptools.setup(
    name="sedex",
    version="0.1.0",
    description="SEDEX Messagebox Manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eraymann/sedex",
    author="Elias Raymann",
    author_email="elias.raymann@swisstopo.ch",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=2.7"
)
