from django import forms
from .models import EditedImage

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = EditedImage
        fields = ['original_image']
