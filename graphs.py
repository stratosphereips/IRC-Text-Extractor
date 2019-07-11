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
        # hash_node = lambda v: str(abs(hash(v)) % (10 ** 8))
        # return hash_node(self.name)
        return self.ip

    def label(self):
        # return self.name
        return self.ip


class Edge(object):
    def __init__(self, src_node: Node, dst_node: Node, label='', directional=True):
        self.src_node = src_node
        self.dst_node = dst_node
        self.label = label
        self.directional = directional

    def __eq__(self, other):
        if isinstance(other, Edge):
            return self.src_node == other.src_node and self.dst_node == other.dst_node and self.label == other.label
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
