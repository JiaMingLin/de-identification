import json
from .models import Task, Job
from .serializers import TaskSerializer, JobSerializer
from common.data_utilities import DataUtils
from django.http import Http404
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

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
        The post request must contains data path and fields descriptions.
        1. passing path, fields to data utilities.
        2. data utilities returns the data model, dependency graph, junction tree
        3. save the entities to database.
        4. return the data models to client
        """
        serializer = TaskSerializer(data=request.data)
        if(serializer.is_valid()):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskRetrieveUpdateDestroyView(APIView):

    def get(self, request, pk, format = None):
        task = get_object_or_404(Task, pk = pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

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
        preview = data.data_preview(format = 'json')
        return Response(preview, status = status.HTTP_200_OK)