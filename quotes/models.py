from django.db import models, transaction, connection
from django.core.exceptions import ValidationError
from django.db.models import F, Q, Sum, UniqueConstraint
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from .utils import normalize_text

class Source(models.Model):
    MOVIE = "movie"
    BOOK = "book"
    KIND_CHOICES = [
        (MOVIE, "Фильм"),
        (BOOK, "Книга")
    ]

    name = models.CharField(max_length=255, unique=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default=MOVIE)

    def __str__(self):
        return self.name

    def get_full_name(self):
        return f"{self.name} ({self.get_kind_display()})"

class QuoteQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True, weight__gt=0)

    def weighted_random(self, exclude_pk=None):
        qs = self.active()
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)

        agg = qs.aggregate(total=Sum("weight"))
        total = agg.get("total") or 0
        if total <= 0:
            return None

        import random
        r = random.randint(1, int(total))
        cumulative = 0
        for row in qs.values("id", "weight").order_by("id"):
            cumulative += row["weight"]
            if cumulative >= r:
                return self.get(pk=row["id"])
        return None

class Quote(models.Model):
    text = models.TextField()
    normalized_text = models.CharField(max_length=500, editable=False, unique=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="quotes")
    weight = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = QuoteQuerySet.as_manager()
    weight = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    class Meta:
        indexes = [
            models.Index(fields=["source", "is_active"]),
            models.Index(fields=["-likes", "-views"]),
        ]
        UniqueConstraint(
            fields=["source", "normalized_text"],
            name="uq_quote_source_normalized_text"
        ),

    def clean(self):
        if self.source_id:
            quotes_from_this_source = Quote.objects.filter(source=self.source)

            if self.pk:
                quotes_from_this_source = quotes_from_this_source.exclude(pk=self.pk)

            if quotes_from_this_source.count() >= 3:
                raise ValidationError(
                    "У этого источника уже есть 3 цитаты. Больше добавлять нельзя."
                )

        if self.weight < 1:
            raise ValidationError("Вес должен быть положительным целым числом (минимум 1).")

    def save(self, *args, **kwargs):
        self.normalized_text = normalize_text(self.text)
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.source}: {self.text[:50]}..."

class Vote(models.Model):
    LIKE = 1
    DISLIKE = -1
    VALUE_CHOICES = [(LIKE, "like"), (DISLIKE, "dislike")]

    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name="votes")
    session_key = models.CharField(max_length=64)
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [("quote", "session_key")]
        indexes = [models.Index(fields=["quote", "session_key"])]
