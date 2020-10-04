import networkx as nx
#from networkx.readwrite.gexf import read_gexf
from networkx.readwrite.gpickle import read_gpickle
from networkx.drawing.nx_agraph import write_dot

from build_func_deps import output_file


def is_valid_func(name):
    # When low_sensitivity is True, any conditions can be added here if the function is too common.
    # For example, filter it out from the output graph directly by name etc.
    return len(name) > 6


def set_color_of_node(graph, name, color):
    if name in graph.nodes:
        graph.nodes[name]['fillcolor'] = color
        graph.nodes[name]['style'] = 'filled'


def set_shape_of_node(graph, name, shape):
    if name in graph.nodes:
        graph.nodes[name]['shape'] = shape


if __name__ == '__main__':
    # Function name to inspect
    func_to_check = 'raw_create_docnote_part'
    # Want to checking calling or being called
    check_calling = True
    # Want to exclude short name functions
    low_sensitivity = False
    # Make sure to cutoff
    path_cutoff = 3

    call_graph = read_gpickle(output_file)
    if low_sensitivity:
        selected_functions = [n for n, _ in call_graph.nodes(data=True) if is_valid_func(n)]
        call_graph = call_graph.subgraph(selected_functions)

    if check_calling:
        paths = nx.single_source_shortest_path(
            call_graph, func_to_check, cutoff=path_cutoff)
    else:
        paths = nx.single_source_shortest_path(
            call_graph.reverse(), func_to_check, cutoff=path_cutoff)
    path_funcs = set()
    for func_node in paths.items():
        path_funcs.update(func_node[1])
    call_graph = call_graph.subgraph(path_funcs)
    if func_to_check in call_graph.nodes:
        set_color_of_node(call_graph, func_to_check, 'greenyellow')

    write_dot(call_graph, 'build_func_deps.dot')
