from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class AdminRecipe(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = ('name', 'author',
                    'favorites_count', 'get_ingredients_display')
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')
    exclude = ('ingredients',)

    @admin.display(description='Ингредиенты')
    def get_ingredients_display(self, obj):
        return ', '.join([
            ingredient.name for ingredient in obj.ingredients.values()])

    @admin.display(description='Добавлено в избранное')
    def favorites_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Tag)
class AdminTag(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_filter = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class AdminIngredient(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)


admin.site.register(ShoppingCart)
admin.site.register(Favorite)
