# pyCallGraph

The project uses Python ast module and very simple algorithm (but effective) to calculate potential static call graph of Python code. Basically it only consider function names and the number of arguments when building the graph. Because nature of this comparison, this tool does not work well when using with a function with common name (e.g. `save`, `load` etc.), although considering arguments can alleviate this issue. It works well with functions that has more specific name (e.g. `load_plugins` etc.).

The code and dependencies can be easily adjusted to work with both Python 2.7 or Python 3, but needs to make sure to pickup the right Python version when analysing source code. In other words, should match the Python version which is used by source code, or the ast module will report syntax error when trying to parse the source code files.

NOTE: The purpose of the code is not to achieve absolutely accurate (actually it is impossible), but to provide auxiliary to work with other methods (like code intelligence of IDE) to give a more comprehensive and convenient picture of the Python code.

## Example
The following example is the result of checking `load_plugins` function of the open source project: https://github.com/nedbat/coveragepy:

![Alt text](build_func_deps.example.png?raw=true "load_plugins graph")

## How to use
Currently as some difficulties to config/run `pygraphviz` package on Windows, only Linux is supported.

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
7. Now the environment is ready, need to change the `build_func_deps_config.py` to setup output folder and mostly importantly the folders of the source code `root` to scan for building the graph.
8. Run the following command to generate & save the whole call graphs of the source code to the output folder:
    ```shell script
    ./venv/bin/python build_func_deps.py
    ```
9. Now run the following command to generate the png file for the function to be inspected by `func_to_check` setting in `build_func_deps_config.py`:
    ```shell script
    ./venv/bin/python build_func_deps_dot.py 'load_plugins' 3 0
    ```
   The first argument is the name of the function to check. The second argument is the `upstream_cutoffs` and the third one is `downstream_cutoff`. There is also a optional `-e` argument to exclude any functions name you do not want to include in the output. Please run the following command to get helps:
    ```shell script
    ./venv/bin/python build_func_deps_dot.py -h
    ```
   The output png file(s) in the png file(s) is in the format of `funcname_minargs_maxargs_type`, as the tool differentiate functions with both their names and the number of arguments. The node name(s) in the graph is in the format of `funcname_minargs_maxargs`, and use different colors to represent different function types (`wheat` for normal function, `yellow` for class, `orchid` for property, `bisque` for class method, `lightskyblue` for static method and `lightgray` for instance method).
   
   It is recommended for complex Python code keeping the `upstream_cutoffs` and `downstream_cutoff` lower than 4, or it will take too much time to generate the result. It is also recommended to set one of parameters to 0 if sometimes the output png layout is confusing.

10. From now on repeat step 9 to inspect any other functions. If you want to re-build the whole call graphs, just run step 8 again.
