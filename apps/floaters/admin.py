from django.contrib import admin
from .models import Floater

class FloaterAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_name', 'display_order', 'tier')  # fields to display in the list view
    search_fields = ('display_name',)  # fields to search by
    list_filter = ('tier',)  # fields to filter by

admin.site.register(Floater, FloaterAdmin)