from django import forms


class SearchForm(forms.Form):
    query = forms.CharField(max_length=30, min_length=2)
    count = forms.TypedChoiceField(choices=[(i, i) for i in range(1, 11)], coerce=str)


class MyForm(forms.Form):
    query = forms.CharField(max_length=30, min_length=2)
    count = forms.TypedChoiceField(choices=[(i, i) for i in range(1, 11)],
                                   coerce=str)
