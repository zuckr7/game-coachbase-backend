from django.contrib import admin
from django.db.models import Q
from .models import LevelDoc, UserProgressDoc
from .cb import CB

@admin.register(LevelDoc)
class LevelDocAdmin(admin.ModelAdmin):
    list_display = ('level_id','name','difficulty')

@admin.register(UserProgressDoc)
class UserProgressDocAdmin(admin.ModelAdmin):
    list_display   = ('user_id','username','points','coins','passedLevel')
    search_fields  = ('username',)   # теперь будет работать, т.к. есть реальное поле
    readonly_fields = ('user_id',)   # если нужно
    def has_add_permission(self, request):
        return False
