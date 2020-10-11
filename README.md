# pyCallGraph

The project uses Python ast module and simple algorithm (but effective) to generate static call graph of Python code. Basically it uses source code information (source file name, line no and col offset) when deciding function definition, but on the calling side, it only consider function names and the number of arguments when adding graph edges. The graph stop at nodes when multiple function definitions can match the calling.

The code and dependencies can be easily adjusted to work with both Python 2.7 or Python 3, but make sure to pickup the Python version matching source code (e.g. do not use Python 2 ast to analyse Python 3, or vise verse.)

NOTE: The purpose is not to achieve absolutely accurate (actually it is impossible), but to provide auxiliary tool to give a more comprehensive and convenient picture of the Python code base.

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
3. Create virtualenv according to Python version:
    ```shell script
    virtualenv -p /home/username/opt/python-2.7.15/bin/python venv
    ```
    Please run according to Python version needed.
4. Upgrade pip in virtual environment to the latest version:
    ```shell script
    ./venv/bin/python -m pip install --upgrade pip
    ```
5. Install `networkx` package:
    ```shell script
    ./venv/bin/pip install networkx
    ```
6. Install `pygraphviz` (please choose Python version according to your needs):
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
7. Now the environment is ready, copy `build_func_deps_config.example.py` to `build_func_deps_config.py` and setup output folder, the source code folders (`source_roots` list), `exclude_folders` and `enable_ambiguity_call_guessing`. The `enable_ambiguity_call_guessing` option allows the tool guess which function is called when multiple function definition matched.
8. Run the following command to generate & save the whole call graphs of the source code to the output folder:
    ```shell script
    ./venv/bin/python build_func_deps.py
    ```
    If on Python 2.7 a error about `enum` happens when trying to run the above command, please run the follow command to install enum support and try again:
    ```shell script
    ./venv/Scripts/pip install enum34
    ```
9. Run the following command to generate the png file for the function to be inspected:
    ```shell script
    ./venv/bin/python build_func_deps_dot.py 'load_plugins' 3 0
    ```
   The first argument is the name of the function to check. The second argument is the `upstream_cutoffs` and the third one is `downstream_cutoff`. Please run the following command to get helps:
    ```shell script
    ./venv/bin/python build_func_deps_dot.py -h
    ```
   The output png file(s) in the png file(s) is in the format of `funcname-source_lineno_coloffset`, as the tool differentiate function definitions with those info (small chances of conflicts as we only use base name of the source file when generating output). The node name(s) in the graph is in the format of `funcname (source lineno)`, and use different colors to represent different function types (`wheat` for normal function, `yellow` for class, `orchid` for property - support is turned off for speeding up, `bisque` for class method, `lightskyblue` for static method and `lightgray` for instance method).
   
   The source info on the node represents which source file on which line the function is defined, and the line number on the edge represents on which line the target function is called.
   
   NOTE: All line numbers and col offsets are estimated, because source code may be changed quite often, and those numbers have already been decided when building the graph. To update them, need to redo the step 8 based on the latest source code.
   
   It is recommended for complex Python code keeping the `upstream_cutoffs` and `downstream_cutoff` not too high, or it will take too much time to generate the result png, or the result png will be empty.
10. From now on repeat step 9 to inspect any other functions. If you want to re-build the whole call graphs, just run step 8 again. Note unnecessary links can be present in the graph as we cannot differentiate functions from the calling side if there are functions having the same name, and the number of arguments matched.
