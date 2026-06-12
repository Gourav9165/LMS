from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from transactions.models import BorrowRecord
from rich.console import Console
from rich.table import Table

class Command(BaseCommand):
    help = 'Calculates and applies daily fines to overdue books'

    def handle(self, *args, **kwargs):
        console = Console()
        today = timezone.now().date()
        daily_fine_rate = Decimal('10.00') # ₹10 per day

        # Find all books that are overdue and not yet returned
        overdue_records = BorrowRecord.objects.filter(
            is_returned=False, 
            due_date__lt=today
        )

        if not overdue_records:
            console.print("[bold green]✔ All clear! No overdue books today.[/bold green]")
            return

        # Setup aesthetic terminal table
        table = Table(title="Overdue Books Fine Calculation", header_style="bold cyan")
        table.add_column("User", style="magenta")
        table.add_column("Book", style="green")
        table.add_column("Days Overdue", justify="right")
        table.add_column("Total Fine", justify="right", style="bold red")

        for record in overdue_records:
            days_overdue = (today - record.due_date).days
            new_fine = Decimal(days_overdue) * daily_fine_rate

            # Update database
            record.fine_amount = new_fine
            record.save()

            # Add row to terminal UI
            table.add_row(
                record.user.username, 
                record.book.title, 
                str(days_overdue), 
                f"₹{new_fine}"
            )

        console.print(table)
        console.print(f"[bold yellow]⚠ Updated fines for {overdue_records.count()} records.[/bold yellow]")