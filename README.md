# pyCallGraph

The project uses Python ast module and very simple algorithm (but effective) to calculate potential static calling or called graph of Python code. Basically it only compares function names and build the graph.

It works better for functions with longer name. Just create a new Python virtual environment and install dependencies from `requirement.txt` and you are ready to go.

ATTENTION: If you want to generate dot graph, make sure the `Graphviz` is installed.

The code and dependencies can be easily adjusted to work on both Python 2.7 or Python 3, but make sure the right Python version is used when analysing source code.

 