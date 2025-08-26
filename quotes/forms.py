from django import forms
from .models import Quote, Source, normalize_text
from django.core.exceptions import ValidationError
from fuzzywuzzy import fuzz

class QuoteForm(forms.ModelForm):
    confirm_add = forms.BooleanField(required=False, widget=forms.HiddenInput())
    similar_quote = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['weight'].initial = None
        self.similar_quote = None

    source_name = forms.CharField(
        label="Источник",
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Название фильма или книги'})
    )
    source_kind = forms.ChoiceField(label="Тип источника", choices=Source.KIND_CHOICES)

    class Meta:
        model = Quote
        fields = ["text", "source_name", "source_kind", "weight", "confirm_add"]
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Начните вводить текст цитаты здесь...'
            }),
            'weight': forms.NumberInput(attrs={
                'min': 1, 'max': 10, 'placeholder': 'Вес (от 1 до 10)'
            }),
        }
        labels = {
            'text': 'Текст цитаты',
            'weight': '',
        }

    def clean(self):
        cleaned_data = super().clean()

        text = cleaned_data.get("text")
        source_name = cleaned_data.get("source_name")
        confirmed = cleaned_data.get("confirm_add")

        if not text:
            return cleaned_data

        normalized_new = normalize_text(text)

        existing_quote_qs = Quote.objects.filter(normalized_text=normalized_new)
        if self.instance and self.instance.pk:
            existing_quote_qs = existing_quote_qs.exclude(pk=self.instance.pk)

        if existing_quote_qs.exists():
            existing_quote = existing_quote_qs.first()
            raise ValidationError(f"Такая цитата уже существует (источник: {existing_quote.source.name}).")

        if source_name:
            source = Source.objects.filter(name=source_name).first()
            if source and source.quotes.count() >= 3:
                raise ValidationError(f"У источника «{source_name}» уже есть 3 цитаты.")

        if not confirmed:
            existing_quotes = Quote.objects.all()
            for quote in existing_quotes:
                similarity_ratio = fuzz.ratio(normalized_new, quote.normalized_text)
                if similarity_ratio > 90:
                    self.similar_quote = quote.text
                    raise ValidationError("Найдена похожая цитата. Пожалуйста, подтвердите добавление.",
                                          code='similar_quote')

        return cleaned_data

    def save(self, commit=True):
        source_name = self.cleaned_data.get("source_name")
        source_kind = self.cleaned_data.get("source_kind")

        source, _ = Source.objects.get_or_create(
            name=source_name,
            defaults={'kind': source_kind}
        )
        instance = super().save(commit=False)
        instance.source = source
        instance.is_active = True

        if commit:
            instance.save()
        return instance