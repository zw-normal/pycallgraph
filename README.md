# pyCallGraph

The project uses Python ast module and very simple algorithm (but effective) to calculate potential static calling or called graph of Python code. Basically it only compares function names and build the graph.

The code and dependencies can be easily adjusted to work on both Python 2.7 or Python 3, but make sure the right Python version is used when analysing source code.

Please see the comments in the code for how to use it.

NOTE: Although several enhancements can be added to reach more accurate (for example, checking whether the number of function arguments match the function definition), The purpose of the code is not absolutely accurate, but provide auxiliary to work with other methods (like code intelligence of IDE) to give a more comprehensive and convenient picture of the code. 

## Examples
The following example is the result of checking `load_plugins` in open source project: https://github.com/nedbat/coveragepy:

![Alt text](build_func_deps.png?raw=true "load_plugins graph")
