import pygraphviz as pygviz


class SyntaxTree(object):
    """
    Implements the graph drawing wrapper for the syntax tree

    ### Arguments
    - out_image_dir : the output tree image location

    ### Attributes
    - out_image_dir : the image name, used for storing the output image
    - dot : PyGraphviz object, abstract all the graph operations for us
    - counter : internal variable used to avoid name duplication
    """

    def __init__(self, out_image_dir="syntax_tree_output"):
        """
        Constructor
        """
        self.out_image_dir = out_image_dir
        self.dot = pygviz.AGraph()
        self.counter = 0

    def create_node(self, node_name, node_text, shape='square', inline_with=None):
        """
        Attempts to draw a node @ the graph

        ### Arguments
        - node_name : the unique node identifier
        - node_text : text to display at the node body
        - shape : the node shape, can be either "square" or "circle"
        - inline_with : the node name of the node at the same scope
        """
        self.dot.add_node(node_name + str(self.counter), label=node_text, shape=shape)
        ret = node_name+str(self.counter)
        self.counter += 1
        if inline_with is not None:
            self.dot.subgraph(nbunch=[inline_with, ret],rank='same')
            self.dot.add_edge(inline_with, ret)
        return ret

    def connect_node(self, name1, name2):
        """
        Attempts to connect two nodes of id <name1> ---> <name2>
        in an up-down mannar

        ### Arguments
        - name1 : the first node in the connection
        - name2 : the 2nd node in the connection
        """
        self.dot.add_edge(name1, name2)

    def show(self):
        """
        Shows the whole graph, exports an image @ the dir given at the constructor
        """
        self.dot.draw(self.out_image_dir, prog='dot')
