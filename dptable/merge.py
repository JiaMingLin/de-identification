from common.base import Base
import math
import random
import operator
import time
import numpy as np
import cvxpy as cvx

class CliqueMerge(Base):
    def __init__(self, domain, jtree, clusters_num, _lambda):
    	self.domain = domain
    	self.node_card = [len(vals) for vals in domain.values()]
        pass
