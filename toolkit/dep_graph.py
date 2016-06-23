from .base import Base
import pandas.rpy.common as com
import rpy2.robjects as robjects



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

        r_df = com.convert_to_r_dataframe(pandas_df)
        rdomain = robjects.ListVector(domain)

        r=robjects.r
        r.source(self.DEP_GRAPH_R_FILE)
        r_dep_edges = r['get_dep_edges']

        self.dep_graph = r_dep_edges(r_df, rdomain)

    def get_dep_edges(self, display = False):

        if(display == True):
            return [list(rls) for rls in list(self.dep_graph)]
        return self.dep_graph


