from django.contrib import admin, messages
from django.core.management import call_command
from django.urls import path
from django.shortcuts import redirect

from .models import LevelDoc, UserProgressDoc, UserDoc


@admin.register(LevelDoc)
class LevelDocAdmin(admin.ModelAdmin):
    list_display           = ('name','level_id', 'difficulty')
    search_fields          = ('name',)
    list_filter            = ('difficulty',)
    change_list_template   = "admin/dashboard/leveldoc_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                'import-cb/',
                self.admin_site.admin_view(self.import_from_couchbase),
                name='dashboard_leveldoc_import_cb'
            ),
        ]
        return custom + urls

    def import_from_couchbase(self, request):
        try:
            call_command('import_cb')
            self.message_user(request,
                              "Levels & Progress успешно импортированы из Couchbase!",
                              level=messages.SUCCESS)
        except Exception as e:
            self.message_user(request,
                              f"Ошибка при импорте: {e}",
                              level=messages.ERROR)
        return redirect('..')


@admin.register(UserProgressDoc)
class UserProgressDocAdmin(admin.ModelAdmin):
    list_display           = ('username','user_id','points','coins','passedLevel')
    search_fields          = ('username',)
    readonly_fields        = ('username',)
    has_add_permission     = lambda self, req: False
    change_list_template   = "admin/dashboard/userprogressdoc_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                'import-cb/',
                self.admin_site.admin_view(self.import_from_couchbase),
                name='dashboard_userprogressdoc_import_cb'
            ),
        ]
        return custom + urls

    def import_from_couchbase(self, request):
        try:
            call_command('import_cb')
            self.message_user(request,
                              "Levels & Progress успешно импортированы из Couchbase!",
                              level=messages.SUCCESS)
        except Exception as e:
            self.message_user(request,
                              f"Ошибка при импорте: {e}",
                              level=messages.ERROR)
        return redirect('..')


@admin.register(UserDoc)
class UserDocAdmin(admin.ModelAdmin):
    list_display           = ('username','user_id','vk_id','version','created_at')
    search_fields          = ('username','vk_id')
    readonly_fields        = ('user_id','created_at')
    list_filter            = ('vk_id',)
    ordering               = ('-created_at',)
    change_list_template   = "admin/dashboard/userdoc_changelist.html"

    # отключаем создание через админку (пароли хранятся в Couchbase)
    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                'import-cb/',
                self.admin_site.admin_view(self.import_from_couchbase),
                name='dashboard_userdoc_import_cb'
            ),
        ]
        return custom + urls

    def import_from_couchbase(self, request):
        try:
            call_command('import_cb')
            self.message_user(request,
                              "Все пользователи успешно импортированы из Couchbase!",
                              level=messages.SUCCESS)
        except Exception as e:
            self.message_user(request,
                              f"Ошибка при импорте: {e}",
                              level=messages.ERROR)
        return redirect('..')
