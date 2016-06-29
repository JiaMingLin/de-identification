from rest_framework import serializers
from .models import Task, Job

class TaskSerializer(serializers.ModelSerializer):
	class Meta:
		model = Task
		field = ('task_id', 'task_name', 'selected_attrs', 'data_path', 'jtree_strct', 'dep_graph', 'start_time', 'end_time', 'status')



class JobSerializer(serializers.ModelSerializer):
	class Meta:
		model = Job
		field = ('dp_id', 'task_id', 'privacy_level', 'epsilon', 'status', 'synthetic_path', 'statistics_err', 'log_path', 'start_time', 'end_time')
