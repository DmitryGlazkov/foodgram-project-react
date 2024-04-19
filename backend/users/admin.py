from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from recipes.models import Recipe

from .models import Follow

User = get_user_model()


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'get_follow_count',
        'get_recipe_count'
    )
    list_editable = (
        'email',
        'first_name',
        'last_name'
    )
    search_fields = (
        'email',
        'username'
    )
    list_filter = (
        'email',
        'username'
    )

    @admin.display(description='Количество подписчиков')
    def get_follow_count(self, obj):
        return Follow.objects.filter(user=obj).count()

    @admin.display(description='Количество рецептов')
    def get_recipe_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


admin.site.register(Follow)
admin.site.unregister(Group)
admin.site.empty_value_display = 'Не задано'
