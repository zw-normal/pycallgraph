# -*- coding: utf-8 -*-

import ast
import os
import pickle
import sys
import fnmatch
from enum import Enum
from collections import defaultdict

import networkx as nx
from networkx.readwrite.gpickle import write_gpickle

from build_func_deps_config import (
    source_roots, exclude_folders, function_name_threahold, output_folder)


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


def record_func_def(func_def):
    call_graph.add_node(
        func_def, label='<{}<BR/><FONT POINT-SIZE="10">{} L{}</FONT>>'.format(
            func_def.name, get_base_source_name(func_def.source), func_def.lineno),
        shape='box', fillcolor=func_def.type.value[1], style='filled')
    func_defs[func_def.name].add(func_def)


def inspect_func_call(source, func, func_def):
    func_call_visitor = FunctionCallVisitor(source, func, func_def)
    func_call_visitor.visit(func)


def get_func_callee_name(callee):
    if isinstance(callee.func, ast.Attribute):
        return callee.func.attr
    elif isinstance(callee.func, ast.Name):
        return callee.func.id
    return None


def record_func_call(caller_def, callee):
    # Caller -> Callee
    func_name = get_func_callee_name(callee)
    if (func_name is not None) and (
            len(func_defs[func_name]) <= function_name_threahold) and (
            not is_buildin_func(func_name)):
        call_args_length = len(callee.args) + len(callee.keywords)
        for func_def in func_defs[func_name]:
            if (call_args_length >= func_def.min_args) and (call_args_length <= func_def.max_args):
                call_graph.add_edge(caller_def, func_def, label='L{}'.format(callee.lineno))


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


def get_base_source_name(source):
    return os.path.basename(source)


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
        return '{} ({} L{} C{})'.format(self.name, self.source, self.lineno, self.col_offset)

    def output_dot_file_name(self):
        return '{}-{}_{}_{}.dot'.format(
            self.name, get_base_source_name(self.source)[0:-3], self.lineno, self.col_offset)

    def output_png_file_name(self):
        return '{}-{}_{}_{}.png'.format(
            self.name, get_base_source_name(self.source)[0:-3], self.lineno, self.col_offset)


class FunctionDefVisitorPhase1(ast.NodeVisitor):
    # Phase 1 is to collect all function defs

    def __init__(self, source):
        self.source = source

    def visit_FunctionDef(self, node):
        if node.name != '__init__':
            # visit_ClassDef handles the constructor
            record_func_def(FunctionDef(self.source, node))

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        for method in (member for member in node.body if isinstance(member, ast.FunctionDef)):
            if method.name == '__init__':
                record_func_def(
                    FunctionDef.from_class_constructor(self.source, method, node.name))
                break

        self.generic_visit(node)


class FunctionDefVisitorPhase2(ast.NodeVisitor):
    # Phase 2 is to build the call graph

    def __init__(self, source):
        self.source = source

    def visit_FunctionDef(self, node):
        if node.name != '__init__':
            # As phase 1, visit_ClassDef handles the constructor
            inspect_func_call(self.source, node, FunctionDef(self.source, node))
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        for method in (member for member in node.body if isinstance(member, ast.FunctionDef)):
            if method.name == '__init__':
                inspect_func_call(
                    self.source, method,
                    FunctionDef.from_class_constructor(self.source, method, node.name))
                break
        self.generic_visit(node)


class FunctionCallVisitor(ast.NodeVisitor):

    def __init__(self, source, caller, caller_def):
        self.source = source
        self.caller = caller
        self.caller_def = caller_def

    def visit_Call(self, node):
        # Caller -> Callee
        record_func_call(self.caller_def, node)
        self.generic_visit(node)

    # def visit_Attribute(self, node):
    #     # Looks like property supporting is time consuming, and not quite useful, let us turn it off for now
    #     # A attribute access can be a property, just need to check whether we have one defined
    #     for func in func_defs[node.attr]:
    #         if (func.type == FuncType.Property) and (
    #                 func.min_args == 0) and (
    #                 func.max_args == 0):
    #             call_graph.add_edge(
    #                 self.caller_def, func,
    #                 label='L{}'.format(node.lineno))
    #     self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # Do not iterate 'def func' in func
        if node == self.caller:
            self.generic_visit(node)

    def visit_ClassDef(self, node):
        # Do not iterate 'inner class' in func
        pass


def scan_source_files(visitor_cls):
    for source_root in source_roots:
        for folder, dirs, files in os.walk(source_root):
            dirs[:] = [d for d in dirs if d not in exclude_folders]
            for source_file in files:
                if fnmatch.fnmatch(source_file, '*.py') and ('test' not in source_file):
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
