from django import forms
from kmtshi.models import Candidate, Comment, Classification

class CandidateForm(forms.ModelForm):

    class Meta:
        model = Candidate
        fields = ('classification',)

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)

class NameForm(forms.Form):
    name = forms.CharField(label='Object Name Contains',max_length=100)

class CoordinateForm(forms.Form):
    ra = forms.DecimalField(label='RA (decimal deg)',min_value=0.00,max_value=360.00)
    dec = forms.DecimalField(label='DEC (decimal deg)',min_value=-90.00,max_value=90.00)
    radius = forms.DecimalField(label='search radius (arcsec)',min_value=0.01,max_value = 120.0)

class SelectCandidatesForm(forms.Form):
    choices = forms.ModelMultipleChoiceField(
        queryset = None,
        widget = forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args,**kwargs)
        self.fields['choices'].queryset = queryset
