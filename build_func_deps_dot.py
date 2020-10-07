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
    FunctionDef, FuncColor)
from build_func_deps_config import (output_folder)


def set_color_of_node(graph, name, color):
    if name in graph.nodes:
        graph.nodes[name]['fillcolor'] = color
        graph.nodes[name]['style'] = 'filled'


def set_shape_of_node(graph, name, shape):
    if name in graph.nodes:
        graph.nodes[name]['shape'] = shape


parser = argparse.ArgumentParser()
parser.add_argument('func_to_check', help='The name of function to check', type=str)
parser.add_argument('upstream_cutoffs', help='The cutoff for checking who is calling the func', type=int)
parser.add_argument('downstream_cutoff', help='The cutoff for checking who the func is calling', type=int)

if __name__ == '__main__':
    # networkx 2.2 or above, graphviz and pygraphviz are needed to generate dot & png
    args = parser.parse_args()
    func_to_check = args.func_to_check
    upstream_cutoffs = args.upstream_cutoffs
    downstream_cutoff = args.downstream_cutoff

    call_graph = read_gpickle(input_graph_file)
    with open(input_def_file, 'rb') as input_def_file:
        func_defs = pickle.load(input_def_file)

    func_defs_len = len(func_defs[func_to_check])
    if func_defs_len == 0:
        print('Function {} is not found in the graph.'.format(func_to_check))
    elif func_defs_len > 6:
        print('Function {} has more than 6 different definitions. '
              'May pick another function to check.'.format(func_to_check))
    else:
        for func in func_defs[func_to_check]:
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
            if len(path_funcs) > 200:
                print('More than 200 functions in the graph of {}, '
                      'please reduce upstream_cutoff and/or downstream_cutoff.'.format(func))
            else:
                call_graph = call_graph.subgraph(path_funcs)

                if func in call_graph.nodes:
                    set_color_of_node(call_graph, func, 'greenyellow')

                output_dot_file = os.path.join(output_folder, func.output_dot_file_name())
                output_png_file = os.path.join(output_folder, func.output_png_file_name())

                write_dot(call_graph, output_dot_file)
                with open(output_png_file, "wb") as output:
                    subprocess.Popen(
                        ['dot', '-Tpng', output_dot_file], stdout=output)
