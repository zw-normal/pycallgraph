# pyCallGraph

The project uses Python ast module and very simple algorithm (but effective) to calculate potential static calling or called graph of Python code. Basically it only compares function names and build the graph.

It works better for functions with longer name. Just create a new Python virtual environment and install dependencies from `requirement.txt` and you are ready to go.

ATTENTION: If you want to generate dot graph, make sure the `Graphviz` is installed.

The code and dependencies can be easily adjusted to work on both Python 2.7 or Python 3, but make sure the right Python version is used when analysing source code.

NOTE: Although several enhancements can be added to reach more accurate (for example, checking whether the number of function arguments match the function definition), The purpose of the code is not absolutely accurate, but provide auxiliary to work with other methods (like code intelligence of IDE) to give a more comprehensive and convenient picture of the code. 

## Examples
The following are two examples of checking the calling & callee of two functions in open source project: https://github.com/nedbat/coveragepy:

### Callee (who calls the function)
![Alt text](build_func_deps_callee.png?raw=true "Callee")

### Calling (who the function calls)
![Alt text](build_func_deps_calling.png?raw=true "Calling")
 