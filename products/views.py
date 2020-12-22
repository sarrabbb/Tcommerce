from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category , FlashSales 
from .forms import ProductForm , CategoryForm , FlashSalesForm
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import Http404
from comments.models import Comment , CommentProvider
from comments.forms import CommentForm 
from cart.models import Coupon , Refunds as Refund
from cart.forms import CouponForm
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required , user_passes_test
from django.contrib import messages
from django.views.generic import ListView
from registration.decorators import provider_required , buyer_required
from datetime import date
from django.core.mail import send_mail
from django.conf import settings

from django.http import HttpResponse , HttpResponseRedirect
import _datetime
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

from django.core.mail import send_mail

from cart.models import Order , Payment

# Create your views here.


# all user features
def index(request):
    today = _datetime.date.today()
    products = Product.objects.all()
    Categories_list = Category.objects.all()

    vents_flash = FlashSales.objects.filter(approved = True)
    return render(request, "index.html" ,{"vents_flash": vents_flash, "products": products,"Categories_list": Categories_list},)

# view product list
# @register.filter
def in_category(things, category):
    return things.filter(category=category)

def productlist(request):
    Categories_list = Category.objects.all()
    products = Product.objects.all()
    productsPage = Product.objects.all()

    paginator = Paginator(productsPage, 2)
    page = request.GET.get("page")
    productsPage = paginator.get_page(page)

    return render(
        request,
        "products/productlist.html",
        {"Categories_list": Categories_list, "items": productsPage},
    )

# search by keyword : product name 
def search(request):

    Categories_list = Category.objects.all()
    productsPage = Product.objects.all()

    paginator = Paginator(productsPage, 2)
    page = request.GET.get("page")
    productsPage = paginator.get_page(page)

    if request.method == "GET":
        query = request.GET.get("q")
        if query:
            productsRslt = Product.objects.filter(Q(name__contains=query))
            return render(
                request, "products/filterProducts.html",
                {"productsRslt": productsRslt,"items": productsPage,"Categories_list": Categories_list}
            )
        else:
            return render(request, "products/notfoundsearch.html")
    else:
        return render(request, "products/productlist.html", {})


# filter by category : one or many checkbox 
def filter_category(request):

    Categories_list = Category.objects.all()
    filter_category = request.GET.getlist('filter')
    productsPage = Product.objects.all()

    paginator = Paginator(productsPage, 2)
    page = request.GET.get("page")
    productsPage = paginator.get_page(page)
    if filter_category:
        categoryFilter = Category.objects.filter(title__in=filter_category)
        products = Product.objects.filter(category__in=categoryFilter)
        return render(
            request, 
            "products/filterProducts.html",
            {"filterRslt": products,"items": productsPage,"Categories_list": Categories_list}
        )
    
    # if no checkbox is selected
    else :
        
        return render(
        request,
        "products/productlist.html",
        {"Categories_list": Categories_list, "items": productsPage},
    )
    

# user features
# products

def productdetails(request, id):

    try:
        product = Product.objects.get(pk=id)
        current_user = request.user
        # adding a comment
        comments = Comment.objects.filter(product=product)
        new_comment = None
        if request.method == "POST":
            comment_form = CommentForm(data=request.POST)
            if comment_form.is_valid():

                # Create Comment object but don't save to database yet
                new_comment = comment_form.save(commit=False)
                # Assign the current product to the comment
                new_comment.product = product
                # Assign the current user to the comment
                new_comment.user = current_user
                # Save the comment to the database
                new_comment.save()
            return redirect("productdetails", id=id)

        else:
            comment_form = CommentForm()
    except Product.DoesNotExist:
        return render(request, "products/notfoundsearch.html")

    return render(
        request,
        "products/productdetails.html",
        {
            "product": product,
            "comments": comments,
            "comment_form": comment_form,
            "new_comment": new_comment,
        },
    )


# provider features 
# CRUD PRODUCT

