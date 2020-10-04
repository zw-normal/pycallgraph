import ast
import os
import networkx as nx
from networkx.readwrite.gpickle import write_gpickle


call_graph = nx.DiGraph()


def is_buildin_func(name):
    return name in __builtins__.__dict__.keys()


def is_class(name):
    return name[0].isupper()


class FunctionDefVisitor(ast.NodeVisitor):

    def visit_FunctionDef(self, node):
        call_graph.add_node(node.name, shape='box', fillcolor='lightgray', style='filled')

        func_call_visitor = FunctionCallVisitor(node)
        func_call_visitor.visit(node)
        self.generic_visit(node)


class FunctionCallVisitor(ast.NodeVisitor):

    def __init__(self, parent):
        self.parent = parent

    def visit_Call(self, node):
        # Caller -> Callee
        func_name = None
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id
        if (func_name is not None) and (not is_buildin_func(func_name)):
            if is_class(func_name):
                call_graph.add_node(func_name, shape='box', fillcolor='yellow', style='filled')
            else:
                call_graph.add_node(func_name, shape='box', fillcolor='lightgray', style='filled')
            call_graph.add_edge(self.parent.name, func_name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # Do not iterate 'def func' in func
        if node == self.parent:
            self.generic_visit(node)

    def visit_ClassDef(self, node):
        # Do not iterate 'methods of inner class' in func
        pass


# Where to save graph
output_file = os.path.join('.', 'build_func_deps.graph')

if __name__ == '__main__':
    # networkx 2.2 or above version is needed

    # Roots path of the python source code
    roots = [
        '/Users/weizheng/Programming/Python/coveragepy',
    ]

    for root in roots:
        for folder, next_folders, files in os.walk(root):
            for file in files:
                if ('xtest' not in folder) and \
                        ('test' not in folder) and \
                        ('test' not in file):
                    _, ext = os.path.splitext(file)
                    if ext == '.py':
                        with open(os.path.join(folder, file), 'r') as source:
                            print(source.name)
                            ast_tree = ast.parse(source.read())
                            func_def_visitor = FunctionDefVisitor()
                            func_def_visitor.visit(ast_tree)
    write_gpickle(call_graph, output_file)
