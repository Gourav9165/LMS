from django.contrib import admin
from .models import BorrowRecord

@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'issue_date', 'due_date', 'is_returned', 'fine_amount')
    list_filter = ('is_returned', 'due_date')
    search_fields = ('user__username', 'book__title')