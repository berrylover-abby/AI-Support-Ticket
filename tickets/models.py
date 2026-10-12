from django.db import models

# Create your models here.
class Ticket(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Status(models.TextChoices):
        PENDING_ANALYSIS = "pending_analysis", "Pending analysis"
        PENDING_REVIEW = "pending_review", "Pending review"
        CONFIRMED = "confirmed", "Confirmed"
        ANALYSIS_FAILED = "analysis_failed", "Analysis failed"
    
    # status format:
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING_ANALYSIS,
    )

    # ai result format:
    ai_result = models.JSONField(
    default=dict,
    blank=True,
    )
    # category
    reviewed_category = models.CharField(
        max_length=20,
        choices=[
            ("account", "Account"),
            ("billing", "Billing"),
            ("technical", "Technical"),
            ("other", "Other"),
        ],
        blank=True,
    )
    # priority
    reviewed_priority = models.CharField(
        max_length=10,
        choices=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
        ],
        blank=True,
    )
    reviewed_summary = models.TextField(blank=True)
    reviewed_reply = models.TextField(blank=True)


    # Record metadata for the most recent successful analysis.
    analysis_model = models.CharField(max_length=100, blank=True)
    analysis_prompt_version = models.CharField(max_length=50, blank=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)



