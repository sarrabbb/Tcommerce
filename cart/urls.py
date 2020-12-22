from django.urls import path
from . import views
from django.conf.urls import include, url
from .views import (
    CheckoutView,
    PaymentView,
    cartdetail,
        AddCouponView,
    Pdf

)

urlpatterns = [
    # links 
    path('product/',include('products.urls')),

    # carts
    path('addCart/<int:id>/', views.addCart,name='addCart') ,
    path('removeFromCart/<int:id>/', views.removeFromCart,name='removeFromCart') ,
    path('removeSingleItemFromCart/<int:id>/', views.removeSingleItemFromCart,name='removeSingleItemFromCart') ,
    path('cartdetail/', cartdetail.as_view(), name='cartdetail'),

    # checkout
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('chargeCache/', views.chargeCache, name='chargeCache'), 

    # Coupon
    path('addCoupon/', AddCouponView.as_view(), name='addCoupon'),

    # refund
    path("request-refund/", views.RequestRefund, name='request-refund'),

    # pdf
    path("Pdf",Pdf.as_view(), name = 'Pdf')
    ]


