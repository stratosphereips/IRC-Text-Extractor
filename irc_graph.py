from graphviz import Digraph

class Node(object):
    def __init__(self, ip: str, port: int, name: str):
        self.ip = ip
        self.port = port
        self.name = name

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.ip == other.ip and self.port == other.port and self.name == other.name
        return False

    def id(self):
        hash_node = lambda v: str(abs(hash(v)) % (10 ** 8))
        return hash_node(self.name)
        # return self.ip

    def label(self):
        return self.name
        # return self.ip


class Edge(object):
    def __init__(self, src_node: Node, dst_node: Node, msg: str, time: int, pkt_size: int, directional=True):
        self.src_node = src_node
        self.dst_node = dst_node
        self.msg = msg
        self.time = time
        self.pkt_size = pkt_size
        self.directional = directional

    def __eq__(self, other):
        if isinstance(other, Edge):
            return self.src_node == other.src_node and \
                   self.dst_node == other.dst_node and \
                   self.time == other.time and \
                   self.msg == other.msg
        return False


class Graph(object):
    def __init__(self, nodes=None, edges=None):
        if nodes is None:
            nodes = []
        if edges is None:
            edges = []
        self.nodes = nodes
        self.edges = edges

    def add_node(self, node: Node) -> bool:
        """ :returns False if the node is already in nodes
            :returns True otherwise
        """
        if node not in self.nodes:
            self.nodes.append(node)
            return True

        return False

    def add_edge(self, edge: Edge) -> bool:
        """ :returns False if the edge is already in edges
            :returns True otherwise
        """
        if edge not in self.edges:
            self.edges.append(edge)
            return True


def build_graph(irc_logs):
    print('building graph...')
    graph = Graph()
    for log in irc_logs:
        v1_ip, v1_port, v1_name = log['src_ip'], log['src_port'], log['src']
        v2_ip, v2_port, v2_name = log['dst_ip'], log['dst_port'], log['dst']
        for m in log['msgs']:
            msg = m['msg']
            time = m['timestamp']
            size = m['pkt_size']
            v1, v2 = Node(v1_ip, v1_port, v1_name), Node(v2_ip, v2_port, v2_name)
            e = Edge(v1, v2, msg, time, size)
            graph.add_node(v1)
            graph.add_node(v2)
            graph.add_edge(e)

    return graph


def visualize_graph(graph, tree_path):
    print('visualizing graph...')
    dot = Digraph('IRC Tree', filename=tree_path)
    dot.graph_attr.update(sep='+100,s100')

    edges = set()
    for edge in graph.edges:
        v1, v2 = edge.src_node, edge.dst_node

        # comment this block of code to show non-duplicate edges between nodes
        dot.node(v1.id(), label=v1.label())
        dot.node(v2.id(), label=v2.label())
        dot.edge(v1.id(), v2.id())

        # uncomment this block of code to show duplicate edges between nodes
        if (v1.id(), v2.id()) not in edges:
            edges.add((v1.id(), v2.id()))
            dot.node(v1.id(), label=v1.label())
            dot.node(v2.id(), label=v2.label())
            dot.edge(v1.id(), v2.id())
    dot.view()
