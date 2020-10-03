import ast
import os
import networkx as nx
from networkx.drawing.nx_agraph import write_dot
from networkx.readwrite.gpickle import write_gpickle, read_gpickle


call_graph = nx.DiGraph()

def is_valid_func(name):
    # When low_sensitivity is True, any conditions can be added here if the function is too common.
    # For example, filter it out from the output graph directly by name etc.
    return len(name) > 6


def is_buildin_func(name):
    return name in __builtins__.__dict__.keys()


def is_class(name):
    return name[0].isupper()


def set_color_of_node(graph, name, color):
    if name in graph.nodes:
        graph.nodes[name]['fillcolor'] = color
        graph.nodes[name]['style'] = 'filled'


def set_shape_of_node(graph, name, shape):
    if name in graph.nodes:
        graph.nodes[name]['shape'] = shape


class FunctionDefVisitor(ast.NodeVisitor):

    def visit_FunctionDef(self, node):
        call_graph.add_node(node.name)
        set_shape_of_node(call_graph, node.name, 'box')
        set_color_of_node(call_graph, node.name, 'gray')

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
        if func_name is not None:
            call_graph.add_edge(self.parent.name, func_name)
            set_shape_of_node(call_graph, func_name, 'box')
            if is_class(func_name):
                set_color_of_node(call_graph, func_name, 'yellow')
            else:
                set_color_of_node(call_graph, func_name, 'lightgray')
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # Do not iterate 'def func' in func
        if node != self.parent:
            pass
        else:
            self.generic_visit(node)

    def visit_ClassDef(self, node):
        # Do not iterate 'methods of inner class' in func
        pass


if __name__ == '__main__':

    # Root path of the python source code
    # root = os.path.join(os.path.sep, 'Users', 'weizheng', 'Programming', 'Django', 'datagraph')
    root = os.path.join(os.path.sep, 'Users', 'weizheng', 'Programming', 'python', 'coveragepy')
    # Exclude following folder under root
    EXCLUDE_FOLDERS = (
        os.path.join('xpt', 'upgrade'),
        'static_src',
        'venv',
        'migrations',
        '.git',
        '.idea',
    )
    # Function name to inspect
    func_to_check = 'load_plugins'
    # Want to checking calling or being called
    check_calling = True
    # Want to exclude short name functions
    low_sensitivity = False
    # Want to exclude buildin functions
    exclude_build_ins = True
    # Where to load & save graph
    output_file = os.path.join('.', 'build_func_deps.graph')

    if os.path.isfile(output_file):
        call_graph = read_gpickle(output_file)
    else:
        for folder, next_folders, files in os.walk(root):
            for file in files:
                if not any([f in folder for f in EXCLUDE_FOLDERS]) \
                        and 'test' not in file:
                    _, ext = os.path.splitext(file)
                    if ext == '.py':
                        with open(os.path.join(folder, file), 'r') as source:
                            ast_tree = ast.parse(source.read())
                            func_def_visitor = FunctionDefVisitor()
                            func_def_visitor.visit(ast_tree)
        write_gpickle(call_graph, output_file)

    sub_call_graph = call_graph
    if low_sensitivity:
        selected_functions = [n for n, _ in call_graph.nodes(data=True) if is_valid_func(n)]
        sub_call_graph = call_graph.subgraph(selected_functions)
    if exclude_build_ins:
        selected_functions = [n for n, _ in sub_call_graph.nodes(data=True) if not is_buildin_func(n)]
        sub_call_graph = call_graph.subgraph(selected_functions)

    if check_calling:
        paths = nx.single_source_shortest_path(sub_call_graph, func_to_check)
    else:
        paths = nx.single_source_shortest_path(sub_call_graph.reverse(), func_to_check)
    path_functions = set()
    for func_node in paths.items():
        path_functions.update(func_node[1])
    sub_call_graph = call_graph.subgraph(path_functions)
    if func_to_check in sub_call_graph.nodes:
        set_color_of_node(sub_call_graph, func_to_check, 'greenyellow')

    write_dot(sub_call_graph, 'build_func_deps.dot')
