from django.db import models
from django.contrib.auth.models import User
import html
from datetime import datetime, timedelta

class TaxLot(models.Model):
	class Meta:
		ordering = ['lot_number']
	
	lot_number = models.CharField(max_length=10, primary_key=True)
	lot_address = models.CharField(max_length=50)
	owner_name = models.CharField(max_length=50)

	def __str__(self):
		return self.lot_number + " " + self.lot_address
	
	


class Tree(models.Model):
	class Meta:
		ordering = ['tag']
	
	tag = models.CharField(max_length=8, blank = True)
	old_tag = models.CharField(max_length=8, blank = True)
	is_public = models.BooleanField()
	latitude = models.FloatField(blank = True, null = True)
	longitude = models.FloatField(blank = True, null = True)
	gps_error_ft = models.FloatField(blank = True, null = True)
	street_number = models.IntegerField(blank = True, null = True)
	street_name = models.CharField(max_length = 50, blank = True, null = True)
	side_of_street = models.CharField(
		max_length = 1,
		choices=[('N', 'North'), ('S', 'South'), ('E', 'East'), ('W', 'West')],
		blank = True,
	)
	location_remarks = models.CharField(max_length=100, blank = True)
	tax_lot = models.ForeignKey(TaxLot, on_delete=models.PROTECT, null = True, blank = True)
	
	def __str__(self):
		return self.tag
		
	def street_address(self):
		if (self.street_number):
			return str(self.street_number) + " " + self.street_name
		else:
			return self.street_name
		
	def is_removed(self):
		return self.maintenanceentry_set.filter(removed=True).count() > 0
		
	def is_removed_since(self, cutoff):
		''' Returns True if this tree was removed on or after the specified cutoff '''
		
		obs = self.maintenanceentry_set.all()
	
		for o in obs:
			if o.date >= cutoff and o.removed:
				return True
		
		return False

			
	def is_quality_tree(self):
		return tree_condition(self) == "Excellent"
	
	def tree_condition(self):
		obs = self.maintenanceentry_set.order_by('-date')
		
		for o in obs:
			if o.overall_condition is not None:
				return o.get_overall_condition_display()
		
		return None
	
	def ded_status(self):
		obs = self.maintenanceentry_set.order_by('-date')
	
		for o in obs:
			if o.ded_status is not None:
				return o.get_ded_status_display()
		return None	

		
			
	def has_ded(self):
		obs = self.maintenanceentry_set.order_by('-date')
	
		for o in obs:
			if o.ded_status is not None:
				return o.ded_status == "C" or o.ded_status == "S"
		
		return False	
		
	def most_recent_ded_treatment(self):
		maint = self.maintenanceentry_set.order_by('-date')
	
		for m in maint:
			if m.arbotect_application or m.alamo_application:
				return m.date
	
		return None	
	
	def is_arbotect_treated_since(self, cutoff):
		''' Returns True if this tree was treated on or after the specified cutoff '''
	
		obs = self.maintenanceentry_set.all()
	
		for o in obs:
			if o.date >= cutoff and o.arbotect_application:
				return True
	
		return False
	
	def total_dbh_in_year(self, year: int) -> int:
		""" Gets the total DBH (adding up stems if necessary) in the year, or an earlier year if necessary """
		
		obs = self.maintenanceentry_set.order_by('-date')

		for o in obs:
			if o.date.year > year:
				continue;
			if o.dbh:
				parts = o.dbh.replace(', ', ',').split(',')
				total = 0
						
				for stem in parts:
					total += int(stem)

				return total
		
		return 0


		
        
class MaintenanceEntry(models.Model):
	class Meta:
		ordering = ['tree', 'date']
        
	# Basic log entry details
	tree = models.ForeignKey(Tree, on_delete=models.CASCADE)
	date = models.DateField()
	logged_by = models.ForeignKey(User, on_delete= models.PROTECT, related_name="logged_by_user")
	remarks = models.CharField(max_length = 200, blank = True)
        
	tree_condition_choices = [('Q', 'Excellent'), ('N', 'Good'), ('W', 'Poor'), ('D', 'Dead'), ('M', 'Missing')]
	detail_quality_choices = [('E', 'Excellent'), ('VG', 'Very Good'), ('G', 'Good'), ('F', 'Fair'), ('P', 'Poor'), ('VP', 'Very Poor')]
	ded_choices = [('N', 'None apparent'), ('S', 'Suspected'), ('C', 'Confirmed')]
        
	# General observations
	overall_condition = models.CharField(max_length = 1, choices = tree_condition_choices, blank = True)
	ded_status =  models.CharField(max_length = 1, choices = ded_choices, blank = True)
        
	# Detailed inspection
	dbh = models.CharField(max_length=15, blank = True)
	general_crown = models.CharField(max_length = 2, choices = detail_quality_choices, blank = True)
	foliage = models.CharField(max_length = 2, choices = detail_quality_choices, blank = True)
	structure = models.CharField(max_length = 2, choices = detail_quality_choices, blank = True)
	deadwood_present = models.CharField(max_length = 2, choices = detail_quality_choices, blank = True)

	# Maintenance items
	arbotect_application = models.BooleanField(default=False)
	alamo_application = models.BooleanField(default=False)
	cambistat_application = models.BooleanField(default=False)
	pruned = models.BooleanField(default=False)
	tested_ded = models.BooleanField(default=False)
	removed = models.BooleanField(default=False)
	stump_ground = models.BooleanField(default=False)
    
	def maintenance_actions(self):
		actions = list()
            
		if (self.arbotect_application):
			actions.append("Arbotect")
		if (self.pruned):
			actions.append("Pruned")
		if (self.alamo_application):
			actions.append("Alamo")
		if (self.cambistat_application):
			actions.append("Cambistat")
		if (self.tested_ded):
			actions.append("Tested DED")
		if (self.removed):
			actions.append("Removed")
		if (self.stump_ground):
			actions.append("Stump ground")
        
		return ', '.join(actions)
        
	def __str__(self):
		return "Tree # " + self.tree.tag + " log entry " + self.date.strftime("%b %Y")


		
	
class ActionItem(models.Model):
	
	tree = models.ForeignKey(Tree, on_delete=models.CASCADE, null = True, blank = True)
	
	date_opened = models.DateField()
	opened_by = models.ForeignKey(User, on_delete= models.PROTECT, related_name="opened_by_user")
	action_note = models.CharField(max_length = 200, blank = True)
	
	date_closed = models.DateField(null = True, blank = True)
	closed_by = models.ForeignKey(User, on_delete= models.PROTECT, null = True, blank = True, related_name="closed_by_user")
	closed_note = models.CharField(max_length = 200, blank = True)

		
	def is_open(self):
		return self.date_closed is None
	