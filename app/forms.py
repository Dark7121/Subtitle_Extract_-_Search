from django import forms
from .models import Video

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'video_file']
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if Video.objects.filter(title=title).exists():
            raise forms.ValidationError("A video with this title already exists. Please choose another Title.")
        return title
