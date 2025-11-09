import datetime

from django.test import TestCase

from catalog.models import Author, Book, BookInstance, BookLang, Genre

class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # יצירת אובייקט שלא משתנה במהלך הבדיקות
        Author.objects.create(first_name='Big', last_name='Bob')

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEqual(field_label, 'first name')

    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEqual(max_length, 100)

    def test_last_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('last_name').verbose_name
        self.assertEqual(field_label, 'last name')

    def test_last_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('last_name').max_length
        self.assertEqual(max_length, 100)

    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEqual(field_label, 'died')

    def test_date_of_birth_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_birth').verbose_name
        self.assertEqual(field_label, 'date of birth')

    
    def test_object_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=1)
        expected_object_name = f'{author.last_name}, {author.first_name}'
        self.assertEqual(str(author), expected_object_name)

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        # תיכשל גם אם ה־URLConf לא מוגדר
        self.assertEqual(author.get_absolute_url(), '/catalog/author/1')


class GenreModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Genre.objects.create(name='Epic Fantasy')

    def test_name_label(self):
        genre = Genre.objects.get(id=1)
        self.assertEqual(genre._meta.get_field('name').verbose_name, 'name')

    def test_name_help_text(self):
        genre = Genre.objects.get(id=1)
        self.assertEqual(genre._meta.get_field('name').help_text, 'Enter a book genre')

    def test_name_unique_case_insensitive(self):
        # בדיקה שמגבלה קיימת - הוספה של Genre בעל שם זהה (הבדל אותיות) תיכשל
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            Genre.objects.create(name='epic fantasy')


class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(first_name='Jane', last_name='Austen')
        cls.genre_one = Genre.objects.create(name='Classic Fiction')
        cls.genre_two = Genre.objects.create(name='Romance')
        cls.genre_three = Genre.objects.create(name='Satire')
        cls.genre_four = Genre.objects.create(name='Drama')

        cls.book = Book.objects.create(
            title='Pride and Prejudice',
            author=cls.author,
            summary='A classic novel.',
            isbn='1234567890123',
        )
        cls.book.genre.set([cls.genre_one, cls.genre_two, cls.genre_three, cls.genre_four])

    def test_title_label(self):
        self.assertEqual(self.book._meta.get_field('title').verbose_name, 'title')

    def test_isbn_label(self):
        self.assertEqual(self.book._meta.get_field('isbn').verbose_name, 'ISBN')

    def test_get_absolute_url(self):
        expected = f'/catalog/book/{self.book.id}'
        self.assertEqual(self.book.get_absolute_url(), expected)

    def test_display_genre_with_more_than_three_items(self):
        self.assertEqual(self.book.display_genre(), 'Classic Fiction, Romance, Satire')


class BookInstanceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = Author.objects.create(first_name='George', last_name='Orwell')
        genre = Genre.objects.create(name='Dystopia')
        cls.language = BookLang.objects.create(booklang='en')
        cls.book = Book.objects.create(
            title='1984',
            author=author,
            summary='Big Brother is watching you.',
            isbn='9876543210123',
        )
        cls.book.genre.add(genre)

    def _create_instance(self, **kwargs):
        defaults = {
            'book': self.book,
            'imprint': 'First edition',
            'booklang': self.language,
        }
        defaults.update(kwargs)
        return BookInstance.objects.create(**defaults)

    def test_string_representation_includes_status(self):
        instance = self._create_instance(status='o', due_back=datetime.date.today())
        self.assertIn('On loan', str(instance))
        self.assertIn(str(instance.book), str(instance))

    def test_is_overdue_true_when_due_back_in_past(self):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        instance = self._create_instance(status='o', due_back=yesterday)
        self.assertTrue(instance.is_overdue)

    def test_is_overdue_false_when_due_back_future(self):
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        instance = self._create_instance(status='o', due_back=tomorrow)
        self.assertFalse(instance.is_overdue)


class BookLangModelTest(TestCase):
    def test_string_representation(self):
        language = BookLang.objects.create(booklang='la')
        self.assertEqual(str(language), 'Lashon Hakodsh')
