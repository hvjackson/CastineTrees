from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.db.models import Count
from django.urls import reverse
from django.utils import dateparse

from .models import Tree, MaintenanceEntry, ActionItem
from datetime import datetime
import csv

def tree_export(request):

	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="tree_list_export.csv"'

	writer = csv.writer(response)
	
	
	writer.writerow(['tag', 'old tag', 'is public', 'address', 'side of street', 'location remarks', 'property owner', 'lat', 'long'])
	
	tree_list = Tree.objects.all().select_related()

	
	for t in tree_list:
		writer.writerow([
			t.tag,
			t.old_tag,
			"Public" if t.is_public else "Private",
			t.street_address(),
			t.side_of_street,
			t.location_remarks,
			t.property_owner,
			t.latitude,
			t.longitude,
		])
			

	return response
	
def maintenance_export(request):
	
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="tree_maintenance_export.csv"'
	
	writer = csv.writer(response)
	
	
	writer.writerow([
		'tree',
		'date',
		'logged by',
		'remarks',
		'condition',
		'DED status',
		'DBH',
		'crown',
		'foliage',
		'structure',
		'deadwood',
		'arbotect',
		'alamo',
		'cambistat',
		'pruned',
		'tested DED',
		'removed',
		'stump ground'
		
	])
	
	maintenance_list = MaintenanceEntry.objects.order_by('tree__tag').select_related()
	
	
	for m in maintenance_list:
		writer.writerow([
			m.tree.tag,
			m.date,
			m.logged_by.first_name + " " + m.logged_by.last_name,
			m.remarks,
			m.get_overall_condition_display(),
			m.get_ded_status_display(),
			m.dbh,
			m.get_general_crown_display(),
			m.get_foliage_display(),
			m.get_structure_display(),
			m.get_deadwood_present_display(),
			m.arbotect_application,
			m.alamo_application,
			m.cambistat_application,
			m.pruned,
			m.tested_ded,
			m.removed,
			m.stump_ground
			
		])
			
	
	return response
	
def action_export(request):
	
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="action_item_list_export.csv"'
	
	writer = csv.writer(response)
	
	
	writer.writerow([
		'date opened',
		'tree',
		'opened by',
		'task note',
		'date closed',
		'closed by',
		'closed note'
	])
	
	task_list = ActionItem.objects.order_by('date_opened').select_related()
	
	
	for t in task_list:
		writer.writerow([
			t.date_opened,
			t.tree.tag if t.tree else "",
			t.opened_by.first_name + " " + t.opened_by.last_name,
			t.action_note,
			t.date_closed,
			(t.closed_by.first_name + " " + t.closed_by.last_name) if t.closed_by else "",
			t.closed_note
		])
			
	
	return response