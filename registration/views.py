from django.shortcuts import redirect, render

from django.contrib.auth.models import auth
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required , user_passes_test
from registration.decorators import provider_required 
from django.contrib.sites.shortcuts import get_current_site

from django.template.loader import render_to_string

from django.utils.encoding import force_bytes

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.core.mail import EmailMessage

from django.http import HttpResponse , HttpResponseRedirect


from .models import Profile , User , Provider
from .forms import SignUpForm, UserUpdateForm, ProfileUpdateForm , signupProviderForm
from .tokens import account_activation_token
from products.models import Product , Category

from comments.models import Comment ,  CommentProvider
from comments.forms import CommentForm , CommentProviderForm

from cart.models import Order ,  OrderItem , Address



from io import BytesIO
from django.template.loader import get_template
from django.views import View

def signin(request):
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            # return render(request,'index.html')
            return redirect("product/productlist")

        else:
            messages.info(request, "invalide credentials")
            messages.info(request, request.user.username)
            return redirect("signin")

    else:
        return render(request, "users/signin.html")


def signupchoice(request):
    return render(request, "users/signupchoice.html")


def signupProvider(request):
    if request.method == "POST":
        form = signupProviderForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.is_provider = True
            user.save()
            user.profile.phone_number = form.cleaned_data.get("phone_number")
            user.profile.address = form.cleaned_data.get("address")
            user.save()

            current_site = get_current_site(request)
            subject = "Activate Your MySite Account"
            message = render_to_string(
                "users/account_activation_email.html",
                {
                   'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })

            # user.email_user(subject, message)

            # return redirect('account_activation_sent')
            to_email = form.cleaned_data.get("email")
            email = EmailMessage(subject, message, to=[to_email])
            email.send()
            return HttpResponse(
                "Please confirm your email address to complete the registration"
            )
    else:
        form = signupProviderForm()
    return render(request, "users/signupProvider.html", {"form": form})


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.is_buyer = True
            user.save()
            user.profile.birth_date = form.cleaned_data.get("birth_date")
            user.profile.phone_number = form.cleaned_data.get("phone_number")
            user.profile.address = form.cleaned_data.get("address")
            user.save()
            current_site = get_current_site(request)
            subject = "Activate Your MySite Account"
            message = render_to_string(
                "users/account_activation_email.html",
                {
                   'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })

            # user.email_user(subject, message)

            # return redirect('account_activation_sent')
            to_email = form.cleaned_data.get("email")
            email = EmailMessage(subject, message, to=[to_email])
            email.send()
            return HttpResponse(
                "Please confirm your email address to complete the registration"
            )
    else:
        form = SignUpForm()
    return render(request, "users/Signup.html", {"form": form})


@login_required
def logout(request):
    auth.logout(request)
    return redirect("signin")

@login_required
def delete_account(request):
    user = request.user
    user.delete()
    messages.info(request, 'Your account has been deleted.')
    return redirect('signupchoice')



@login_required
def profile(request,id):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile',id)

    else:
        OrderList = Order.objects.filter(user=request.user,ordered=True)
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': user_form,
        'p_form': profile_form,
        'OrderList' : OrderList
    }
    return render(request, "users/profile.html", context)

@login_required
def home(request):
    return render(request, "home.html")



# email validations


def account_activation_sent(request):
    return render(request, "users/account_activation_sent.html")


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return render(request, "index.html")
    else:
        context = {'uidb64':uidb64, 'token':token}
        return render(request, "users/account_activation_invalid.html", context)



def providerProfile(request,id):
    try:
        provider = User.objects.get(pk=id)
        current_user = request.user
        products = Product.objects.filter(owner=id)
        # adding a comment
        comments =  CommentProvider.objects.filter(provider = provider)
        new_comment = None
        if request.method == "POST":
            comment_form = CommentProviderForm(data=request.POST)
            if comment_form.is_valid():
                # Create Comment object but don't save to database yet
                new_comment = comment_form.save(commit=False)
                 # Assign the current product to the comment

                new_comment.provider = provider
                 # Assign the current user to the comment
                new_comment.user = current_user
                 # Save the comment to the database
                new_comment.save()
        else:
            comment_form = CommentProviderForm()

        provider = User.objects.get(pk=id)
        products = Product.objects.filter(owner=provider)
        order = OrderItem.objects.filter(item__in=products)
        context = {'provider':provider,
        'products':products,
        "comments": comments,
        "comment_form": comment_form,
        "new_comment": new_comment,
        'order':order
        }

        return render(request, "users/provider/profile.html", context)
    except User.DoesNotExist:
        return render(request, "products/notfoundsearch.html")



def userProfile(request,id):
    try:
        user = User.objects.get(pk=id)
        OrderList = Order.objects.filter(user=user,ordered=True)

        context = {'user':user,
                'OrderList' : OrderList
        }

        return render(request, "users/admin/userprofile.html", context)
    except User.DoesNotExist:
        return render(request, "products/notfoundsearch.html")

   

   
@user_passes_test(lambda u: u.is_superuser)
def main(request):
    all_users =User.objects.filter(is_buyer=True)
    
    context ={
        'allusers': all_users
        }

    return render(request,"users/admin/main.html",context)


@user_passes_test(lambda u: u.is_superuser)
def providerList(request):
    all_users =User.objects.filter(is_provider=True)
    
    context ={
        'allusers': all_users
        }

    return render(request,"users/admin/providerlist.html",context)


@user_passes_test(lambda u: u.is_superuser)
def delete_account_admin(request,id):
    user =  User.objects.get(pk=id)
    user.delete()
    messages.info(request, 'This account has been deleted.')
    # redirect to the same page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
@provider_required
def main2(request):
    products = Product.objects.filter(owner=request.user)
   
    return render(request, "users/provider/productlistProvider.html", {"object_list": products})


# Download your payment into pdf

def render_to_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html  = template.render(context_dict)
	result = BytesIO()
	pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None

def getdata(request):
    current_user = request.user
    OrderList = Order.objects.filter(user=current_user,ordered=True)
    payment = Address.objects.filter(user=current_user,ordered=True)

    data = {
        "User name": current_user.username,
        "street_address": payment.street_address,
        "apartment_address": payment.apartment_address,
        "zipcode": payment.zip,


        "phone":current_user.profile.phone_number,
        "email": current_user.email,
        }
    return data
