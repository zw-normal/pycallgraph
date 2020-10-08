# -*- coding: utf-8 -*-

import ast
import os
import pickle
import sys
from enum import Enum
from collections import defaultdict

import networkx as nx
from networkx.readwrite.gpickle import write_gpickle

from build_func_deps_config import roots, output_folder


call_graph = nx.DiGraph()
func_defs = defaultdict(set)


class FuncType(Enum):
    Normal = ('n', 'wheat')
    Class = ('cl', 'yellow')
    Property = ('p', 'orchid')
    ClassMethod = ('c', 'bisque')
    StaticMethod = ('s', 'lightskyblue')
    InstanceMethod = ('i', 'lightgray')


def is_buildin_func(name):
    return name in __builtins__.__dict__.keys()


def get_function_type(func):

    def is_instance_method():
        args_len = len(func.args.args)
        if args_len > 0:
            first_arg = func.args.args[0]
            if sys.version_info.major >= 3:
                first_arg = first_arg.arg
            elif isinstance(first_arg, ast.Name):
                first_arg = first_arg.id
            if isinstance(first_arg, str) and first_arg == 'self':
                return True
        return False

    for decorator in func.decorator_list:
        if isinstance(decorator, ast.Name):
            if decorator.id == 'property':
                return FuncType.Property
            elif decorator.id == 'classmethod':
                return FuncType.ClassMethod
            elif decorator.id == 'staticmethod':
                return FuncType.StaticMethod

    if is_instance_method():
        return FuncType.InstanceMethod
    return FuncType.Normal


def add_func_node(func):
    call_graph.add_node(
        func, label='<{}<BR/><FONT POINT-SIZE="10">{} L{}</FONT>>'.format(
            func.name, func.get_base_source_name(), func.lineno),
        shape='box', fillcolor=func.type.value[1], style='filled')


def get_min_args(func, func_type):
    min_args = len(func.args.args) - len(func.args.defaults)
    if func_type not in (FuncType.Normal, FuncType.StaticMethod):
        return min_args - 1
    return min_args


def get_max_args(func, func_type):
    if (func.args.vararg is not None) or \
            (func.args.kwarg is not None):
        return float('inf')

    max_args = len(func.args.args)
    if func_type not in (FuncType.Normal, FuncType.StaticMethod):
        return max_args - 1
    return max_args


class FunctionDef:

    def __init__(self, source, node):
        self.source = source
        self.lineno = node.lineno
        self.col_offset = node.col_offset

        self.name = node.name
        self.type = get_function_type(node)
        self.min_args = get_min_args(node, self.type)
        self.max_args = get_max_args(node, self.type)

    @classmethod
    def from_class_constructor(cls, source, node, class_name):
        func_def = cls(source, node)
        func_def.name = class_name
        func_def.type = FuncType.Class
        return func_def

    def __eq__(self, other):
        if isinstance(other, FunctionDef):
            return (self.source == other.source) and \
                   (self.lineno == other.lineno) and \
                   (self.col_offset == other.col_offset)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.source, self.lineno, self.col_offset))

    def __repr__(self):
        return '{} ({} {})'.format(self.name, self.get_base_source_name(), self.lineno)

    def get_base_source_name(self):
        return os.path.basename(self.source)

    def output_dot_file_name(self):
        return '{}-{}_{}_{}.dot'.format(self.name, self.get_base_source_name()[0:-3], self.lineno, self.col_offset)

    def output_png_file_name(self):
        return '{}-{}_{}_{}.png'.format(self.name, self.get_base_source_name()[0:-3], self.lineno, self.col_offset)


class FunctionDefVisitorPhase1(ast.NodeVisitor):
    # Phase 1 is to collect all function defs

    def __init__(self, source):
        self.source = source

    def visit_FunctionDef(self, node):
        if node.name != '__init__':
            # visit_ClassDef handles the constructor
            func_def = FunctionDef(self.source, node)
            add_func_node(func_def)
            func_defs[node.name].add(func_def)

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        for method in (member for member in node.body if isinstance(member, ast.FunctionDef)):
            if method.name == '__init__':
                func_def = FunctionDef.from_class_constructor(self.source, method, node.name)
                add_func_node(func_def)
                func_defs[node.name].add(func_def)
                break

        self.generic_visit(node)


class FunctionDefVisitorPhase2(ast.NodeVisitor):
    # Phase 2 is to build the call graph

    def __init__(self, source):
        self.source = source

    def visit_FunctionDef(self, node):
        if node.name != '__init__':
            # As phase 1, visit_ClassDef handles the constructor
            func_def = FunctionDef(self.source, node)
            func_call_visitor = FunctionCallVisitor(node, func_def)
            func_call_visitor.visit(node)

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        for method in (member for member in node.body if isinstance(member, ast.FunctionDef)):
            if method.name == '__init__':
                func_def = FunctionDef.from_class_constructor(self.source, method, node.name)
                func_call_visitor = FunctionCallVisitor(method, func_def)
                func_call_visitor.visit(method)
                break
        self.generic_visit(node)


class FunctionCallVisitor(ast.NodeVisitor):

    def __init__(self, caller, caller_def):
        self.caller = caller
        self.caller_def = caller_def

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
                if (call_args_length >= func.min_args) and (call_args_length <= func.max_args):
                    call_graph.add_edge(self.caller_def, func)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        # A attribute access can be a property, just need to check whether we have one defined
        for func in func_defs[node.attr]:
            if (func.type == FuncType.Property) and (
                    func.min_args == 0) and (
                    func.max_args == 0):
                call_graph.add_edge(self.caller_def, func)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # Do not iterate 'def func' in func
        if node == self.caller:
            self.generic_visit(node)

    def visit_ClassDef(self, node):
        # Do not iterate 'inner class' in func
        pass


def scan_source_files(visitor_cls):
    for root in roots:
        for folder, _, files in os.walk(root):
            for source_file in files:
                if ('xtest' not in folder) and \
                        ('test' not in folder) and \
                        ('test' not in source_file):
                    _, ext = os.path.splitext(source_file)
                    if ext == '.py':
                        with open(os.path.join(folder, source_file), 'r') as source:
                            print('Scanning {}'.format(source.name))
                            ast_tree = ast.parse(source.read())
                            visitor = visitor_cls(source.name)
                            visitor.visit(ast_tree)


output_graph_file = os.path.join(output_folder, 'build_func_deps.graph')
output_def_file = os.path.join(output_folder, 'build_func_deps.def')

if __name__ == '__main__':
    # networkx 2.2 or above version is needed

    # Phrase 1
    scan_source_files(FunctionDefVisitorPhase1)
    with open(output_def_file, 'wb') as output_file:
        pickle.dump(func_defs, output_file)

    # Phrase 2
    scan_source_files(FunctionDefVisitorPhase2)
    write_gpickle(call_graph, output_graph_file)
