from django.urls import path

from . import views, csv

urlpatterns = [
    path('', views.index, name='index'),
    path('tree/<slug:tree_tag>/', views.tree, name='tree'),
    path('missing/<slug:tree_tag>/', views.missing, name='missing'),
    path('location/<slug:tree_tag>/', views.location, name='location'),
    path('maintenance/<slug:tree_tag>/', views.maintenance, name='maintenance'),
    path('map', views.map, name='map'),
    path('gis', views.gis, name='gis'),
    path('report', views.report, name='report'),
    path('tasks', views.tasks, name='tasks'),
    path('task/<slug:task_id>/', views.task, name='task'),
    path('export/', views.export, name='export'),
    path('export/trees', csv.tree_export, name='tree_export'),
    path('export/maintenance', csv.maintenance_export, name='maintenance_export'),
    path('export/tasks', csv.action_export, name='action_export')
] 