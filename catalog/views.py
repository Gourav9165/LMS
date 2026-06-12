from django.shortcuts import render
from django.db.models import Q, Count, Sum
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.contrib.auth import get_user_model
from transactions.models import BorrowRecord
from users.models import User
from .models import Book

User = get_user_model()

def home(request):
    return render(request, 'catalog/home.html')

def book_list(request):
    query = request.GET.get('q', '')
    
    if query:
        # Search by title, author, or ISBN simultaneously
        books = Book.objects.filter(
            Q(title__icontains=query) | 
            Q(author__icontains=query) | 
            Q(isbn__icontains=query)
        )
    else:
        books = Book.objects.all()

    return render(request, 'catalog/book_list.html', {'books': books, 'query': query})

User = get_user_model()

@staff_member_required
def analytics_dashboard(request):
    # 1. Count Total Books
    total_books = Book.objects.count()
    
    # 2. Count Active Members (Excluding superusers/admins)
    total_members = User.objects.filter(is_superuser=False).count()
    
    # 3. Count Active Borrows (Books not yet returned)
    active_borrows = BorrowRecord.objects.filter(return_date__isnull=True).count()
    
    # 4. Count Overdue Items (Not returned AND due date is in the past)
    today = timezone.now().date()
    overdue_count = BorrowRecord.objects.filter(return_date__isnull=True, due_date__lt=today).count()
    
    # 5. Fetch Recent Transactions (Grab the 5 newest records)
    recent_transactions = BorrowRecord.objects.all().order_by('-issue_date')[:5]

    # Package everything into the context dictionary
    context = {
        'total_books': total_books,
        'total_members': total_members,
        'active_borrows': active_borrows,
        'overdue_count': overdue_count,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'catalog/dashboard.html', context)