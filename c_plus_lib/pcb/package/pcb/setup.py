import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name="pcb_file_io",
    version="0.0.1",
    author="Luke Vassallo",
    author_email="lukevassallo95@gmail.com",
    description="pcb placement engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.github.com/lukevassallo/pcb",
    project_urls={
        "example_site": "https://www.lukevassallo.com" 
    },
    classifiers=[
        "Progamming Language :: Python :: 3"
    ],
    package_dir={"": "src"},    
    package_data={
        # If any package contains *.so, include them:
        "": ["*.so",],
    },    
    packages=setuptools.find_packages(where="src"),
    python_requires=">3.6",
    install_requires=['pcb_netlist_graph']
)
