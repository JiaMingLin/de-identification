from common.base import *
from dptable.variance_reduce import VarianceReduce
from dptable.inference import Inference
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
		jtree_cliques = jtree.get_jtree()['cliques']
		var_reduce = VarianceReduce(self.domains, jtree_cliques, 0.2)
		opted_marginals = [sorted(marginal) for marginal in var_reduce.main()]
		
		# find histograms
		combined_queries = self.combine_cliques_for_query(jtree_cliques, opted_marginals)
		hist_dist = HistogramddDist(self.data)
		histogramdds = hist_dist.histogram_dist(combined_queries)
		
		# do inference
		inference = Inference(
			self.data, 
			jtree_path,
			self.domains, 
			opted_marginals,
			histogramdds,
			0.2)
		
		# sampling