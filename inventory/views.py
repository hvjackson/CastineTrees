from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.db.models import Count
from django.urls import reverse
from django.utils import dateparse

from .models import Tree, MaintenanceEntry, ActionItem
from datetime import datetime


def index(request):
    tree_list = Tree.objects.order_by('-tag')
    
    template = loader.get_template('inventory/index.html')
    context = {
        'page_title': "Inventory",
        'tree_list': tree_list,
    }
    return HttpResponse(template.render(context, request))

def tree(request, tree_tag):
    
    tree = Tree.objects.get(tag=tree_tag)
    
    if request.method == 'POST':
        ai = ActionItem(
            date_opened = dateparse.parse_date(request.POST['date']),
            opened_by = request.user,
            action_note = request.POST['openedComment'],
            tree_id = tree.id
            )
        ai.save()
        return HttpResponseRedirect("#")
    
    template = loader.get_template('inventory/tree.html')
    context = {
        'page_title': "Tree #" + tree.tag + " Info",
        'tree': tree,
    }
    return HttpResponse(template.render(context, request))
    
def missing(request, tree_tag):
    
    tree = Tree.objects.get(tag=tree_tag)
    
    if request.method == 'POST':
        return HttpResponseRedirect("#")
    
    template = loader.get_template('inventory/missing.html')
    context = {
        'page_title': "Tree #" + tree.tag + " Info",
        'tree': tree,
    }
    return HttpResponse(template.render(context, request))

def location(request, tree_tag):
    t = Tree.objects.get(tag=tree_tag)
    
    if request.method == 'POST':
        new_lat = request.POST['lat']
        new_long = request.POST['long']
        new_err = request.POST['err']
        is_approx = ('approximate' in request.POST)
        
        t.latitude = float(new_lat)
        t.longitude = float(new_long)
        if (is_approx):
            t.gps_error_ft = 1000
        else:
            t.gps_error_ft = float(new_err)
            
        t.save()
        
        if 'referer' in request.POST:
            return HttpResponseRedirect(request.POST['referer'])
        else:
            return HttpResponseRedirect(reverse('tree', args=(t.tag,)))
        
    else:
        template = loader.get_template('inventory/location.html')
        context = {
               'tree': t,
               }
        return HttpResponse(template.render(context, request))
        
 


def maintenance(request, tree_tag):
    t = Tree.objects.get(tag=tree_tag)
    
    if request.method == 'POST':
        new_maint = MaintenanceEntry (
            tree_id = t.id,
            date = dateparse.parse_date(request.POST['date']),
            logged_by = request.user,
            remarks = request.POST['maintenance_remarks'],
            overall_condition = request.POST['overall_condition'],
            ded_status = request.POST['ded_status'],
            
            dbh = request.POST['dbh'],
            general_crown = request.POST['crown_condition'],
            foliage = request.POST['foliage_condition'],
            structure = request.POST['structure_condition'],
            deadwood_present = request.POST['deadwood_condition'],
            
            arbotect_application = 'arbotectCheckbox' in request.POST,
            alamo_application = 'alamoCheckbox' in request.POST,
            cambistat_application = 'cambistatCheckbox' in request.POST,
            pruned = 'prunedCheckbox' in request.POST,
            tested_ded = 'dedTestedCheckbox' in request.POST,
            removed = 'removedCheckbox' in request.POST,
            stump_ground = 'stumpGroundCheckbox' in request.POST, 
        )
        new_maint.save()
        
        if request.POST['actionItemText'] and not request.POST['actionItemText'].isspace():
            new_ai = ActionItem(
                date_opened = dateparse.parse_date(request.POST['date']),
                opened_by = request.user,
                action_note = request.POST['actionItemText'],   
                tree_id = t.id
            )
            new_ai.save()
        
        return HttpResponseRedirect(reverse('tree', args=(t.tag,)))
        
    else:  
        template = loader.get_template('inventory/maintenance.html')
        context = {
            'page_title': "New Log Entry",
            'tree': t
        }
        return HttpResponse(template.render(context, request))
        

    
def map(request):
    tree_list = Tree.objects.all().select_related()
    tagged = 0
    untagged = 0
    removed = 0
    
    for t in tree_list:
        if (t.latitude is not None) and (t.latitude > 0):
            tagged += 1
        elif t.is_removed():
            removed += 1
        else:
            untagged += 1
        
    
    template = loader.get_template('inventory/map-ded.html')
    context = {
        'page_title': "Map",
        'tree_list': tree_list,
        'tagged_count': tagged,
        'untagged_count': untagged,
        'removed_count': removed
    }
    return HttpResponse(template.render(context, request))

    
def report(request):
    tree_removals = { }
    arbotect_treatments = { }
    alamo_treatments = { }
    
    for y in range(2010, datetime.today().year + 1):
        this_year = MaintenanceEntry.objects.filter(date__year=y)
        
        removals = list(this_year & MaintenanceEntry.objects.filter(removed=True))
        tree_removals[y] = removals
        
        if y >= 2016:
            ar_treatments = list(
                (this_year & (MaintenanceEntry.objects.filter(arbotect_application=True)))
                ) 
            al_treatments = list(
                (this_year & (MaintenanceEntry.objects.filter(alamo_application=True)))
                ) 
        
            arbotect_treatments[y] = ar_treatments
            alamo_treatments[y] = al_treatments


    template = loader.get_template('inventory/report.html')
    context = {
        'page_title': "Summary",
        'tree_removals': tree_removals,
        'arbotect_treatments': arbotect_treatments,
        'alamo_treatments': alamo_treatments
    }
    return HttpResponse(template.render(context, request))
    
def tasks(request):    
    
    if request.method == 'POST':
        ai = ActionItem(
            date_opened = dateparse.parse_date(request.POST['date']),
            opened_by = request.user,
            action_note = request.POST['openedComment'],
            tree_id = int(request.POST['targetTree']) if request.POST['targetTree'] else None
        )
        ai.save()
        return HttpResponseRedirect("#")
        
    open_action_items = ActionItem.objects.all().filter(date_closed__isnull = True)
    closed_action_items = ActionItem.objects.all().filter(date_closed__isnull = False)
    trees = Tree.objects.all()
    
    template = loader.get_template('inventory/tasks.html')
    context = {
        'page_title': "Action Items",
           'open_action_items': open_action_items,
           'closed_action_items': closed_action_items,
           'trees': trees
    }
    return HttpResponse(template.render(context, request))
    
    
def task(request, task_id):    
    action_item = ActionItem.objects.get(id=task_id)
        
    if request.method == 'POST':
        action_item.date_closed = dateparse.parse_date(request.POST['date'])
        action_item.closed_by = request.user
        action_item.closed_note = request.POST['closedComment']

        action_item.save()

        return HttpResponseRedirect(reverse('tasks')) 
        
    else:
        template = loader.get_template('inventory/task.html')
        context = {
            'page_title': "Action Item",
               'action_item': action_item,
        }
        return HttpResponse(template.render(context, request))


def gis(request):
    template = loader.get_template('inventory/gis.html')
    context = { }
    return HttpResponse(template.render(context, request))
    

def export(request):
    template = loader.get_template('inventory/export.html')
    context = { }
    return HttpResponse(template.render(context, request))
    