from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [



    # all users
    path("productlist", views.productlist, name="productlist"),
    path("search", views.search, name="search"),
    path("filter_category", views.filter_category, name="filter_category"),
    path("productdetails/<int:id>/", views.productdetails, name="productdetails"),

    # get_previous_page
    path("get_previous_page", views.get_previous_page, name="get_previous_page"),

    # provider
    # products
    path("addproduct", views.addproduct, name="addproduct"),
    path("delete/<int:id>/", views.deleteProduct, name="deleteProduct"),
    path("updateproduct/<int:id>/", views.updateproduct, name="updateproduct"),
    path("productlistProvider", views.productlistProvider, name="productlistProvider"),

    # catrgory
    path('addcategory', views.addcategory,name='addcategory'),
    path('searchCategory',views.searchCategory,name='searchCategory'),
    path('deletecategory/<int:id>/',views.deletecategory,name='deletecategory'),
    path('categorydetails/<int:id>/',views.categorydetails,name='categorydetails'),
    path('updatecategory/<int:id>/',views.updatecategory,name='updatecategory'),
    path('categorylistProvider',views.categorylistProvider,name='categorylistProvider'),

    # comments
    path('allcomments',views.CommentListProvider,name='allcomments'),
    path('filter_comment',views.filter_comment , name='filter_comment'),

    # flash
    path('flash',views.FlashVenteList,name='flash'),
    path('add_Flash',views.add_Flash,name='add_Flash'),

   
    # admin
    # comments
    path('comments',views.CommentList,name='comments'),
    path('commentsProvider',views.commentsProvider,name='commentsProvider'),
    path('deleteComment/<int:id>/',views.DeleteComment,name='deleteComment'),
    path('signaler_comment/<int:id>/',views.signaler_comment,name='signaler_comment'),
    path('signaler_comment/<int:id>/',views.signaler_comment_provider,name='signaler_comment_provider'),
    
    # category
    path('categorylist',views.categorylist,name='categorylist'),
    path('categoryinfo/<int:id>/',views.categorydetailsAdmin,name='categoryinfo'),

    # products
    path('productlistAdmin',views.productlistAdmin,name='productlistAdmin'),
    
    # flash sales
    path('Flash_sales',views.Flash_sales,name='Flash_sales'),
    path('add_Flash_sales',views.add_Flash_sales_admin,name='add_Flash_sales'),
    path('update_Flash_sales/<int:id>/',views.update_Flash_sales,name='update_Flash_sales'),
    path('view_flash_sales/<int:id>/', views.view_flash_sales ,name='view_flash_sales'),
    path('delete_Flash_sales/<int:id>/' , views.delete_Flash_sales , name='delete_Flash_sales'),
    path('accepteFalsh_sales/<int:id>/',views.accepteFalsh_sales,name='accepteFalsh_sales'),

    # Coupon
    path('coupon',views.CouponList, name='coupon'),
    path('addCouponAdmin',views.addCouponAdmin,name='addCouponAdmin'),
    path('update_Coupon/<int:id>/',views.update_Coupon,name='update_Coupon'),
    path('delete_Coupon/<int:id>/',views.delete_Coupon,name='delete_Coupon'),

    # refund
    path("refundlist/", views.refundlist, name='refundlist'),
    path("DeclineRefund/<int:id>/", views.DeclineRefund, name='DeclineRefund'),
    path("acceptRefund/<int:id>/", views.acceptRefund, name='acceptRefund'),

    # payment
    path("paymentlist",views.paymentlist,name="paymentlist"),
]
