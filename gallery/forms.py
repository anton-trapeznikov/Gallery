from django import forms
from gallery.models import Tag


class FilterForm(forms.Form):
    '''
    Форма фильтра для списка фотографий.

    '''

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self._tags = Tag.objects.all().order_by('name')

        # Множественный выбор тегов
        self.fields['tag'] = forms.MultipleChoiceField(
            required=False,
            widget=forms.SelectMultiple(attrs={'class': 'js-form-tags'}),
            label='Теги',
            choices=[(tag.pk, tag.name) for tag in self._tags],
        )

        # Множественный выбор исключающих тегов
        self.fields['ex_tag'] = forms.MultipleChoiceField(
            required=False,
            widget=forms.SelectMultiple(attrs={'class': 'js-form-ex-tags'}),
            label='Исключающие теги',
            choices=[(tag.pk, tag.name) for tag in self._tags],
        )

        # Порядок сортировки
        self.fields['order'] = forms.ChoiceField(
            required=False,
            widget=forms.Select(attrs={'class': 'js-order'}),
            label='Порядок сортировки',
            choices=(
                ('date-desc', 'По дате (от новых к старым)'),
                ('date-asc', 'По дате (от старых к новым)'),
                ('rating-desc', 'По рейтингу (самые популярные)'),
                ('rating-asc', 'По рейтингу (самые непопулярные)'),
            ),
        )
