import networkx as nx
from networkx.readwrite.gpickle import read_gpickle
from networkx.drawing.nx_agraph import write_dot

from build_func_deps import output_file


def set_color_of_node(graph, name, color):
    if name in graph.nodes:
        graph.nodes[name]['fillcolor'] = color
        graph.nodes[name]['style'] = 'filled'


def set_shape_of_node(graph, name, shape):
    if name in graph.nodes:
        graph.nodes[name]['shape'] = shape


if __name__ == '__main__':
    # networkx 2.2 or above, graphviz or pygraphviz are needed to generate dot & png

    # Function name to inspect
    func_to_check = 'load_plugins'
    # Upstream cutoff (who is calling the func)
    upstream_cutoffs = 3
    # Downstream cutoff (who the func is calling)
    downstream_cutoff = 2

    call_graph = read_gpickle(output_file)
    upstream_paths = {}
    downstream_paths = {}
    if downstream_cutoff > 0:
        upstream_paths = nx.single_source_shortest_path(
            call_graph, func_to_check, cutoff=downstream_cutoff)
    if upstream_cutoffs > 0:
        downstream_paths = nx.single_source_shortest_path(
            call_graph.reverse(), func_to_check, cutoff=upstream_cutoffs)
    path_funcs = set()
    for func_node in upstream_paths.items():
        path_funcs.update(func_node[1])
    for func_node in downstream_paths.items():
        path_funcs.update(func_node[1])
    call_graph = call_graph.subgraph(path_funcs)
    if func_to_check in call_graph.nodes:
        set_color_of_node(call_graph, func_to_check, 'greenyellow')

    write_dot(call_graph, 'build_func_deps.dot')
