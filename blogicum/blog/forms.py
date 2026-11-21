from django import forms
from django.core.exceptions import ValidationError

from blog.models import Comment
from blog.moderation import is_toxic

MODERATION_ERROR = (
    'Комментарий не проходит модерацию. '
    'Пожалуйста, сформулируйте мысль корректнее.'
)


class CommentForm(forms.ModelForm):

    def clean_text(self):
        text = self.cleaned_data['text']

        if is_toxic(text):
            raise ValidationError(MODERATION_ERROR)

        return text

    class Meta:
        model = Comment
        fields = ('text',)
