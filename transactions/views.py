from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from catalog.models import Book
from .models import BorrowRecord, Reservation
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def issue_book(request, book_id):
    # Ensure the user is logged in and is a valid member
    if not request.user.is_authenticated or not request.user.is_member:
        messages.error(request, "You must be a registered member to borrow books.")
        return redirect('book_list')

    book = get_object_or_404(Book, id=book_id)

    with transaction.atomic():
        if book.available_copies > 0:
            book.available_copies -= 1
            book.save()

            due_date = timezone.now().date() + timedelta(days=14)
            BorrowRecord.objects.create(
                user=request.user,
                book=book,
                due_date=due_date
            )
            
            # NEW: Trigger the email notification
            subject = f"Book Checked Out: {book.title}"
            message = f"Hello {request.user.username},\n\nYou have successfully borrowed '{book.title}'.\nPlease ensure it is returned by {due_date} to avoid any fines.\n\nHappy Reading!"
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False,
            )

            messages.success(request, f"Successfully borrowed {book.title}.")
        else:
            messages.warning(request, "Sorry, this book is currently out of stock.")

    return redirect('book_list')

@staff_member_required
def return_book(request, record_id):
    record = get_object_or_404(BorrowRecord, id=record_id, is_returned=False)
    
    with transaction.atomic():
        # 1. Mark the record as returned and log the date
        record.is_returned = True
        record.return_date = timezone.now().date()
        
        # Note: In a real system, you would handle fine payment logic here 
        # before clearing the fine_amount or marking it paid.
        record.save()

        # 2. Increment the available copies back into inventory
        book = record.book
        book.available_copies += 1
        book.save()

        messages.success(request, f"Book '{book.title}' has been successfully returned by {record.user.username}.")
        
    # Redirect back to a librarian dashboard or admin panel
    return redirect('admin:transactions_borrowrecord_changelist')


def reserve_book(request, book_id):
    if not request.user.is_authenticated or not request.user.is_member:
        messages.error(request, "You must log in to reserve books.")
        return redirect('login')

    book = get_object_or_404(Book, id=book_id)

    # 1. Prevent reserving if the book is actually available
    if book.available_copies > 0:
        messages.warning(request, "This book is available! You can borrow it directly.")
        return redirect('book_list')

    # 2. Prevent reserving if the user already has an active reservation for it
    if Reservation.objects.filter(user=request.user, book=book, status='PENDING').exists():
        messages.info(request, "You are already on the waitlist for this book.")
        return redirect('book_list')

    # 3. Create the reservation
    Reservation.objects.create(user=request.user, book=book)
    
    # Optional: Calculate their spot in line
    spot_in_line = Reservation.objects.filter(book=book, status='PENDING').count()
    
    messages.success(request, f"Reserved! You are number {spot_in_line} on the waitlist for '{book.title}'.")
    return redirect('book_list')


@login_required
def generate_receipt(request, record_id):
    # Fetch the record, ensuring it belongs to the logged-in user
    record = get_object_or_404(BorrowRecord, id=record_id, user=request.user)
    
    # Define the template and the data to pass to it
    template_path = 'transactions/receipt_pdf.html'
    context = {'record': record}
    
    # Create the HTTP response with the correct PDF headers
    response = HttpResponse(content_type='application/pdf')
    # Use 'attachment;' to force a download. Change to 'inline;' if you want it to open in a new tab instead.
    response['Content-Disposition'] = f'attachment; filename="Library_Receipt_{record.book.isbn}.pdf"'
    
    # Render the HTML
    template = get_template(template_path)
    html = template.render(context)
    
    # Convert HTML to PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors generating your PDF.')
    
    return response