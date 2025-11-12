from django.http import HttpResponseRedirect
from catalog.forms import RenewBookForm
import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.template.defaultfilters import title
from django.views import generic
from .admin import BookInline
from .models import Book, Author, BookInstance, Genre
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin



def index(request):

    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()
    num_genre = Genre.objects.count()

    num_visits = request.session.get('num_visits', 0)
    num_visits += 1
    request.session['num_visits'] = num_visits
    username_visits = request.session.get('username', "User")

    # Handle book search
    search_results = None
    if request.method == 'POST':
        book_name = request.POST.get('book_name', '')
        if book_name:
            # Search for books containing the search term (case-insensitive)
            search_results = Book.objects.filter(title__icontains=book_name)


    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genre': num_genre,
        'search_results': search_results,
        'num_visits' : num_visits,
        'username_visits' : username_visits
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10
    context_object_name  = 'book_list'   # שם משלכם לרשימה כמשתנה תבנית
    queryset = Book.objects.all()#filter(title__contains='ספר')[:5] # קבל 5 ספרים המכילים את הכותרת 'war'
    template_name = 'books/my_arbitrary_template_name_list.html'  # ציינו שם/מיקום תבנית משלכם

class BookDetailView(generic.DetailView):
    model = Book

    def book_detail_view(request, primary_key):
        book = get_object_or_404(Book, pk=primary_key)
        return render(request, 'catalog/book_detail.html', context={'book': book})


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10
    context_object_name = 'author_list'   # שם משלכם לרשימה כמשתנה תבנית
    queryset = Author.objects.all()#filter(title__contains='ספר')[:5] # קבל 5 ספרים המכילים את הכותרת 'war'
    template_name = 'author/my_arbitrary_template_name_list.html'  # ציינו שם/מיקום תבנית משלכם


class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Author
    
    def author_detail_view(request, primary_key):
        author = get_object_or_404(Author, pk=primary_key)
        return render(request, 'catalog/author_detail.html', context={'author': author})
    

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """תצוגה כללית של ספרים מושאלים למשתמש הנוכחי."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )
   
    def get_borrower(self, obj):
        return(obj.borrower)


class AllLoanedBooksByUserListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    """תצוגה כללית של כל הספרים המושאלים (לספרניות בלבד)."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(status__exact='o')
            .order_by('due_back')
        )

    def test_func(self):
        # רק אם המשתמש שייך לקבוצה בשם 'ספרניות'
        return self.request.user.groups.filter(name='Librarians').exists()

@login_required
def renew_book_librarian(request, pk):
    from django.http import HttpResponseForbidden
    if not request.user.groups.filter(name='Librarians').exists():
        return HttpResponseForbidden("Access denied: Only librarians can renew books.")
    """תצוגה לחידוש ספר ספציפי על ידי ספרנית."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # אם מדובר בבקשת POST – עבד את הנתונים מהטופס
    if request.method == 'POST':

        # צור מופע טופס ומלא אותו בנתונים מהבקשה (binding)
        form = RenewBookForm(request.POST)

        # בדוק אם הטופס תקין
        if form.is_valid():
            # עדכן את התאריך החדש במודל
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # הפנה לעמוד אחר (all-borrowed)
            return HttpResponseRedirect(reverse('all-borrowed'))

    # אם זו בקשת GET (או כל סוג אחר) – צור טופס ברירת מחדל
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

class AuthorCreate(UserPassesTestMixin, PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/11/2023'}
    permission_required = 'catalog.add_author'

    def test_func(self):
        return self.request.user.groups.filter(name='Librarians').exists()

class AuthorUpdate(UserPassesTestMixin, PermissionRequiredMixin, UpdateView):
    model = Author
    # לא מומלץ (עלול להוות סיכון אבטחתי אם יתווספו שדות)
    fields = '__all__'
    permission_required = 'catalog.change_author'

    def test_func(self):
        return self.request.user.groups.filter(name='Librarians').exists()

class AuthorDelete(UserPassesTestMixin, PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.delete_author'

    def test_func(self):
        return self.request.user.groups.filter(name='Librarians').exists()
    
    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("author-delete", kwargs={"pk": self.object.pk})
            )


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.add_book'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.change_book'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    permission_required = 'catalog.delete_book'
    success_url = reverse_lazy('books')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = context.get('object') or getattr(self, 'object', None) or self.get_object()
        bookinstances = book.bookinstance_set.all()
        context['bookinstance_list'] = bookinstances
        context['has_bookinstances'] = bookinstances.exists()
        context['book'] = book
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.form_valid(form=None)

    def form_valid(self, form):
        if self.object.bookinstance_set.exists():
            context = self.get_context_data(object=self.object)
            context['cannot_delete'] = True
            return self.render_to_response(context)
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)
