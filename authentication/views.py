from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages


from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from django.contrib.auth.tokens import default_token_generator

from django.contrib.auth import authenticate,login,logout

import random


def generate_verification_code():
    return ''.join(random.choices('0123456789', k=4))


def signup(request):
    if request.method=="POST":
        email = request.POST['email']
        password = request.POST['pass1']
        confirm_password = request.POST['pass2']

        if password != confirm_password:
            messages.warning(request,"password is not matching")
            return render(request,'auth/signup.html')
        
        if email:
            try:
                if User.objects.get(username=email):
                    messages.info(request,"email already teken")
                    return render(request,"auth/signup.html")
            except Exception as identifier:
                pass
        else:
             messages.warning(request,"email is not given")
             return render(request,"auth/signup.html")

        user = User.objects.create_user(email,email,password)
        user.is_active=False
        user.save()

        verification_code = generate_verification_code()
        Profile.objects.create(user=user, verification_code=verification_code)


        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        domain = get_current_site(request).domain
        activation_link = f"http://{domain}/auth/activate/{uid}/{token}/"

        subject = "Activate Your Account"
        message = render_to_string('activationemail.html', {
            'user': user,
            'activation_link': activation_link,
        })

        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

        messages.success(request, "Account created successfully. Activation email has been sent.")
        return redirect('/auth/login/')  


    return render(request,'auth/signup.html')



def activate(request, uidb64, token):
        try:
            uid=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=uid)
        except Exception as identifier:
            user=None
        if user is not None and default_token_generator.check_token(user,token):
            user.is_active=True
            user.save()
            messages.info(request,"Account Activated Successfully")
            return redirect('/auth/login/')
        return render(request,'activatefail.html')

def login_user(request):

    if request.method=="POST":

        username=request.POST['email']
        userpassword=request.POST['pass1']
        myuser=authenticate(request,username=username,password=userpassword)

        if myuser is not None:
            login(request,myuser)
            messages.success(request,"Login Success")
            return redirect('/')

        else:
            messages.info(request,"USER is not valid")
            return redirect('/auth/login/')

    return render(request,'auth/login.html')  

def logout_user(request):
    logout(request)
    messages.info(request,"Logout Success")
    return redirect('/')



from .models import Profile 

def forgotpassword(request):
    if request.method == 'POST':
        email=request.POST['email']
        if email:
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, 'Email not found.')
                return redirect('/auth/forgot-password/')
            
            # Generate a verification code
            profile = Profile.objects.get(user=user)
            profile.generate_verification_code()
            verification_code =  profile.verification_code
            
            # Build the email
            message = f"Your verification code is: {verification_code}"
            
            # Send the email
            send_mail('Verification Code', message, settings.EMAIL_HOST_USER, [email])
            
            messages.success(request, 'An email has been sent to the provided email address with a verification code.')
            return redirect('verify_code', email=email)
        else:
            messages.error(request, 'email is not  given')

    
    return render(request, 'auth/forgotpassword.html')


def verify_code(request, email):
    user = User.objects.get(email=email)
    profile = Profile.objects.get(user=user)
    
    if request.method == 'POST':
        entered_code = request.POST['code']
        
        if str(profile.verification_code) == entered_code:
            # Code is correct
            messages.success(request, 'Verification code is correct.')
            return redirect('reset_password', email=email)
        else:
            # Code is incorrect
            messages.error(request, 'Incorrect verification code.')
            return redirect('verify_code', email=email)
    
    return render(request, 'auth/verify_code.html', {'email': email})


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User

def reset_password(request, email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, 'Invalid email.')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            # Set the new password
            user.set_password(password)
            user.save()
            
            # Authenticate the user and log them in
            user = authenticate(username=user.username, password=password)
            login(request, user)
                        
            messages.success(request, 'Password has been reset successfully. You are now logged in.')
            return redirect('/')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('reset_password', email=email)
    
    return render(request, 'auth/resetpassword.html', {'email': email})










