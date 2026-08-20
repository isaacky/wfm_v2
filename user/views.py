from email.message import EmailMessage
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, UserProfileForm,ChangeSectorForm
from django.contrib import messages, auth
from .models import Account, UserProfile

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


def loginuser(request):
    if request.user.is_authenticated:
        return redirect('main:my-dashboard')
    else:
        if request.method == 'POST':

             stid = request.POST['stid']
             password = request.POST['password']

             user = auth.authenticate(stid=stid, password=password)

             if user is not None and user.is_active == True:
               auth.login(request,user)
               messages.success(request, f'Karibu Tena {request.user.name}')
               if stid == request.POST['password']:
                   return redirect('change_password')
               return redirect('main:my-dashboard')
             else:
                messages.error(request, 'Incorrect credentials or your profile may be disabled')
                return redirect('login')

        return render(request, 'user/login.html')

@login_required(login_url="login")
def logoutUser(request):
    auth.logout(request)
    messages.success(request, 'You Have Logged Out Successfully!')
    return redirect('login')

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(stid__exact=request.user.stid)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'user/change_password.html')

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user =Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('user/reset_password_email.html',{
                'user' : user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to =[to_email])
            send_email.send()

            messages.success(request,'Password reset has been sent to your email address')
            return redirect('login')

        else:
            messages.error(request, 'Account Does Not Exist')
            return redirect('forgotPassword')
    return render(request, 'user/forgotPassword.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'user/resetPassword.html')

@login_required(login_url='login')
def registerUser(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        profile = UserProfileForm(request.POST)
        if form.is_valid() and profile.is_valid():
            email = form.cleaned_data.get('email')
            username = email.split('@')[0]
            name = form.cleaned_data.get('name')
            stid = form.cleaned_data.get('stid')
            mobile = form.cleaned_data.get('mobile')
            password = form.cleaned_data.get('stid')
            user = Account.objects.create_user(email=email, username=username, stid=stid, name=name, mobile=mobile,password=password)
            user.save()


            profile1 = UserProfile()
            profile1.user_id = user.id
            profile1.county = profile.cleaned_data.get('county')
            profile1.region = profile.cleaned_data.get('region')
            profile1.campaign = profile.cleaned_data.get('campaign')
            profile1.save()

            users = Account.objects.order_by('-date_joined').filter(stid=stid)
            context = {
                'users': users, }
            messages.success(request, 'User Registered Successfully')
            return render(request, 'user/registeredusers.html', context)
        else:
            messages.error(request, 'Error While Registering a New User')
            return redirect('register-user')

    else:
        form = RegistrationForm()
        profile = UserProfileForm()
    context = {
        'form': form,
        'profile': profile,
         'nbar' : 'registernewuser'
    }

    return render(request, 'user/registernewuser.html', context)
@login_required(login_url='login')
def registeredusers(request):
    if request.user.is_authenticated:
        users = (
            Account.objects.select_related("userprofile")
            .filter(is_superuser=False)
            .order_by("-date_joined")
        )
        paginator = Paginator(users, 10)
        page = request.GET.get('page')
        paged_uploads = paginator.get_page(page)

        context = {
            'users': paged_uploads,
            'nbar' : 'admin',
            'nbar' : 'registeredusers'}
    return render(request, 'user/registeredusers.html', context)

@login_required(login_url='login')
def changesector(request):
    me  = UserProfile.objects.get(user=request.user)
    form1 = ChangeSectorForm(instance=me)
 

    if request.method == 'POST':
        form1 = ChangeSectorForm(request.POST,instance=me)
        if form1.is_valid():
            form1.save()
            messages.success(request, 'Updated successfully')
            return redirect('main:my-dashboard')

    context ={'form': form1}
    return render(request, 'user/changesector.html', context)

@login_required(login_url='login')
def deactivateuser(request,stid):        
    user = Account.objects.get(stid=stid)
    user.is_active = False
    user.save()
    messages.success(request, 'Profile successfully disabled.')
    return redirect('registered-user')

@login_required(login_url='login')
def activateuser(request,stid):        
    user = Account.objects.get(stid=stid)
    user.is_active = True
    user.save()
    messages.success(request, 'Profile successfully Activated.')
    return redirect('registered-user')

@login_required(login_url='login')
def reset_password(request,stid):  
    user = Account.objects.get(stid=stid)
    password = str(user.stid) 
    user.set_password(password)
    user.save()
    messages.success(request, 'Password successfully Reset to. ' + password)
    return redirect('registered-user')

@login_required(login_url='login')
def set_admin(request,stid):        
    user = Account.objects.get(stid=stid)
    user.is_staff = True
    user.save()
    messages.success(request, 'User Has Been Configured as Admin Successfully.')
    return redirect('registered-user')

@login_required(login_url='login')
def set_user(request,stid):        
    user = Account.objects.get(stid=stid)
    user.is_staff = False
    user.save()
    messages.success(request, 'User Has Been Configured as User Successfully.')
    return redirect('registered-user')

@login_required(login_url="login")
def delete_user(request, pk):
    if not request.user.is_superuser:
        messages.error(request, 'This action was NOT Successful. Permission Declined')
        return redirect('registered-user')
    else:      
        img  = Account.objects.get(id=pk)
        if request.method =='POST':
            img.delete()
            return redirect('registered-user')
        context = {'object' : img}
       
        return render(request, 'user/delete_confirmation.html', context)

@login_required(login_url="login")
def update_user(request,pk):
    if not request.user.is_admin:
         messages.error(request, 'This action was NOT Successful.')
         return redirect('registered-user')
    else:
        img  = Account.objects.get(pk=pk)
        img1 = UserProfile.objects.get(user_id=img.pk)
        form = RegistrationForm(instance=img)
        profile = UserProfileForm(instance=img1)

    
        if request.method == 'POST':
            form = RegistrationForm(request.POST, instance=img)
            profile = UserProfileForm(request.POST, instance=img1)
            if form.is_valid() and profile.is_valid():
                if not profile.cleaned_data.get('profiletype') == 'cse':
                    form.save()
                    profile.save()
                    messages.success(request, 'User Profile Updated successfully')
                    return redirect('registered-user')
                else:
                    messages.error(request, 'You cannot change the profile to CSE')
                    return redirect('registered-user')
            
        context ={ 'form': form,  'profile': profile}
    return render(request, 'user/registernewuser.html', context)
@login_required(login_url="login")
def search_user(request):
	if 'keyword' in request.GET:
		keyword = request.GET["keyword"]
		if keyword:
			paged_uploads = Account.objects.filter(stid=keyword)			
	context = {
		'users': paged_uploads,	
        'nbar': 'searchuser',	
	}
	
	return render(request, 'user/registeredusers.html', context)