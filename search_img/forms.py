from django import forms


class SearchForm(forms.Form):
    query = forms.CharField(max_length=30, min_length=2)
    s = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    count = forms.TypedChoiceField(choices=[(i, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[i-1]) for i in range(1, 11)], coerce=str)


class MyForm(forms.Form):
    query = forms.CharField(max_length=30, min_length=2)
    s = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    count = forms.TypedChoiceField(choices=[(i, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[i - 1]) for i in range(1, 20)],
                                   coerce=str)