@login_required
@provider_required
def productlistProvider(request):
    products = Product.objects.filter(owner=request.user)
    productsPage = Product.objects.filter(owner=request.user)
    paginator = Paginator(productsPage, 2)
    page = request.GET.get("page")
    productsPage = paginator.get_page(page)

    return render(request, "users/provider/productlistProvider.html", {"object_list": products, "items": productsPage})


@login_required
@provider_required
def addproduct(request):

    if request.method == "GET":
        form = ProductForm()
        return render(request, "products/addproduct.html", {"form": form})
    else:
        form = ProductForm(request.POST, request.FILES)
        
        if form.is_valid():
            product = form.save(commit = False)
            product.owner = request.user
            product.name = form.cleaned_data.get("name")
            product.description = form.cleaned_data.get("description")
            product.price = form.cleaned_data.get("price")
            product.quantity = form.cleaned_data.get("quantity")
            productimage = form.cleaned_data.get("image")
            product.save()
            return redirect("provider")
        else:
            print(form.errors)
        return redirect("addproduct")

@login_required
@provider_required
def deleteProduct(request, id):
    product = Product.objects.get(pk=id)
    product.delete()
    return redirect("productlistProvider")

@login_required
@provider_required
def updateproduct(request, id):

    product = get_object_or_404(Product, pk=id)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect("productlistProvider")
    return render(request, "products/updateproduct.html", {"form": form})

# put a product on flashsales


def product_flashsales(request):
    if request.method == "POST":
        form = FlashSalesForm(request.POST or None)
        user = request.user
        if form.is_valid():
            form.save()
            
        else:
            print(form.errors)
    else:
        form = FlashSalesForm()
        return render(request, "flash_sales/addflashsales.html", {"form": form})

# CRUD CATEGORY

@login_required
@provider_required
def categorylistProvider(request):

    categorys = Category.objects.filter(owner=request.user)
    categoryPage = Category.objects.filter(owner=request.user)
    paginator = Paginator(categoryPage, 2)
    page = request.GET.get('page')
    categoryPage = paginator.get_page(page)

    return render(request,'users/provider/categorylistProvider.html',{'object_list':categorys})

@login_required
@provider_required
def addcategory(request):

    if request.method=='GET':
        form = CategoryForm()
        return render(request, 'categories/addcategory.html',{'form':form})
    else:
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit = False)
            category.owner = request.user
            category.name = form.cleaned_data.get("name")
            category.description = form.cleaned_data.get("description")
            form.save()
            return redirect('categorylistProvider')
        else:
            print(form.errors)
        return redirect('addcategory')
        

@login_required
@provider_required
def deletecategory(request,id):

    category = Category.objects.get(pk=id)
    category.delete()
    return redirect('categorylistProvider')


@login_required
@provider_required
def updatecategory(request,id):
    
    category = get_object_or_404(Category, pk=id)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        return redirect('categorylistProvider')
    return render(request, 'categories/updatecategory.html', {'form': form})

@login_required
@provider_required
def categorydetails(request,id):
    try:
        category = get_object_or_404(Category, pk=id)
        return render(request,'categories/categorydetails.html',{'category':category})

    except ObjectDoesNotExist:
        messages.warning(request,'You dont have that category')
        return render(request, 'categories/categorydetails.html')

@login_required
@provider_required
def searchCategory(request):  

    if request.method == 'GET':    
        query = request.GET.get('q') 
        if query:
            categoryRslt = Category.objects.filter(Q(name__contains=query)) 

            return render(request,'users/provider/categorylistProvider.html',{"categoryRslt":categoryRslt})
        else:
            return render(request,'products/notfoundsearch.html')
    else:
        return render(request,"users/provider/categorylistProvider.html",{})

# Comments
@login_required
@provider_required
def CommentListProvider(request):
    products = Product.objects.filter(owner=request.user)
    c = Comment.objects.all().filter(product__in=products)
    return render(request, "users/provider/comments.html", { "comments" : c})

