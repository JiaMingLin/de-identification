import json
from .models import Task, Job, UtilityMeasure
from .serializers import TaskSerializer, JobSerializer, UtilityMeasureSerializer
from common.base import *
from common.data_utilities import DataUtils
from common.enums import *
from celery.result import AsyncResult
from celery.task.control import revoke, inspect

from datetime import datetime
from django.http import Http404
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
import common.constant as c

"""
The De-Identification Index page
	1. Listing
	2. Creating
	3. Deleting
	4. Retrieving
"""

class TaskListCreateView(APIView):

	def get(self, request, format = None):
		tasks = Task.objects.all()
		serializer = TaskSerializer(tasks, many = True)
		return Response(serializer.data)

	def post(self, request, format = None):
		"""
		Request
		=================================
		task_name:
		file_path:
			The original file path.
		selected_attrs:
			The user specified attributes
			[{'attr_name':'A', 'dtype':'C'}, 
			 {'attr_name':'B','dtype':'D'},...]
		Response
		=================================
		"""
		data = request.data
		data['opted_cluster'] = ''
		data['white_list'] = ''
		serializer = TaskSerializer(data=data)
		
		if(serializer.is_valid()):
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskRetrieveUpdateDestroyView(APIView):

	def get(self, request, pk, format = None):
		task = get_object_or_404(Task, pk = pk)
		import ast
		task.selected_attrs = ast.literal_eval(task.selected_attrs)
		task.opted_cluster = ast.literal_eval(task.opted_cluster)
		task.white_list = ast.literal_eval(task.white_list)
		serializer = TaskSerializer(task)
		return Response(serializer.data)

	def put(self, request, pk, format=None):
		task = get_object_or_404(Task, pk = pk)
		serializer = TaskSerializer(task, data=request.data)
		task.selected_attrs = ast.literal_eval(task.selected_attrs)
		task.opted_cluster = ast.literal_eval(task.opted_cluster)
		task.white_list = request.data['white_list']
		serializer = TaskSerializer(task, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, pk, format=None):
		task = get_object_or_404(Task, pk = pk)
		task.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

class JobListCreateView(APIView):
	def get(self, request, task_id, format = None):
		jobs = get_list_or_404(Job, task_id = task_id)
		serializer = JobSerializer(jobs, many = True)
		return Response(serializer.data)

	def post(self, request, task_id):
		data = request.data
		data['task_id'] = task_id
		serializer = JobSerializer(data = data)
		if(serializer.is_valid()):
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobRetrieveUpdateDestroyView(APIView):

	def get(self, request, pk, task_id, format = None):
		job = get_object_or_404(Job, pk = pk)
		import ast
		job.statistics_err = ast.literal_eval(job.statistics_err) if len(job.statistics_err) > 0 else ''
		serializer = JobSerializer(job)
		return Response(serializer.data)


class DataPreview(APIView):
	def post(self, request, format = None):
		"""
		The Request contains data path
		1. using data utilities to preview the given data
		2. retrieves all the fields and the first 5 data.
		3. return the fields and sample data to client
		"""
		req = request.data
		data = DataUtils(str(req['file_path']))
		preview_df = data.data_preview()
		rows = [row[1].tolist() for row in preview_df.iterrows()]
		col_names = list(preview_df.columns.values)
		result = dict({
			'rows':rows,
			'col_names':col_names
		})
		result = json.dumps(result)
		return Response(result, status = status.HTTP_200_OK)


class ProcessControlListView(APIView):
	def post(self, request, format = None):
		i = inspect()
		result = 'Fail'
		key = 'proc_ids'
		req_obj = request.data

		if key in req_obj.keys():
			ids = req_obj[key]
			#procs = i.query_task(ids = ['2d45fae0-9b4d-4c03-93c7-3388df9b30e1', '98c36c8b-f4b7-435d-a716-3605625ca9dc', '7c43315f-4629-4f87-8361-bca48c5c9d71', '33ecc028-bd0c-4672-8e97-8b9db9653960'])
			#procs = i.query_task()
			procs = i.revoked()
		else:
			result = 'There is no key "%s" in request body.' % key

		result = json.dumps(result)
		return Response(result, status.HTTP_200_OK)

class ProcessControlView(APIView):

	def get(self, request, proc_id, format = None):
		result = dict()
		proc = AsyncResult(proc_id)

		try:
			data = proc.result
			result[c.CELERY_PRO_PERCENT] = data[c.CELERY_PRO_PERCENT]
			result[c.PRO_NAME] = data[c.PRO_NAME]
		except:
			print "process exit"

		result[c.CELERY_STATUS] = ProcessStatus.get_code(str(proc.status).upper())

		return Response(result, status = status.HTTP_200_OK)

	def delete(self, request, proc_id, format = None):
		data = 'INIT'
		instance = None
		try:
			revoke(proc_id, terminate=True)
			instance = get_object_or_404(Job, proc_id = proc_id)
		except:
			instance = get_object_or_404(Task, proc_id = proc_id)

		instance.status = ProcessStatus.get_code('REVOKED')
		instance.end_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
		instance.save()
		result = dict({
				c.CELERY_STATUS: ProcessStatus.get_code('REVOKED')
			})
		return Response(result, status = status.HTTP_200_OK)

class UtilityMeasureHTMLListView(APIView):
	def get(self, request, req_type, format = None):
		result = 'INIT'
		if req_type == 'v_methods':
			result = EvalMethodEnums.get_names()
		elif req_type == 'algorithms':
			result = MLAlgorithmEnums.get_names()
		else:
			result = json.dumps('Query Type not Found')

		return Response(result, status = status.HTTP_200_OK)

class UtilityMeasureListCreateView(APIView):
	def get(self, request, format = None):
		result = 'INIT'
		objs = UtilityMeasure.objects.all()
		serializer = UtilityMeasureSerializer(objs, many = True)
		return Response(serializer.data, status = status.HTTP_200_OK)

	def post(self, request, format = None):
		result = 'INIT'
	
		data = request.data
		data["ml_measure"] = ''
		data["ml_result"] = ''
		data["query_results"] = ''
		serializer = UtilityMeasureSerializer(data=data)
		
		if(serializer.is_valid()):
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UtilityMeasureRetrieveUpdateDestroyView(APIView):
	def get(self, request, analysis_id, format = None):
		result = 'INIT'
		obj = get_object_or_404(UtilityMeasure, pk = analysis_id)
		import ast
		obj.task_ids = ast.literal_eval(obj.task_ids)
		obj.ml_config = ast.literal_eval(obj.ml_config)
		obj.ml_measure = ast.literal_eval(obj.ml_measure)
		obj.ml_result = ast.literal_eval(obj.ml_result)
		obj.user_queries = ast.literal_eval(obj.user_queries)
		obj.query_results = ast.literal_eval(obj.query_results)

		serializer = UtilityMeasureSerializer(obj)

		return Response(serializer.data, status = status.HTTP_200_OK)

	def put(self, request, analysis_id, format=None):
		obj = get_object_or_404(UtilityMeasure, pk = pk)
		import ast
		obj.task_ids = ast.literal_eval(obj.task_ids)
		obj.ml_config = ast.literal_eval(obj.ml_config)
		obj.user_queries = ast.literal_eval(obj.user_queries)

		serializer = UtilityMeasureSerializer(task, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, analysis_id, format=None):
		obj = get_object_or_404(UtilityMeasure, pk = pk)
		obj.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)