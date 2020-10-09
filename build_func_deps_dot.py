# -*- coding: utf-8 -*-

import os
import pickle
import subprocess
import argparse

import networkx as nx
from networkx.readwrite.gpickle import read_gpickle
from networkx.drawing.nx_agraph import write_dot

from build_func_deps import (
    output_graph_file as input_graph_file,
    output_def_file as input_def_file,
    FunctionDef, FuncType)
from build_func_deps_config import (output_folder)


# Load existing graph
call_graph = read_gpickle(input_graph_file)
with open(input_def_file, 'rb') as input_def_file:
    func_defs = pickle.load(input_def_file)


# Define and parse the command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('func_to_check', help='The name of function to check', type=str)
parser.add_argument('upstream_cutoffs', help='The cutoff for checking who is calling the func', type=int)
parser.add_argument('downstream_cutoff', help='The cutoff for checking who the func is calling', type=int)
parser.add_argument(
    '-e', '--exclude', help='Comma-separated exclude function names: e.g. save, get_1_1_im',
    required=False, default="")

args = parser.parse_args()
func_to_check = args.func_to_check
upstream_cutoffs = args.upstream_cutoffs
downstream_cutoff = args.downstream_cutoff
exclude_func_names = set()
if args.exclude:
    exclude_func_names.update((e.strip() for e in args.exclude.split(',')))


def generate_dot_png():
    upstream_paths = {}
    downstream_paths = {}
    if upstream_cutoffs > 0:
        upstream_paths = nx.single_target_shortest_path(
            call_graph, func, cutoff=upstream_cutoffs)
    if downstream_cutoff > 0:
        downstream_paths = nx.single_source_shortest_path(
            call_graph, func, cutoff=downstream_cutoff)
    path_funcs = set()
    for func_node in upstream_paths.items():
        path_funcs.update(func_node[1])
    for func_node in downstream_paths.items():
        path_funcs.update(func_node[1])
    if len(path_funcs) > 150:
        print('More than 150 functions in the graph of {}, '
              'please reduce upstream_cutoff and/or downstream_cutoff.'.format(func))
    else:
        if exclude_func_names:
            for func_name in exclude_func_names:
                if func_name != func_to_check:
                    path_funcs = filter(lambda f: func_name not in f.name, path_funcs)
        func_call_graph = call_graph.subgraph(path_funcs)
        func_call_graph.nodes[func]['fillcolor'] = 'greenyellow'

        output_dot_file = os.path.join(output_folder, func.output_dot_file_name())
        output_png_file = os.path.join(output_folder, func.output_png_file_name())

        write_dot(func_call_graph, output_dot_file)
        with open(output_png_file, "wb") as output:
            subprocess.Popen(
                ['dot', '-Tpng', output_dot_file], stdout=output)


if __name__ == '__main__':
    # networkx 2.2 or above, graphviz and pygraphviz are needed to generate dot & png

    func_defs_len = len(func_defs[func_to_check])
    if func_defs_len == 0:
        print('Function {} is not found in the graph.'.format(func_to_check))
    elif func_defs_len > 8:
        print('Function {} has more than 6 different definitions. '
              'May pick another function to check.'.format(func_to_check))
    else:
        for func in func_defs[func_to_check]:
            generate_dot_png()
