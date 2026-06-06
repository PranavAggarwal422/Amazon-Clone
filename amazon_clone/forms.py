from django import forms    
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User 

class CustomUserCreationForm(UserCreationForm)  : 
    first_name = forms.CharField(required = True)
    last_name = forms.CharField(required = True) 
    email = forms.EmailField(required = True) 

    class Meta : 
        model = User 
        fields = [ "email" , "first_name" , "last_name" , "password1" , "password2"]
    

    def clean_email(self) : 
        email = self.cleaned_data["email"]
        if User.objects.filter(email = email).exists() : 
            raise forms.ValidationError("Email is already registered")
        return email 
    
    def save(self , commit = True) : 
        user = super().save(commit = False)
        user.username = self.cleaned_data["email"]
        if commit : 
            user.save()
        return user 
    

