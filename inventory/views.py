from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.db.models import Count
from django.urls import reverse
from django.utils import dateparse

from .models import Tree, MaintenanceEntry, ActionItem
import datetime


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
        if 'mark-as-existing' in request.POST:
            tree.gps_error_ft = None
            tree.save()
        
        elif 'mark-as-removed' in request.POST:


            new_maint = MaintenanceEntry (
                tree_id = tree.id,
                logged_by = request.user,
                remarks = '',
                overall_condition = '',
                ded_status = '',
                
                dbh = '',
                general_crown = '',
                foliage = '',
                structure = '',
                deadwood_present = '',
                
                arbotect_application = False,
                alamo_application = False,
                cambistat_application = False,
                pruned = False,
                tested_ded = False,
                removed = True,
                stump_ground = False,
            )
            
            new_maint.date = dateparse.parse_date(request.POST['removed-date'])
            if (new_maint.date is None):
                new_maint.date = datetime.date(1900, 1, 1)

            
            new_maint.save()
            
            tree.gps_error_ft = None
            tree.save()
            
        
        elif 'submit-action-item' in request.POST:
            print("new action item")
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
    
def missing(request):
    
    tree_list = Tree.objects.all().select_related()

    
    template = loader.get_template('inventory/missing.html')
    context = {
        'page_title': "Missing Trees",
        'tree_list': tree_list
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
        
        # If the tree is being marked as removed, it's no longer "missing":
        if ('removedCheckbox' in request.POST) & (t.gps_error_ft == -1):
            t.gps_error_ft = None
            t.save()
            
        
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
        
    
    template = loader.get_template('inventory/map.html')
    context = {
        'page_title': "Map",
        'tree_list': tree_list,
        'tagged_count': tagged,
        'untagged_count': untagged,
        'removed_count': removed
    }
    return HttpResponse(template.render(context, request))
    
    
def map_arbotect(request):
    removed_trees = []
    treated_trees = []
    ded_trees = []
    existing_trees = []
    
    cutoff = datetime.date(datetime.date.today().year - 2, 1, 1)
    
    for tree in Tree.objects.all().select_related():
        if tree.latitude is None:
            pass # skip trees with no location
        elif tree.is_removed_since(cutoff):
            removed_trees.append(tree)
        elif tree.is_removed():
            pass # skip removed trees
        elif tree.gps_error_ft == -1:
            pass # skip trees that are missing
        elif tree.is_arbotect_treated_since(cutoff):
            treated_trees.append(tree)
        elif tree.has_ded() :
            ded_trees.append(tree)
        else:
            existing_trees.append(tree)
            
    
    template = loader.get_template('inventory/map-arbotect.html')
    context = {
        'page_title': "Map of Arbotect Treatments",
        'removed_trees': removed_trees,
        'treated_trees': treated_trees,
        'ded_trees': ded_trees,
        'existing_trees': existing_trees,
        'cutoff_year': cutoff.year,
        'pin_colors': {
            'blue': "#4193e0",
            'green': "#0F0",
            'red': "#F00",
            'yellow': '#FD0',
            'purple': '#F0F',
            'gray': ''
        }
    }
    return HttpResponse(template.render(context, request))

class treatment_summary:
    def __init__(self): # constructor
        self.public_number = 0
        self.private_number = 0
        self.public_dbh = 0
        self.private_dbh = 0
        self.public_trees = [ ]
        self.private_trees = [ ]
    
def report(request):
    undated_removals = [ ]
    tree_removals = { }
    arbotect_treatments = { }
    alamo_treatments = { }
    
    undated_entries = MaintenanceEntry.objects.filter(date__year=1900)
    undated_removals = list(undated_entries & MaintenanceEntry.objects.filter(removed=True))
    
    for y in range(2010, datetime.date.today().year + 1):
        this_year = MaintenanceEntry.objects.filter(date__year=y)
        
        removals = list(this_year & MaintenanceEntry.objects.filter(removed=True))
        tree_removals[y] = removals
        
        if y >= 2016:
            arbotect_this_year = treatment_summary()
            
            for t in list(this_year & (MaintenanceEntry.objects.filter(arbotect_application=True))):
                
                if (t.tree.is_public):
                    arbotect_this_year.public_number += 1
                    arbotect_this_year.public_dbh += t.tree.total_dbh_in_year(y)
                    arbotect_this_year.public_trees.append(t.tree)
                else:
                    arbotect_this_year.private_number += 1
                    arbotect_this_year.private_dbh += t.tree.total_dbh_in_year(y)
                    arbotect_this_year.private_trees.append(t.tree)
            
            al_treatments = list(
                (this_year & (MaintenanceEntry.objects.filter(alamo_application=True)))
                ) 
        
            arbotect_treatments[y] = arbotect_this_year
            alamo_treatments[y] = al_treatments


    template = loader.get_template('inventory/report.html')
    context = {
        'page_title': "Summary",
        'undated_removals': undated_removals,
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


    

def about(request):
    template = loader.get_template('inventory/about.html')
    context = { }
    return HttpResponse(template.render(context, request))
    