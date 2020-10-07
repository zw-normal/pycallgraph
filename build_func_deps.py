import ast
import os
import pickle
import sys
from collections import defaultdict

import networkx as nx
from networkx.readwrite.gpickle import write_gpickle

from build_func_deps_config import roots, output_folder

call_graph = nx.DiGraph()
func_defs = defaultdict(set)


def is_buildin_func(name):
    return name in __builtins__.__dict__.keys()


def is_class(name):
    return name[0].isupper()


def is_class_or_instance_method(arguments):
    args_len = len(arguments.args)
    if args_len > 0:
        first_arg = arguments.args[0]
        if sys.version_info.major >= 3:
            first_arg = first_arg.arg
        elif isinstance(first_arg, ast.Name):
            first_arg = first_arg.id
        if isinstance(first_arg, str) and (first_arg == 'cls' or first_arg == 'self'):
            return True
    return False


def get_min_args(arguments):
    min_args = len(arguments.args) - len(arguments.defaults)
    if is_class_or_instance_method(arguments):
        return min_args - 1
    return min_args


def get_max_args(arguments):
    if (arguments.vararg is not None) or \
            (arguments.kwarg is not None):
        return float('inf')
    elif is_class_or_instance_method(arguments):
        return len(arguments.args) - 1
    return len(arguments.args)


class FunctionDef:

    def __init__(self, node):
        self.name = node.name
        self.min_args = get_min_args(node.args)
        self.max_args = get_max_args(node.args)

    def __eq__(self, other):
        if isinstance(other, FunctionDef):
            return (self.name == other.name) and \
                   (self.min_args == other.min_args) and \
                   (self.max_args == other.max_args)

    def __hash__(self):
        return hash((self.name, self.min_args, self.max_args))

    def __repr__(self):
        return '{}_{}_{}'.format(self.name, self.min_args, self.max_args)

    def output_dot_file_name(self):
        return '{}_{}_{}.dot'.format(self.name, self.min_args, self.max_args)

    def output_png_file_name(self):
        return '{}_{}_{}.png'.format(self.name, self.min_args, self.max_args)


class FunctionDefVisitorPhase1(ast.NodeVisitor):
    # Phase 1 is to collect all function defs
    def visit_FunctionDef(self, node):
        func_def = FunctionDef(node)
        call_graph.add_node(func_def, shape='box', fillcolor='lightgray', style='filled')
        func_defs[node.name].add(func_def)

        self.generic_visit(node)


class FunctionDefVisitorPhase2(ast.NodeVisitor):
    # Phase 2 is to build the actual call graph
    def visit_FunctionDef(self, node):
        func_call_visitor = FunctionCallVisitor(node)
        func_call_visitor.visit(node)
        self.generic_visit(node)


class FunctionCallVisitor(ast.NodeVisitor):

    def __init__(self, parent):
        self.parent = parent
        self.parent_def = FunctionDef(parent)

    def visit_Call(self, node):
        # Caller -> Callee
        func_name = None
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id
        if (func_name is not None) and (not is_buildin_func(func_name)):
            call_args_length = len(node.args) + len(node.keywords)
            for func in func_defs[func_name]:
                if (call_args_length >= func.min_args) and (
                        call_args_length <= func.max_args):
                    call_graph.add_edge(self.parent_def, func)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # Do not iterate 'def func' in func
        if node == self.parent:
            self.generic_visit(node)

    def visit_ClassDef(self, node):
        # Do not iterate 'methods of inner class' in func
        pass


def scan_source_files(visitor):
    for root in roots:
        for folder, next_folders, files in os.walk(root):
            for file in files:
                if ('xtest' not in folder) and \
                        ('test' not in folder) and \
                        ('test' not in file):
                    _, ext = os.path.splitext(file)
                    if ext == '.py':
                        with open(os.path.join(folder, file), 'r') as source:
                            ast_tree = ast.parse(source.read())
                            visitor.visit(ast_tree)


output_graph_file = os.path.join(output_folder, 'build_func_deps.graph')
output_def_file = os.path.join(output_folder, 'build_func_deps.def')

if __name__ == '__main__':
    # networkx 2.2 or above version is needed

    # Phrase 1
    scan_source_files(FunctionDefVisitorPhase1())
    with open(output_def_file, 'wb') as output_file:
        pickle.dump(func_defs, output_file)

    # Phrase 2
    scan_source_files(FunctionDefVisitorPhase2())
    write_gpickle(call_graph, output_graph_file)
