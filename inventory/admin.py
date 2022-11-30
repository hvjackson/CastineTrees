from django.contrib import admin

# Register your models here.

from .models import Tree
from .models import MaintenanceEntry
from .models import ActionItem
from .models import TaxLot

admin.site.register(Tree)
admin.site.register(MaintenanceEntry)
admin.site.register(ActionItem)
admin.site.register(TaxLot)



admin.site.site_title = "Castine Trees Admin"
admin.site.site_header = "Castine Trees Admin"
admin.site.index_title = "Castine Trees Admin"
admin.site.site_url = '/inventory'