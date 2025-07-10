from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import PasswordChangeForm




class Enquiry_form(ModelForm):
    class Meta:
        model=Enquiry
        fields=('name','email','phone','message')
        

class Signup_form(UserCreationForm):
    class Meta:
        model=Custom_user
        fields=['first_name','last_name','username','email','password1','password2']
        
        
        
class Profile_change_form(UserChangeForm):
    class Meta:
        model=Custom_user
        fields=['first_name','last_name','username','email']
        
    def __init__(self, *args, **kwargs):
        super(Profile_change_form, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control'
            })
            
            
            

class Password_Change_Form(PasswordChangeForm):
    old_password = forms.CharField(
        label="Old Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter current password'
        })
    )
    new_password1 = forms.CharField(
        label="New Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        }),
        help_text="Minimum 8 characters. Should not be too common or entirely numeric."
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )
    
    
    
class Trainer_profile_form(ModelForm):
    
    first_name=forms.CharField(
        label="First Name",
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'First Name'})
    )
    
    last_name=forms.CharField(
        label="Last Name",
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Last Name'})
    )
    
    email=forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Email'})
    )
    
    
    class Meta:
      
        model=Trainer
        exclude = ['trainer', 'salary',]

        widgets = {
            
            'image': forms.FileInput(attrs={
                'class': 'form-control',
            }),

            'profession': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter profession',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter address',
                'rows': 3,
            }),
            
            'facebook': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Facebook profile link',
            }),
            'whatsapp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'WhatsApp number or link',
            }),
            'instagram': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Instagram profile link',
            }),
            'linkedin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'LinkedIn profile link',
            }),
            'youtube': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'YouTube channel link',
            }),
        }
        
    def __init__(self,*args,**kwargs):
        user = kwargs.pop('user',None)
        super().__init__(*args,**kwargs)
        
        if user:
            self.fields['first_name'].initial=user.first_name
            self.fields['last_name'].initial=user.last_name
            self.fields['email'].initial=user.email
            
            
        self.order_fields([
            'image',
            'first_name',
            'last_name',
            'profession',
            'address',
            'email',
            'facebook',
            'whatsapp',
            'instagram',
            'linkedin',
            'youtube',
        ])
            
    def save(self, commit = True,user = None):
        Trainer= super().save(commit=False)
        
        if user:
            user.first_name=self.cleaned_data['first_name']
            user.last_name=self.cleaned_data['last_name']
            user.email=self.cleaned_data['email']
            
            if commit:
                user.save()
        
        if commit:
            Trainer.save()
        return Trainer