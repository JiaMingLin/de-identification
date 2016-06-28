from common.base import Base

import common.constant as c
import rpy2.robjects as ro
import rpy2.rlike.container as rlc

class Inference(Base):
	def __init__(self, data_path, edges, nodes, domain, cluster, epsilon):
		"""
		Initialize the inference class.
		TODO: 1. refactor, the data_path, edges, nodes, domain 
				are temporary to be here.
		param
			data_path: the path of data file.
		param
			edges: the edges in dependency graph.
		param
			nodes: the nodes(attributes) in data set.
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
		self.data_path = data_path
		self.edges = edges
		self.nodes = nodes
		self.cluster = cluster
		self.epsilon = epsilon		
		self.rdomain = self.convert2rdomain(domain)

	def execute(self):
		do_inference = self.get_r_method(c.INFERENCE_R_FILE, 'do_inference')
		sim_data = do_inference(c.R_SCRIPT_PATH, self.cluster, self.edges, self.nodes, self.epsilon, self.data_path, self.rdomain)
		print sim_data

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

