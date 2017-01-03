from django import forms
from kmtshi.models import Candidate
#from .models import Comments

class CandidateForm(forms.ModelForm):

    class Meta:
        model = Candidate
        fields = ('classification',)

#class CommentsForm(forms.ModelForm):

#    class Meta:
#        model = Comments
#        fields = ('text',)