from django import forms
from kmtshi.models import Candidate, Comment

class CandidateForm(forms.ModelForm):

    class Meta:
        model = Candidate
        fields = ('classification',)

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)

class NameForm(forms.Form):
    name = forms.CharField(label='Object Name',max_length=100)