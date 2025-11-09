import copy
import datetime
import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from catalog.models import Author, Book, BookInstance, BookLang, Genre
from catalog import views as catalog_views


User = get_user_model()

if not hasattr(catalog_views, 'reverse'):
    catalog_views.reverse = reverse


def _templates_with_extra_dir(extra_dir):
    templates = copy.deepcopy(settings.TEMPLATES)
    for template in templates:
        dirs = list(template.get('DIRS', []))
        template['DIRS'] = [extra_dir] + dirs
    return templates


class TemplateDirMixin:
    """Mixin that provides a temporary template directory during tests."""

    template_overrides = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._template_dir = None
        cls._template_override = None
        if cls.template_overrides:
            cls._template_dir = tempfile.mkdtemp()
            for relative_path, content in cls.template_overrides.items():
                path = Path(cls._template_dir, relative_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            cls._template_override = override_settings(
                TEMPLATES=_templates_with_extra_dir(cls._template_dir)
            )
            cls._template_override.enable()

    @classmethod
    def tearDownClass(cls):
        if cls._template_override is not None:
            cls._template_override.disable()
        if cls._template_dir and Path(cls._template_dir).exists():
            shutil.rmtree(cls._template_dir)
        super().tearDownClass()


class AuthorListViewTest(TemplateDirMixin, TestCase):
    template_overrides = {
        'author/my_arbitrary_template_name_list.html': '{% for author in author_list %}{{ author.pk }}{% endfor %}'
    }

    @classmethod
    def setUpTestData(cls):
        for author_index in range(13):
            Author.objects.create(
                first_name=f'First {author_index}',
                last_name=f'Last {author_index}',
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('authors'))
        self.assertTemplateUsed(response, 'author/my_arbitrary_template_name_list.html')

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('authors'))
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['author_list']), 10)

    def test_lists_all_authors(self):
        response = self.client.get(reverse('authors') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['author_list']), 3)


class LoanedBookInstancesByUserListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        cls.user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        author = Author.objects.create(first_name='Dominique', last_name='Rousseau')
        genre = Genre.objects.create(name='Fantasy Adventures')
        language = BookLang.objects.create(booklang='en')
        cls.book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFGHIJKLM',
            author=author,
        )
        cls.book.genre.add(genre)

        for copy_index in range(30):
            return_date = timezone.now().date() + datetime.timedelta(days=copy_index % 5)
            borrower = cls.user1 if copy_index % 2 else cls.user2
            BookInstance.objects.create(
                book=cls.book,
                imprint='Unlikely Imprint, 2016',
                due_back=return_date,
                borrower=borrower,
                status='m',
                booklang=language,
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        initial_response = self.client.get(reverse('my-borrowed'))
        self.assertEqual(len(initial_response.context['bookinstance_list']), 0)

        for instance in BookInstance.objects.filter(borrower=self.user1)[:10]:
            instance.status = 'o'
            instance.save()

        response = self.client.get(reverse('my-borrowed'))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        for book_instance in response.context['bookinstance_list']:
            self.assertEqual(book_instance.borrower, self.user1)
            self.assertEqual(book_instance.status, 'o')

    def test_pages_ordered_by_due_date(self):
        for offset, instance in enumerate(BookInstance.objects.filter(borrower=self.user1).order_by('pk')):
            instance.status = 'o'
            instance.due_back = timezone.now().date() + datetime.timedelta(days=offset)
            instance.save()

        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))
        due_back_dates = [item.due_back for item in response.context['bookinstance_list']]
        self.assertEqual(due_back_dates, sorted(due_back_dates))
        self.assertLessEqual(len(due_back_dates), 10)


class AllLoanedBooksByUserListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.group = Group.objects.create(name='Librarians')
        cls.librarian = User.objects.create_user(username='lib_user', password='Pass!234')
        cls.regular_user = User.objects.create_user(username='reader', password='Pass!678')
        cls.librarian.groups.add(cls.group)

        author = Author.objects.create(first_name='Agatha', last_name='Christie')
        genre = Genre.objects.create(name='Mystery')
        language = BookLang.objects.create(booklang='he')
        book = Book.objects.create(
            title='Murder on the Orient Express',
            summary='Detective fiction.',
            isbn='1234567899999',
            author=author,
        )
        book.genre.add(genre)

        for index in range(5):
            BookInstance.objects.create(
                book=book,
                imprint='Vintage',
                due_back=timezone.now().date() + datetime.timedelta(days=index + 1),
                borrower=cls.librarian if index % 2 else cls.regular_user,
                status='o',
                booklang=language,
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('all-borrowed'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/allbooks/')

    def test_forbidden_for_non_librarian(self):
        self.client.login(username='reader', password='Pass!678')
        response = self.client.get(reverse('all-borrowed'))
        self.assertEqual(response.status_code, 403)

    def test_librarian_can_access(self):
        self.client.login(username='lib_user', password='Pass!234')
        response = self.client.get(reverse('all-borrowed'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/bookinstance_list_borrowed_user.html')
        queryset = response.context['bookinstance_list']
        self.assertTrue(queryset)
        for item in queryset:
            self.assertEqual(item.status, 'o')


class RenewBookInstancesViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.group = Group.objects.create(name='Librarians')
        cls.librarian = User.objects.create_user(username='librarian', password='Lib&Pwd123')
        cls.borrower = User.objects.create_user(username='borrower', password='Borrow&Pwd123')
        cls.librarian.groups.add(cls.group)

        author = Author.objects.create(first_name='Louise', last_name='Penny')
        genre = Genre.objects.create(name='Detective')
        language = BookLang.objects.create(booklang='la')
        book = Book.objects.create(
            title='Still Life',
            summary='First in the Gamache series.',
            isbn='5555555555555',
            author=author,
        )
        book.genre.add(genre)

        cls.book_instance = BookInstance.objects.create(
            book=book,
            imprint='Minotaur Books',
            due_back=datetime.date.today() + datetime.timedelta(days=10),
            borrower=cls.borrower,
            status='o',
            booklang=language,
        )
        cls.url = reverse('renew-book-librarian', kwargs={'pk': cls.book_instance.pk})

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/accounts/login/?next={self.url}')

    def test_forbidden_if_not_librarian(self):
        self.client.login(username='borrower', password='Borrow&Pwd123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_get_librarian_view(self):
        self.client.login(username='librarian', password='Lib&Pwd123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_renew_librarian.html')

    def test_initial_date_is_three_weeks_ahead(self):
        self.client.login(username='librarian', password='Lib&Pwd123')
        response = self.client.get(self.url)
        initial_date = response.context['form'].initial['renewal_date']
        expected_date = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(initial_date, expected_date)

    def test_successful_post_redirects(self):
        self.client.login(username='librarian', password='Lib&Pwd123')
        valid_date = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(self.url, {'renewal_date': valid_date})
        self.assertRedirects(response, reverse('all-borrowed'))
        self.book_instance.refresh_from_db()
        self.assertEqual(self.book_instance.due_back, valid_date)

    def test_post_invalid_past_date(self):
        self.client.login(username='librarian', password='Lib&Pwd123')
        invalid_date = datetime.date.today() - datetime.timedelta(days=1)
        response = self.client.post(self.url, {'renewal_date': invalid_date})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'renewal_date', 'Invalid date - renewal in past')

    def test_post_invalid_future_date(self):
        self.client.login(username='librarian', password='Lib&Pwd123')
        invalid_date = datetime.date.today() + datetime.timedelta(weeks=5)
        response = self.client.post(self.url, {'renewal_date': invalid_date})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'renewal_date', 'Invalid date - renewal more than 4 weeks ahead')
