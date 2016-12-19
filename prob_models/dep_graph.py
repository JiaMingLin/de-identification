
import rpy2.robjects as ro
import common.constant as c
import time

from common.base import Base
from itertools import combinations


class DependencyGraph(Base):
    
    # The dependency graph
    dep_graph = None

    def __init__(self, data = None, edges = None, noise_flag = True, white_list = [], eps1_val = c.EPSILON_1):
        """
        __init__
        Input:
            1. DataUtils.Data
        Procedure
            1. Convert the given data frame to dataframe in R
            2. Convert the given Domain(in python dict) to ListVector
            3. Instantial the attributes dependency.
        """
        self.LOG = Base.get_logger("DepGraph")
        self.noise_flag = noise_flag
        self.eps1_val = eps1_val
        if data is None:
           self.edges = edges
           self.edges_robj = self._get_edges_in_r(self.edges)
        else:
            pandas_df = data.get_pandas_df()
            domain = data.get_domain()
            r_df = self.pandas2ri.py2ri(pandas_df)
            rdomain = ro.ListVector(domain)
            self.edges_robj = self._build_dep_graph(r_df, rdomain)
            self.edges = self._get_edges_in_py(self.edges_robj)

        self.white_list = white_list


    def get_dep_edges(self, display = True):
        pairwise_white_list = reduce(lambda acc, curr: acc+curr
                                    ,[list(combinations(cluster, 2)) for cluster in self.white_list]
                                    ,[])
        if display is False:
            return _get_edges_in_r(self.edges + pairwise_white_list)
        return self.edges + pairwise_white_list

    def set_white_list(self, white_list):
        self.white_list = white_list
        return self

    def _get_edges_in_r(self, edges):
        return ro.Vector([ro.StrVector(e) for e in edges])

    def _get_edges_in_py(self, redges):
        return [list(rls) for rls in list(redges)]

    def _build_dep_graph(self, r_df, r_domain):
        r_dep_edges = self.get_r_method(c.DEP_GRAPH_R_FILE, 'get_dep_edges')
        self.LOG.info("Starting to compute Dep-Graph with eps1: %.2f..." % self.eps1_val)
        start = time.time()
        robj = r_dep_edges(r_df, r_domain, self.noise_flag, self.eps1_val)
        end = time.time()
        self.LOG.info("Compute Dep-Graph complete in %d seconds." % (end-start))

        return robj


