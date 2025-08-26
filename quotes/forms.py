from django import forms
from .models import Quote, Source

class QuoteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['weight'].initial = None

    source_name = forms.CharField(
        label="Источник",
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Название фильма или книги'})
    )
    source_kind = forms.ChoiceField(label="Тип источника", choices=Source.KIND_CHOICES)

    class Meta:
        model = Quote
        fields = ["text", "source_name", "source_kind", "weight"]
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Начните вводить текст цитаты здесь...'
            }),
            'weight': forms.NumberInput(attrs={
                'min': 1,
                'max': 10,
                'placeholder': 'Вес (от 1 до 10)'
            }),
        }
        labels = {
            'text': 'Текст цитаты',
            'weight': '',
        }

    def save(self, commit=True):
        source_name = self.cleaned_data["source_name"]
        source_kind = self.cleaned_data["source_kind"]

        source, _ = Source.objects.get_or_create(
            name=source_name,
            defaults={'kind': source_kind}
        )

        instance = super().save(commit=False)
        instance.source = source

        if commit:
            instance.save()
        return instance