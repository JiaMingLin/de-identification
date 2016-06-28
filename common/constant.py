import os

ROOT_PATH = os.path.dirname(os.path.dirname(__file__))

"""
R file path
"""
R_SCRIPT_PATH = os.path.join(ROOT_PATH, 'R/')
DEP_GRAPH_R_FILE = os.path.join(R_SCRIPT_PATH, "dep-graph.R")
JTREE_R_FILE = os.path.join(R_SCRIPT_PATH, "jtree.R")
INFERENCE_R_FILE = os.path.join(R_SCRIPT_PATH, "inference.R")

"""
Test file path
"""
TEST_FILE_PATH = os.path.join(ROOT_PATH, 'static/test/')
TEST_DATA_PATH = os.path.join(TEST_FILE_PATH, 'Data2-coarse.csv')