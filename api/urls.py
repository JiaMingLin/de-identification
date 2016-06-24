from django.conf.urls import url
from . import views, apis

urlpatterns = [
        #url(r'^$', views.IndexView.as_view()),
]

urlpatterns += [
    url(r'^data/$', apis.DataPreview.as_view()),
    url(r'^de-identification/$', apis.TaskListCreateView.as_view()),
    url(r'^de-identification/(?P<pk>[0-9]+)/$', apis.TaskRetrieveUpdateDestroyView.as_view()),
    url(r'^de-identification/(?P<task_id>[0-9]+)/job/$', apis.JobListCreateView.as_view()),
    url(r'^de-identification/(?P<task_id>[0-9]+)/job/(?P<pk>[0-9]+)/$', apis.JobRetrieveUpdateDestroyView.as_view()),
]