# flash vents
@login_required
@provider_required
def FlashVenteList(request):
    products = Product.objects.filter(owner=request.user)
    flashventes = FlashSales.objects.all().filter(product__in=products)
    return render(request, "users/provider/flashventes.html", { "flash" : flashventes})

@login_required
@provider_required
def add_Flash(request):

    if request.method == "GET":
        form = FlashSalesForm()
        return render(request, "flash_sales/addflashsales.html", {"form": form})
    else:
        form = FlashSalesForm(request.POST or None)
        
        if form.is_valid():
            form.save()
            return redirect("flash")
        else:
            print(form.errors)
            return redirect("add_Flash")
    
# admin features
#  comments
@user_passes_test(lambda u: u.is_superuser)
def CommentList(request):
    c = Comment.objects.all()
    return render(request, "users/admin/comments.html", { "comments" : c})

@user_passes_test(lambda u: u.is_superuser)
def DeleteComment(request,id):
    comment = get_object_or_404(Comment, pk=id)
    comment.delete()
    return redirect("comments")

@user_passes_test(lambda u: u.is_superuser)
def signaler_comment(request,id):
    comment = get_object_or_404(Comment, pk=id)
    comment.flag = True 
    comment.save()
    return redirect("comments")


@user_passes_test(lambda u: u.is_superuser)
def signaler_comment_provider(request,id):
    comment = get_object_or_404(CommentProvider, pk=id)
    comment.flag = True 
    comment.save()
    return redirect("commentsProvider")

@user_passes_test(lambda u: u.is_superuser)
def commentsProvider(request):
    c = CommentProvider.objects.all()
    return render(request, "users/admin/commentsProvider.html", { "comments" : c})


@user_passes_test(lambda u: u.is_superuser)
def filter_comment(request):
    value = request.GET['filter']

    if value:
        reslut = CommentProvider.objects.filter(flag=value)
        return render(
            request, 
            "users/admin/commentsProvider.html",
            { "comments" :reslut }
        )
    
    # if no checkbox is selected
    else :
        return redirect('commentsProvider')
        

# View category list

@user_passes_test(lambda u: u.is_superuser)
def categorylist(request):

    categorys = Category.objects.all()
    categoryPage = Category.objects.all()
    paginator = Paginator(categoryPage, 2)
    page = request.GET.get('page')
    categoryPage = paginator.get_page(page)

    return render(request,'users/admin/categorylist.html',{'object_list':categorys,'items':categoryPage})


# View product list

@user_passes_test(lambda u: u.is_superuser)
def productlistAdmin(request):
    products = Product.objects.all()
    productsPage = Product.objects.all()
    paginator = Paginator(productsPage, 2)
    page = request.GET.get("page")
    productsPage = paginator.get_page(page)

    return render(request, "users/admin/productlist.html", {"object_list": products, "items": productsPage})


@user_passes_test(lambda u: u.is_superuser)
def categorydetailsAdmin(request,id):
    try:
        category = get_object_or_404(Category, pk=id)
        return render(request,'users/admin/categorydetails.html',{'category':category})

    except ObjectDoesNotExist:
        messages.warning(request,'You dont have that category')
        return render(request, 'users/admin/categorydetails.html')

# FlashSales




@property
def is_past_due(self):
    today = _datetime.date.today()
    return today > self.date
    

@user_passes_test(lambda u: u.is_superuser)
def Flash_sales(request):
    flash = FlashSales.objects.all()
    return render(request, "users/admin/flash_sales.html", {"flash": flash})


@user_passes_test(lambda u: u.is_superuser)
def accepteFalsh_sales(request,id):
    
    # accepter vente flash
    flash = get_object_or_404(FlashSales, pk=id)
    flash.approved = True
    flash.save()

    # notify provider
    product = flash.product
    owner = product.owner
    recipient_list = owner.email

    subject = 'Flash Vente'
    message = ' Your request has been approved '
    email_from = settings.EMAIL_HOST_USER
    send_mail( subject, message, email_from, [recipient_list] )
    
    return redirect('Flash_sales')


