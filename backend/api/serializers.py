from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.constants import AMOUNT_MAX, AMOUNT_MIN
from recipes.constants import TIME_MAX, TIME_MIN
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, instance):
        user = self.context.get('request').user
        return user.is_authenticated and user.follower.filter(
            author=instance).exists()


class UserCreateCustomSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients',
        required=True,
        many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserSerializer()
    tags = TagSerializer(many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, instance):
        request = self.context.get('request')
        return (request.user.is_authenticated and instance.favorites.filter(
            user=request.user).exists())

    def get_is_in_shopping_cart(self, instance):
        request = self.context.get('request')
        return (
            request.user.is_authenticated and instance.shopping_list.filter(
                user=request.user).exists()
        )


class IngredientCreateInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        write_only=True,
        min_value=AMOUNT_MIN,
        max_value=AMOUNT_MAX
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = IngredientCreateInRecipeSerializer(
        many=True,
        write_only=True
    )
    image = Base64ImageField(allow_null=True, allow_empty_file=True)
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    cooking_time = serializers.IntegerField(
        min_value=TIME_MIN,
        max_value=TIME_MAX
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate(self, data):
        if not data.get('name'):
            raise serializers.ValidationError('Обязательное поле')
        if not data.get('text'):
            raise serializers.ValidationError('Обязательное поле')
        if not data.get('cooking_time'):
            raise serializers.ValidationError('Обязательное поле')
        if not data.get('image'):
            raise serializers.ValidationError('Обязательное поле')
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Добавьте ингредиенты.'}
            )
        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Добавьте хотя бы один тег.'}
            )
        ingredients_count = [ingredient['id'] for ingredient in ingredients]
        if len(ingredients_count) != len(set(ingredients_count)):
            raise serializers.ValidationError(
                {'ingredients': 'Нельзя добавлять одинаковые ингредиенты.'}
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {'tags': 'Нельзя добавлять одинаковые теги.'}
            )
        for ingredient_id in ingredients_count:
            try:
                Ingredient.objects.get(pk=ingredient_id)
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    {'ingredients': 'Ингредиент не существует.'})
        return super().validate(data)

    @staticmethod
    def recipe_ingredient_create(ingredients_data, recipe):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    ingredient_id=ingredient['id'],
                    amount=ingredient['amount'],
                    recipe=recipe
                ) for ingredient in ingredients_data
            ]
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        validated_data['author'] = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.recipe_ingredient_create(ingredients_data=ingredients_data,
                                      recipe=recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.recipe_ingredient_create(ingredients_data, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance, context=context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'cooking_time',
            'image'
        )


class FollowSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes',
                                               'recipes_count')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_recipes(self, instance):
        request = self.context['request']
        recipes_limit = request.GET.get('recipes_limit')
        recipes = instance.recipes.all()
        try:
            if recipes_limit:
                recipes = recipes[:int(recipes_limit)]
        except ValueError:
            raise ValueError('Некорректное значение')
        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, data):
        return data.recipes.count()


class FollowCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, data):
        user = data['user']
        author = data['author']
        if user == author:
            raise serializers.ValidationError(
                'Подписаться на себя невозможно.'
            )
        if Follow.objects.filter(
                user=user, author=author
        ).exists():
            raise serializers.ValidationError(
                'Повторная подписка на автора невозможна.'
            )
        return data

    def to_representation(self, instance):
        return FollowSerializer(
            instance=instance.author,
            context=self.context).data


class CommonCreateSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe, context=self.context).data

    def validate_unique_together(self, attrs, serializer):
        queryset = self.Meta.model.objects.all()
        fields = self.Meta.fields
        message = self.Meta.message
        validator = UniqueTogetherValidator(
            queryset=queryset,
            fields=fields,
            message=message
        )
        validator.set_context(serializer)
        validator(attrs)


class FavoriteSerializer(CommonCreateSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        message = 'Рецепт в избранном.'

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if Favorite.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError('Такой рецепт уже добавлен.')
        return super().validate(data)


class ShoppingCartSerializer(CommonCreateSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        message = 'Рецепт в списке покупок.'

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if user.shopping_list.filter(recipe=recipe).exists():
            raise serializers.ValidationError('Такой рецепт уже добавлен.')
        return super().validate(data)
