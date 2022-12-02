from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views, csv

urlpatterns = [
    path('', views.index, name='index'),
    path('tree/<slug:tree_tag>/', views.tree, name='tree'),
	path('lot/<slug:lot_number>/', views.lot, name='lot'),
    path('missing/', views.missing, name='missing'),
	path('removed/', views.removed, name='removed'),
    path('location/<slug:tree_tag>/', views.location, name='location'),
    path('maintenance/<slug:tree_tag>/', views.maintenance, name='maintenance'),
    path('map', views.map, name='map'),
    path('map/arbotect', views.map_arbotect, name='map_arbotect'),
    path('report', views.report, name='report'),
    path('tasks', views.tasks, name='tasks'),
    path('task/<slug:task_id>/', views.task, name='task'),
    path('about/', views.about, name='about'),
    path('export/trees', csv.tree_export, name='tree_export'),
    path('export/maintenance', csv.maintenance_export, name='maintenance_export'),
    path('export/tasks', csv.action_export, name='action_export')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)