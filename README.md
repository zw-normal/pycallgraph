# pyCallGraph

The project uses Python ast module and very simple algorithm (but effective) to calculate potential static calling or called graph of Python code. Basically it only compares function names and build the graph.

The code and dependencies can be easily adjusted to work on both Python 2.7 or Python 3, but make sure the right Python version is used when analysing source code.

Please see the comments in the code for how to use it.

NOTE: Although several enhancements can be added to reach more accurate (for example, checking whether the number of function arguments match the function definition), The purpose of the code is not absolutely accurate, but provide auxiliary to work with other methods (like code intelligence of IDE) to give a more comprehensive and convenient picture of the code. 

## Examples
The following example is the result of checking `load_plugins` in open source project: https://github.com/nedbat/coveragepy:

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
4. Upgrade pip in venv to the latest version:
    ```shell script
    ./venv/bin/python -m pip install –upgrade pip
    ```
5. Install networkx:
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
7. Now the environment is ready, need to change the `build_func_deps_config.py` according to your paths and needs. Remember for complex code keep `upstream_cutoffs` and `downstream_cutoff` lower than 4, or it will take too much time when running step 9
8. Run the following command to generate & save the whole call graph:
    ```shell script
    ./venv/bin/python build_func_deps.py
    ```
9. Now run the following command to generate the png file for the function set in `func_to_check`:
    ```shell script
    ./venv/bin/python build_func_deps_dot.py
    ```
10. From now on your can change `func_to_check` in `build_func_deps_config.py` and repeat step 9 to inspect any other functions
