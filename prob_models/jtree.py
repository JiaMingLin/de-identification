from common.base import Base
import rpy2.robjects as robjects
import common.constant as c

class JunctionTree(Base):
    
    def __init__(self, edges, nodes):
        
        self.jtree = self._build_jtree(edges, nodes)
    
    def get_jtree(self, display = False):
        if(display == True):
            return [list(rls) for rls in list(self.jtree)]

        return self.jtree

    def _build_jtree(self, edges, nodes):

        r_nodes = robjects.StrVector(nodes)
        get_jtree = self.get_r_method(c.JTREE_R_FILE, 'get_jtree')
        return get_jtree(edges, r_nodes)
