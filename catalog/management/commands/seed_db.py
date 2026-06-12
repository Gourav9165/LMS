from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from faker import Faker
import random
from rich.console import Console

from catalog.models import Book
from users.models import User
from transactions.models import BorrowRecord

class Command(BaseCommand):
    help = 'Seeds the database with realistic dummy books, users, and simulated checkouts.'

    def handle(self, *args, **kwargs):
        fake = Faker()
        console = Console()
        
        console.print("[bold yellow]Cleaning up old dummy data...[/bold yellow]")
        # Delete old books and members, but preserve your superuser admin account
        User.objects.filter(is_superuser=False).delete()
        Book.objects.all().delete()
        
        console.print("[bold cyan]Generating 10 Dummy Members...[/bold cyan]")
        users = []
        for _ in range(10):
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='password123', # Standardized password for testing
                is_member=True,
                library_card_number=fake.unique.bothify(text='LIB-########')
            )
            users.append(user)
            
        console.print("[bold cyan]Generating 50 Realistic Books...[/bold cyan]")
        books = []
        for _ in range(50):
            total = random.randint(2, 6)
            book = Book.objects.create(
                title=fake.catch_phrase().title(),
                author=fake.name(),
                isbn=fake.isbn13().replace("-", ""),
                total_copies=total,
                available_copies=total # We will decrement this when simulating borrows
            )
            books.append(book)
            
        console.print("[bold cyan]Simulating 30 Borrowing Transactions...[/bold cyan]")
        today = timezone.now().date()
        
        for _ in range(30):
            user = random.choice(users)
            book = random.choice(books)
            
            # Prevent checking out if copies are 0
            if book.available_copies <= 0:
                continue
                
            # Randomize the issue date between 1 to 40 days ago
            days_ago = random.randint(1, 40)
            issue_date = today - timedelta(days=days_ago)
            due_date = issue_date + timedelta(days=14)
            
            # Randomly decide if the book was returned or is still kept by the user
            is_returned = random.choice([True, False])
            
            # 1. Create the record
            record = BorrowRecord.objects.create(
                user=user,
                book=book,
                due_date=due_date
            )
            
            # 2. Overwrite the auto_now_add field and update status
            BorrowRecord.objects.filter(id=record.id).update(issue_date=issue_date)
            
            if is_returned:
                record.is_returned = True
                record.return_date = issue_date + timedelta(days=random.randint(1, 14))
                record.save()
            else:
                # If it's not returned, we must decrement the available inventory
                book.available_copies -= 1
                book.save()
            
        console.print("\n[bold green]✔ Database successfully seeded![/bold green]")
        console.print("You can now refresh your Analytics Dashboard to see the charts populate.")