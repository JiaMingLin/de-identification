from common.base import Base
import rpy2.robjects as robjects
import common.constant as c
import time


class DependencyGraph(Base):
    
    # The dependency graph
    dep_graph = None

    def __init__(self, data, noise_flag = True, white_list = []):
        """
        __init__
        Input:
            1. DataUtils.Data
        Procedure
            1. Convert the given data frame to dataframe in R
            2. Convert the given Domain(in python dict) to ListVector
            3. Instantial the attributes dependency.
        """
        pandas_df = data.get_pandas_df()
        domain = data.get_domain()
        r_df = self.pandas2ri.py2ri(pandas_df)
        rdomain = robjects.ListVector(domain)

        self.LOG = Base.get_logger("DepGraph")
        self.noise_flag = noise_flag

        self.dep_graph = self._build_dep_graph(r_df, rdomain)
        self.white_list = white_list


    def get_dep_edges(self, display = True):
        import rpy2.robjects as ro
        from itertools import combinations

        edges = [list(rls) for rls in list(self.dep_graph)]
        pairwise_white_list = reduce(lambda acc, curr: acc+curr
                                    ,[list(combinations(cluster, 2)) for cluster in self.white_list]
                                    ,[])

        if display is True:
            return edges + pairwise_white_list
        return ro.Vector([ro.StrVector(e) for e in edges + pairwise_white_list])

    def _build_dep_graph(self, r_df, r_domain):
        r_dep_edges = self.get_r_method(c.DEP_GRAPH_R_FILE, 'get_dep_edges')
        self.LOG.info("Starting to compute Dep-Graph...")
        start = time.time()
        robj = r_dep_edges(r_df, r_domain, self.noise_flag)
        end = time.time()
        self.LOG.info("Compute Dep-Graph complete in %d seconds." % (end-start))

        return robj
