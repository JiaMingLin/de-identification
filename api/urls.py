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
    url(r'^de-identification/proc/$', apis.ProcessControlListView.as_view()),
    url(r'^de-identification/proc/(?P<proc_id>.*)$', apis.ProcessControlView.as_view()),
    url(r'^de-identification/utility/(?P<req_type>\D+)/$', apis.UtilityMeasureHTMLListView.as_view()),
    url(r'^de-identification/utility/$', apis.UtilityMeasureListCreateView.as_view()),
    url(r'^de-identification/utility/(?P<analysis_id>[0-9]+)/$', apis.UtilityMeasureRetrieveUpdateDestroyView.as_view()),
]