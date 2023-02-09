from django.contrib import admin

from django.template.defaultfilters import truncatechars

from .models import Customer, Post, PostComment, Cart

# Register your models here.


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'first_name', 'last_name', 'description', 'user_class']
    autocomplete_fields = ['user']
    search_fields = ['user__first_name', 'user__last_name']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'book_name', 'author', 'get_description', 'bought_date', 'unit_price', 'book_count', 'wishlisted', 'post_type', 'post_rating', 'posted_on']
    autocomplete_fields = ['user']
    search_fields = ['book_name']

    def get_description(self, obj):
        return truncatechars(obj.description, 50)
        # return obj.description[:35]



@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post_id', 'comment_body', 'created_date']
    autocomplete_fields = ['user', 'post']

# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display = ['id', 'items']