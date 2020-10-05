# pyCallGraph

The project uses Python ast module and very simple algorithm (but effective) to calculate potential static call graph of Python code. Basically it only compares function names and build the graph.

The code and dependencies can be easily adjusted to work with both Python 2.7 or Python 3, but needs to make sure to pickup the right Python version when analysing source code. In other words, should match the Python version which is used by source code, or the ast module will report syntax error when trying to parse the source code files.

NOTE: Although several enhancements can be added to achieve more accurate (e.g. checking if the number of calling function arguments matches the function definition), the purpose of the code is not to achieve absolutely accurate (actually it is impossible), but to provide auxiliary to work with other methods (like code intelligence of IDE) to give a more comprehensive and convenient picture of the Python code.

## Example
The following example is the result of checking `load_plugins` function of the open source project: https://github.com/nedbat/coveragepy:

![Alt text](build_func_deps.example.png?raw=true "load_plugins graph")

## How to use
1. Clone the code:
    ```shell script
    git clone https://github.com/zw-normal/pycallgraph.git
    cd pycallgraph
    ```
2. Make sure Python version is the same as the one used to write code being inspected:
    ```shell script
    python --version
    ```
3. Create virtualenv according to python version:
    ```shell script
    virtualenv ./venv
    ```
4. Upgrade pip in virtual environment to the latest version:
    ```shell script
    ./venv/bin/python -m pip install –upgrade pip
    ```
5. Install networkx package:
    ```shell script
    ./venv/bin/pip install networkx
    ```
6. Install pygraphviz:
    * Python 2
    ```shell script
    sudo apt-get install python-dev graphviz libgraphviz-dev pkg-config
    ./venv/bin/pip install pygraphviz
    ```
    
    * Python 3
    ```shell script
    sudo apt-get install python3-dev graphviz libgraphviz-dev pkg-config
    ./venv/bin/pip install pygraphviz
    ```
7. Now the environment is ready, need to change the `build_func_deps_config.py` according to your paths and needs. Remember for complex Python code keep `upstream_cutoffs` and `downstream_cutoff` settings lower than 4, or it will take too much time when running step 9. It is also recommended to set one of parameters to 0 if sometimes the output dot layout is confusing).
8. Run the following command to generate & save the whole call graphs of the source code:
    ```shell script
    ./venv/bin/python build_func_deps.py
    ```
9. Now run the following command to generate the png file for the function to be inspected by `func_to_check` setting in `build_func_deps_config.py`:
    ```shell script
    ./venv/bin/python build_func_deps_dot.py
    ```
10. From now on your can change `func_to_check` in `build_func_deps_config.py` and repeat step 9 to inspect any other functions. If you want to re-build whole call graphs, just run step 8 again.
