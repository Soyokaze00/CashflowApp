from django.contrib import admin
from  .models import Parent, Child, Cost

# Register your models here.


class ParentAdmin(admin.ModelAdmin):
    list_display=('id', 'username', 'password')


class ChildAdmin(admin.ModelAdmin):
    list_display=('id', 'username', 'password', 'parent')


class CostAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'cate_choices', 'type', 'date', 'child__username', 'child__parent__username') 
    list_filter = ('child__username', 'type', 'cate_choices')  
    search_fields = ('cate_choices', 'description', 'child__username', 'id')  
    ordering = ('-date',) 

admin.site.register(Parent, ParentAdmin)
admin.site.register(Child, ChildAdmin)
admin.site.register(Cost, CostAdmin)