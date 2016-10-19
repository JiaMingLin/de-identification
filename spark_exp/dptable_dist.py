from common.base import *
from dptable.variance_reduce import VarianceReduce
from prob_models.jtree import JunctionTree
from spark_exp.data_dist import DataDist
from spark_exp.dep_graph_dist import DepGraphDist
from spark_exp.histogramdd_dict import HistogramddDist


class DPTableDist(Base):
	def __init__(self, data, partitions_num = 120):
		# read data
		self.data = data
		# repartition
		self.data.coalesce(partitions_num)
		self.df = data.get_df()
		self.domains = data.get_domains()

	def run(self):
		# build markov graph
		graph = DepGraphDist(self.data)
		edges = graph.fit()
		nodes = self.domain.keys()
		
		# build junction tree
		jtree_path = c.TEST_JTREE_FILE_PATH
		jtree = JunctionTree(edges, nodes, jtree_path)
		
		# merge cliques to reduce variance
		var_reduce = VarianceReduce(self.domains, jtree.get_jtree()['cliques'], 0.2)
		opted_marginals = var_reduce.main()
		
		# do inference
		# sampling