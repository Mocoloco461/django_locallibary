from django.contrib import admin
from django.db.models import ManyToManyRel
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Author, Genre, Book, BookInstance, BookLang



class AuthorResource(resources.ModelResource):
    class Meta:
        model = Author

class GenreResource(resources.ModelResource):
    class Meta:
        model = Genre

class BookResource(resources.ModelResource):
    class Meta:
        model = Book

class BookInstanceResource(resources.ModelResource):
    class Meta:
        model = BookInstance

class BookLangResource(resources.ModelResource):
    class Meta:
        model = BookLang




class BookInline(admin.TabularInline):
    model = Book
    extra = 0

@admin.register(Author)
class AuthorAdmin(ImportExportModelAdmin):
    fields = [('first_name', 'last_name'), ('date_of_birth', 'date_of_death')]
    list_display = ('id','first_name', 'last_name', 'date_of_birth', 'date_of_death',)
    resource_class = AuthorResource

    inlines = [BookInline]


@admin.register(Genre)
class GenreAdmin(ImportExportModelAdmin):
    list_display = ['id','name']
    resource_class = GenreResource


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0

@admin.register(Book)
class BookAdmin(ImportExportModelAdmin):
    list_display = ('id','title', 'author', 'isbn', 'display_genre',) #genre - NEED TO FIX!
    resource_class = BookResource

    inlines = [BooksInstanceInline]


@admin.register(BookInstance)
class BookInstanceAdmin(ImportExportModelAdmin):
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {'fields': ('book', 'imprint', 'id')}),
        ('Availability', {'fields': ('status', 'due_back', 'borrower')}),
    )
    resource_class = BookInstanceResource

@admin.register(BookLang)
class BookLangAdmin(ImportExportModelAdmin):
    list_display = ['id', 'booklang']
    resource_class = BookLangResource