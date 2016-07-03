from common.base import Base
import rpy2.robjects as robjects
import common.constant as c

class JunctionTree(Base):
	
	def __init__(self, edges, nodes, jtree_path):
		
		edges = self.convert2rlistofvector(edges)

		self.jtree = self._build_jtree(edges, nodes, jtree_path)
	
	def get_jtree(self):
		"""
		Return
		{
			"cliques":[[1,2,3,4],[3,4,5,6],...],
			"separators":[[3,4],...],
			"parents":[1,2,3,4]
		}
		"""
		names = list(self.jtree.names)
		jtreepy = dict()
		for name in names:
			index = names.index(name)
			if name != 'parents':
				jtreepy[name] = [list(component) for component in list(self.jtree[index])]
			else:
				jtreepy[name] = list(self.jtree[index])		
		return jtreepy

	def _build_jtree(self, edges, nodes, jtree_path):

		r_nodes = robjects.StrVector(nodes)
		get_jtree = self.get_r_method(c.JTREE_R_FILE, 'get_jtree')
		return get_jtree(edges, r_nodes, jtree_path)
