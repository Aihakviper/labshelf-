from django.contrib import admin

from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'tenant', 'category', 'total_copies', 'shelf_location')
    list_filter = ('tenant', 'category')
    search_fields = ('title', 'author', 'isbn')

# Register your models here.
