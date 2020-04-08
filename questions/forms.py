from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Question

class CreateQuestionForm(forms.Form):
    question_text = forms.CharField(max_length=255, widget=forms.Textarea)
    image = forms.ImageField(required=False, label='Attach image (optional)')
    tags = forms.CharField(max_length=100,
        widget=forms.TextInput(attrs={'placeholder': _('Separated by comma')}))

class EditQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'attached_image']
        widgets = {
            'text': forms.Textarea
        }

class CreateAnswerForm(forms.Form):
    answer_text = forms.CharField(max_length=500, widget=forms.Textarea)
