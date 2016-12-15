import json

from celery import shared_task,current_task
from itertools import product

from api.models import *
from common.enums import *
from common.base import *

from datetime import datetime

@shared_task
def create_utility_measure(request):
	
	is_celery = False if 'unitest' in request.keys() else True

	process_update(c.CELERY_PROGRESS, 0, 'Initialize', is_celery)
	# get task ids
	task_ids = request['task_ids']

	# get user quries string array
	queries = request['user_queries']
	
	# get score measures
	measure = MeasureEnums.get_names()

	# ======================
	# Machine Learning Part
	# ======================
	# get the scores for simulated data
	process_update(c.CELERY_PROGRESS, 10, 'Machine Learning Analysis', is_celery)
	ml_config = request['ml_config']
	ml = MLScoring(task_ids, measure, ml_config['algorithm_id'], ml_config['method_id'], ml_config['target'])
	ml_results = ml.get_scores()

	# ======================
	# User Queries Part
	# ======================
	# get the scores for simulated data
	process_update(c.CELERY_PROGRESS, 60, 'User Queries Analysis', is_celery)
	user_q = UserQueryScoring(task_ids, queries)
	user_query_scores = user_q.get_scores()

	# fetch the analysis object by analysis_id and update it
	instance = UtilityMeasure.objects.get(
			analysis_id = request['analysis_id']
		)
	instance.ml_measure = json.dumps(MeasureEnums.get_names())
	instance.ml_results = json.dumps(list(ml_results))
	instance.query_results = json.dumps(list(user_query_scores))
	instance.status = ProcessStatus.get_code('SUCCESS')
	instance.end_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
	instance.save()

	process_update(c.CELERY_PROGRESS, 100, 'Analysis Complete', is_celery)
	return instance.analysis_id

def get_random_values(num):
	import numpy as np
	from time import time
	from numpy import random
	ul = sorted(random.randint(0,100,size = 2))
	rand_score = np.array(sorted(random.randint(ul[0], ul[1], size = num)))
	rand_score = (rand_score / float(max(rand_score))) * 99
	return list(rand_score)

def process_update(progress, percent, name, is_celery = False):
	if is_celery is True:
		current_task.update_state(
				state = progress, 
				meta = {
						c.CELERY_PRO_PERCENT: percent, 
						c.PRO_NAME: name
				}
		)


class BaseScoring(Base):
	def __init__(self, task_ids, figure_ids):
		self.task_ids = task_ids
		self.figure_ids = figure_ids

		self.task_instances = dict()
		self.job_instances = dict()

	def get_job_instances(self, task_id):
		if task_id not in self.job_instances.keys():
			self.job_instances[task_id] = Job.objects.filter(
					task_id = task_id
				)
		return self.job_instances[task_id]

	def get_task_name(self, task_id):
		# TODO, change reterive all the task instance in a transection
		if task_id not in self.task_instances.keys():
			self.task_instances[task_id] = Task.objects.get(
					task_id = task_id
				).task_name
		return self.task_instances[task_id]

	def get_job_file_path(self):
		pass

	def test_case_generate(self):
		prod = product(self.task_ids, self.figure_ids)
		return [{'task_id':t[0], 'figure_id':t[1]} for t in prod]

	def get_noises_params(self, jobs):
		params = [job.epsilon for job in jobs]
		params.append("Original")
		return params

	def construct_scoring_result(self,case,noise_params,scoring):
		case['x_vals'] = noise_params
		case['y_vals'] = scoring
		return case


class MLScoring(BaseScoring):
	def __init__(self,task_ids,measure,algorithm,method,target):
		figure_ids = measure.keys()
		BaseScoring.__init__(self, task_ids, figure_ids)

	def get_scores(self):
		results = []
		test_cases = self.test_case_generate()
		for case in test_cases:
			jobs = self.get_job_instances(case['task_id'])
			noise_params = self.get_noises_params(jobs)
			scores = get_random_values(len(noise_params))
			case = self.construct_scoring_result(case, noise_params, scores)
			results.append(case)
		return results

class UserQueryScoring(BaseScoring):
	def __init__(self,task_ids,queries):
		figure_ids = range(len(queries)+1)[1:]
		BaseScoring.__init__(self, task_ids, figure_ids)

	def get_scores(self):
		results = []
		test_cases = self.test_case_generate()
		for case in test_cases:
			jobs = self.get_job_instances(case['task_id'])
			noise_params = self.get_noises_params(jobs)
			scores = get_random_values(len(noise_params))
			case = self.construct_scoring_result(case, noise_params, scores)
			results.append(case)
		return results
