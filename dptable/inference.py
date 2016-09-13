from common.base import Base
from rpy2.robjects import pandas2ri

import common.constant as c
import pandas.rpy.common as com
import rpy2.robjects as ro
import rpy2.rlike.container as rlc
import time


class Inference(Base):
	def __init__(self, data, jtree_path, domain, cluster, epsilon = 0.0):
		"""
		Initialize the inference class.
		TODO: 1. refactor, the data_path, edges, nodes, domain 
				are temporary to be here.
		param
			data: the pandas dataframe
			TODO: Because the DPTable algorithm construct lots of attributes when reading data,
					to using memory cache, one should refector the inference step of DPTable.
		param
			jtreepy: the junction tree
			{
				'cliques':[
					[1,2,3],
					[2,3,4],...
				],
				'separators':[
					[2,3],...
				],
				'parents':[1,2,3,4,...]
			}

		param
			domain: data information with format in dictionary

			{
				"A":[1,2,3,4,5],
				"B":[2,3,4,5,6]
			}
		param
			cluster: the merged cluster structure
		param
			epsilon: the privacy budget
		"""
		self.LOG = Base.get_logger("Inference")
		self.data = self.convert2rdataframe(data)
		self.data_size = data.get_count()
		self.epsilon = epsilon
		self.rdomain = self.convert2rdomain(domain)
		self.cluster = self.convert2rlistofvector(cluster)
		self.jtree_path = jtree_path

	def execute(self):
		do_inference = self.get_r_method(c.INFERENCE_R_FILE, 'do_inference')
		simulate = self.get_r_method(c.SIMULATE_R_FILE, 'simulate')

		self.LOG.info("Starting to do inferences...")
		start = time.time()
		model = do_inference(c.R_SCRIPT_PATH, self.cluster, self.jtree_path, self.epsilon, self.data, self.rdomain)
		sim_data = simulate(model, self.data_size)

		end = time.time()
		self.LOG.info("Doing inferences complete in %d seconds." % (end-start))

		pandas_df = pandas2ri.ri2py_dataframe(sim_data)
		return pandas_df.astype(int, copy=False)

	def execute_without_noise(self):
		do_inference_without_noise = self.get_r_method(c.INFERENCE_R_FILE, 'do_inference_without_noise')
		simulate = self.get_r_method(c.SIMULATE_R_FILE, 'simulate')

		model = do_inference_without_noise(c.R_SCRIPT_PATH, self.cluster, self.jtree_path, self.data, self.rdomain)
		sim_data = simulate(model, self.data_size)

		pandas_df = pandas2ri.ri2py_dataframe(sim_data)
		return pandas_df.astype(int, copy=False)

	def convert2rdataframe(self, data):
		return com.convert_to_r_dataframe(data.get_pandas_df())

	def convert2rdomain(self, domain):
		"""
		Convert the general domain to a DPTable specified structure
		Parameter:
			domain
			{
				"A": [1,2,3,4,5],
				"B": [2,3,4,5,6]
			}
		Return:
			{
				"name":['A', 'B',...],
				"dsize":{
					"A": <DOMAIN SIZE OF A>,
					"B": <DOMAIN SIZE OF B>,
					...
				},
				"levels":{
					"A": [1,2,3,4,5],
					"B": [4,5,6,8,9],
					...
				}
			}
		"""
		rname = domain.keys()
		rlevels = ro.ListVector([(item[0], ro.IntVector(item[1])) for item in domain.items()])
		rdsize = ro.ListVector([(item[0], len(item[1])) for item in domain.items()])

		rdomain = ro.ListVector([
			('name', rname),
			('levels', rlevels),
			('dsize', rdsize)
		])
		return rdomain