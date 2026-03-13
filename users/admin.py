from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "get_avatar", "selected_theme", "subscribed_to_important_news", "is_staff")
    list_filter = ("selected_theme", "subscribed_to_important_news", "is_staff", "is_active")
    
    # Добавление новых полей в формы редактирования
    fieldsets = UserAdmin.fieldsets + (
        ("Дополнительная информация", {
            "fields": ("avatar", "selected_theme", "subscribed_to_important_news")
        }),
    )
    
    # Добавление новых полей в форму создания
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Дополнительная информация", {
            "fields": ("email", "avatar", "selected_theme", "subscribed_to_important_news")
        }),
    )

    # Метод для отображения миниатюры аватара
    def get_avatar(self, obj):
        if obj.avatar:
            return mark_safe(f'<img src="{obj.avatar.url}" width="35" height="35" style="border-radius:50%; object-fit:cover;"/>')
        return "———"
    get_avatar.short_description = "Аватар"
