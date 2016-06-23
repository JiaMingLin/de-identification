import os

class Base(object):

    """
    Properties
    """
    ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
    R_SCRIPT_PATH = os.path.join(ROOT_PATH, 'R/')

    DEP_GRAPH_R_FILE = os.path.join(R_SCRIPT_PATH,"dep-graph.R")

