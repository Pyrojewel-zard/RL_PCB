To create an installation module, first change directory to the top-level of the packaage hierarchy (i.e. the location where there is the .toml file and execute the build command. Thie simply runs the build module 

cd ./placer/
python3 -m build

The result is a directory called dist having the contents:
    - <name>-<version>-py3-none-any.whl
    - <name>-<version>.tar.gz
    
Where the name and version fields contain values as specified in setup.py

To install the module, simply run the following command:

pip install <path>/<name>-<version>-py3-none-any.whl

extra information

To print package information use: pip show <package-name>
pip show pcb_placement_engine
