# users/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
import random
from .forms import MemberRegistrationForm
from django.contrib.auth.decorators import login_required
from transactions.models import BorrowRecord, Reservation

@login_required
def member_profile(request):
    active_borrows = BorrowRecord.objects.filter(user=request.user, is_returned=False).order_by('due_date')
    total_fines = sum(record.fine_amount for record in active_borrows)
    
    # Fetch user's pending waitlist items
    active_reservations = Reservation.objects.filter(user=request.user, status='PENDING')

    context = {
        'active_borrows': active_borrows,
        'total_fines': total_fines,
        'active_reservations': active_reservations # Inject into template
    }
    return render(request, 'users/profile.html', context)

def register(request):
    # If the user is already logged in, they shouldn't see the signup page
    if request.user.is_authenticated:
        return redirect('book_list')

    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            # Save the user, but don't commit to the database just yet
            user = form.save(commit=False)
            
            # Ensure they are marked as a standard member
            user.is_member = True
            
            # Auto-generate a unique 8-digit library card number
            random_number = random.randint(10000000, 99999999)
            user.library_card_number = f"LIB-{random_number}"
            
            # Now save to the database
            user.save()
            
            # Automatically log the new user in
            login(request, user)
            messages.success(request, f"Welcome! Your new Library Card Number is {user.library_card_number}.")
            return redirect('profile')
    else:
        # If it's a GET request, just show the blank form
        form = MemberRegistrationForm()

    return render(request, 'users/register.html', {'form': form})