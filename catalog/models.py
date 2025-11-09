from datetime import date
from itertools import count
from wsgiref.util import request_uri
import uuid
from django.contrib.admin import display
from django.contrib.admin.utils import help_text_for_field
from django.db import models
from django.urls import reverse
from django.db.models import UniqueConstraint, Model
from django.db.models.functions import Lower
from django.utils.functional import empty
from django.conf import settings



class Genre(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Enter a book genre"
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('genre-detail', args=[str(self.id)])

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='genre_name_case_insensitive_unique',
                violation_error_message="Genre.csv already exists (case insensitive match)"

            ),
        ]

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.RESTRICT, null=True)

    summary = models.CharField(max_length=1000, help_text="bring a brief to the book")
    isbn = models.CharField('ISBN', max_length=13,
                            unique=True,
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn'
                                      '">ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text="select a genre for this book")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):
        """Create a string for the Genre. This is required to display genre in Admin."""
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = 'Genre'

class BookInstance(models.Model):
    x = 0

    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular book across whole library")
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    booklang = models.ForeignKey('BookLang', on_delete=models.RESTRICT, help_text='Book Lang', null=True)


    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text='Book availability',
    )


    def __str__(self):
        match self.status:
            case "m":
                return f"name: {self.book}\n status: {self.get_status_display()}\n we dont know when will back\n id: {self.id} "
            case "o":
                return f"name: {self.book}\n status: {self.get_status_display()}\n will coame back in {self.due_back}\n id: {self.id} "
            case "a":
                return f"name: {self.book}\n status: {self.get_status_display()}\n id: {self.id}"
            case "r":
                return f"name: {self.book}\n status: {self.get_status_display()}\n id: {self.id} "


    
    @property
    def is_overdue(self):
        """בודק אם הספר באיחור על פי תאריך ההחזרה."""
        return bool(self.due_back and date.today() > self.due_back)



    class Meta:
        ordering = ['due_back']

        def __str__(self):
            """String for representing the Model object."""
            return f'{self.id} ({self.book.title})'

class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Returns the URL to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.last_name}, {self.first_name}'

class BookLang(models.Model):

    # ToDo
    # שדה booklang מייצג את שפת הספר, עם אפשרות לבחור מתוך ערכים קבועים, ותוכנן בעתיד להיות מודל
    # נפרד לניהול דינמי דרך האדמין.

    LANGUAGE = [
        ('en', 'English'),
        ('he', 'Hebrow'),
        ('la', 'Lashon Hakodsh')
    ]

    booklang = models.CharField(
        'BookLang',
        max_length=2,
        choices=LANGUAGE,
        blank=True,
        default='he',
        help_text='Book language',
        unique=True,
    )

    def __str__(self):
        return self.get_booklang_display()
        