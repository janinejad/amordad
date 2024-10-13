from django import forms


class CartForm(forms.Form):
    update = forms.BooleanField(required=False,
                                initial=False,
                                widget=forms.HiddenInput)
    variant = forms.IntegerField(widget=forms.HiddenInput(attrs={'id': 'selected-product', 'class': 'quantity'}))
    variant_count = forms.IntegerField()
