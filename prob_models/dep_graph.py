from common.base import Base
import rpy2.robjects as robjects
import common.constant as c


class DependencyGraph(Base):
    
    # The dependency graph
    dep_graph = None

    def __init__(self, data):
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

        self.dep_graph = self._build_dep_graph(r_df, rdomain)

    def get_dep_edges(self, display = False):

        if(display == True):
            return [list(rls) for rls in list(self.dep_graph)]
        return self.dep_graph

    def _build_dep_graph(self, r_df, r_domain):
        r_dep_edges = self.get_r_method(c.DEP_GRAPH_R_FILE, 'get_dep_edges')
        return r_dep_edges(r_df, r_domain)