@user_passes_test(lambda u: u.is_superuser)
def add_Flash_sales_admin(request):

    if request.method == "GET":
        form = FlashSalesForm()
        return render(request, "flash_sales/addflashsales.html", {"form": form})
    else:
        form = FlashSalesForm(request.POST or None)
        
        if form.is_valid():
            form.save()
            return redirect("Flash_sales")
        else:
            print(form.errors)
        return redirect("add_Flash_sales")


@user_passes_test(lambda u: u.is_superuser)
def update_Flash_sales(request, id):

    flash = get_object_or_404(FlashSales, pk=id)
    form = FlashSalesForm(request.POST or None, instance=flash)
    if form.is_valid():
        form.save()
        return redirect('Flash_sales')
    return render(request, 'flash_sales/updateflash.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def view_flash_sales(request,id):
    try:
        Flash = get_object_or_404(FlashSales, pk=id)
        return render(request,'flash_sales/flashdetails.html',{'Flash':Flash})

    except ObjectDoesNotExist:
        messages.warning(request,'You dont have that FlashSales')
        return render(request, 'users/admin/flash_sales.html')

@user_passes_test(lambda u: u.is_superuser)
def delete_Flash_sales(request,id):
    Flash = get_object_or_404(FlashSales, pk=id)
    Flash.delete()
    return redirect("Flash_sales")

    
def get_previous_page(request):
     # redirect to the same page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# coupon
@user_passes_test(lambda u: u.is_superuser)
def CouponList(request):
    coupon = Coupon.objects.all()
    return render(request, "users/admin/couponlist.html", {"coupon": coupon})

@user_passes_test(lambda u: u.is_superuser)
def addCouponAdmin(request):
    if request.method == "GET":
        form = CouponForm()
        context = {
            'form': form
        }
        return render(request, "coupon/add_coupon.html", context)

    else:
        form = CouponForm(request.POST or None)

        if form.is_valid():
            coupon = Coupon()
            coupon.code = form.cleaned_data.get('code')
            coupon.amount = form.cleaned_data.get('amount')
            coupon.save()
            return redirect("coupon")
        else:
            print(form.errors)
            return redirect("addCoupon")

@user_passes_test(lambda u: u.is_superuser)
def update_Coupon(request, id):
    coupon = get_object_or_404(Coupon, pk=id)
    form = CouponForm(request.POST or None, instance=coupon)
    if form.is_valid():
        form.save()
        return redirect('coupon')
    return render(request, 'coupon/updatecoupon.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def delete_Coupon(request,id):
    coupon = get_object_or_404(Coupon, pk=id)
    coupon.delete()
    return redirect('coupon')

# refund
@user_passes_test(lambda u: u.is_superuser)
def refundlist(request):
    refund = Refund.objects.all()
    return render(
        request,
        "users/admin/refundlist.html",
        {"refund": refund}
    )

@user_passes_test(lambda u: u.is_superuser)
def acceptRefund(request,id):
    refund = get_object_or_404(Refund,pk=id)
    refund.accepted = True
    refund.save()

    # notify the user
    recipient_list = refund.email

    subject = 'Refund item'
    message = ' Your request has been approved , we will call you as soon as possible'
    email_from = settings.EMAIL_HOST_USER
    send_mail( subject, message, email_from, [recipient_list] )
    return redirect('refundlist')

@user_passes_test(lambda u: u.is_superuser)
def DeclineRefund(request,id):
    refund = get_object_or_404(Refund,pk=id)
    refund.accepted = False
    refund.save()

    # notify the user
    recipient_list = refund.email

    subject = 'Refund item'
    message = ' Your request of the refund is not accepted'
    email_from = settings.EMAIL_HOST_USER
    send_mail( subject, message, email_from, [recipient_list] )
    return redirect('refundlist')

# payment list
@user_passes_test(lambda u: u.is_superuser)
def paymentlist(request):
    payment = Payment.objects.all()
    return render(
        request,
        "users/admin/paymentlist.html",
        {"payment": payment}
    )
