from common.base import *
from time import time
from base_func_dist import FunctionDist

class DepGraphDist(Base):
	def __init__(self, 
			data, 
			eps1 = 1.0, 
			threh = 0.2, 
			batch_size = 500, 
			partitions = 120):
		
		self.LOG = Base.get_logger("DepGraphDist")
		self.data = data
		self.eps1 = eps1
		self.threh = threh
		self.batch_size = batch_size
		self.partitions = partitions
	
	def fit(self):
		df = self.data.get_df()
		domains = self.data.get_domains()
		self.LOG.info("Coalesce data starting...")
		t1 = time
		df = df.coalesce(self.partitions)
		df.persist()
		nrow = df.count()
		self.LOG.info("Coalesce data complete in %d sec." % (time() - t1))
		
		features = domains.keys()
		ncols = len(features); index = range(features)
		
		batch = self.get_attrs_batch(index)

		for one_round in batch:
			pair_count = df.mapPartitions(lambda iterable: FunctionDist.pair_func_cnt(iterable, one_round)) \
						.repartitionAndSortWithinPartitions(
							self.batch_size, 
							lambda e: (((2 * ncols -1 -e[0]) * e[0]) / 2 + (e[1] - e[0]) -1 ) % self.batch_size
						) \
						.mapPartitions(FunctionDist.g_test)
			print pair_count.collect()

	def get_attrs_batch(self, attrs):
		# drop those attributes with empty name
		attrs = [a for a in attrs if len(str(a)) > 0 ]
		# the set of all pair attributes combinations
		comb_attrs = list(combinations(attrs, 2))
		stairs = np.arange(0, len(comb_attrs), step = self.batch_size)
		return [comb_attrs[left:left+self.batch_size] for left in stairs]
		