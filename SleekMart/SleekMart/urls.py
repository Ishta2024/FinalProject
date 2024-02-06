"""
URL configuration for SleekMart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from dashboard.views import signup_redirect
from dashboard.views import ResetPasswordView, ChangePasswordView
from dashboard import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.views import LoginView
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('',  views.dashboard_home, name='dashboard_home'),
    path('products/<int:category_id>/' , views.products, name='products'),
    path('each_product/<int:product_id>/' , views.each_product, name='each_product'),
    path('addproduct' , views.addproduct, name='addproduct'),
    path('single_product/<int:subcategory_id>/' , views.single_product, name='single_product'),

    path('remove_from_wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('plus_wishlist', views.plus_wishlist, name='plus_wishlist'),
    # path('rate_product/', views.rate_product, name='rate_product'),
    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    path('minus_wishlist', views.minus_wishlist, name='minus_wishlist'),


    path('search/', views.search, name='search'),
    path('delivery_agent_dashboard/', views.delivery_agent_dashboard, name='delivery_agent_dashboard'),
    path('da_details/', views.da_details, name='da_details'),
    path('edit_details/', views.edit_details, name='edit_details'),
    path('display_nearby_agents/<int:seller_id>/', views.display_nearby_agents, name='display_nearby_agents'),
    path('display_nearby_agents_map/<int:seller_id>/', views.display_nearby_agents_map, name='display_nearby_agents_map'),
    path('search_products/', views.search_products, name='search_products'),
    path('generate_report/', views.generate_report, name='generate_report'),

    
    path('checkout/', views.checkout, name='checkout'),
    path('buy_now/<int:product_id>/' , views.buy_now, name='buy_now'),
    path('checkout_complete', views.checkout_complete, name='checkout_complete'),
    path('buyNowComplete/<int:product_id>/<int:quantity>', views.buyNowComplete, name='buyNowComplete'),
    path('create_order/', views.create_order, name='create_order'),
    path('order_list/', views.order_list, name='order_list'),
    path('remove_from_order/<int:item_id>/<int:cart_item_id>/', views.remove_from_order, name='remove_from_order'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order_placed_successfully/<int:order_id>/', views.order_placed_successfully, name='order_placed_successfully'),
    path('cancel_order_confirmation/<int:order_id>/', views.cancel_order_confirmation, name='cancel_order_confirmation'),
    path('single_cancel_order/<int:order_id>/', views.single_cancel_order, name='single_cancel_order'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('order_history', views.order_history, name='order_history'),
    path('orders/', views.orders, name='orders'),
    path('details_order/<int:order_id>/', views.details_order, name='details_order'),
    path('confirm_order/<int:product_id>/', views.ConfirmOrderView.as_view(), name='single_confirm_order'),
    path('order_details/<int:order_item_id>/', views.OrderDetailsView.as_view(), name='order_details'),
    path('order_itemdetails/<int:order_id>/', views.order_itemdetails, name='order_itemdetails'),
    path('delivery_order_itemdetails/<int:order_id>/', views.delivery_order_itemdetails, name='delivery_order_itemdetails'),
    path('generate_bill/<int:order_item_id>/', views.GenerateBillPDF.as_view(), name='generate_bill'),
    
    # path('buy_now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('update_delivery_status/', views.update_delivery_status, name='update_delivery_status'),
    path('update_order_status/', views.update_order_status, name='update_order_status'),
    path('add_review/<int:product_id>/', views.add_review, name='add_review'),
    path('reviews', views.reviews, name='reviews'),
    path('sellerreviews', views.sellerreviews, name='sellerreviews'),
    path('seller_orders', views.seller_orders, name='seller_orders'),
    path('delivery_orders', views.delivery_orders, name='delivery_orders'),

    path('contact' , views.contact, name='contact'),
    path('about' , views.about, name='about'),
    path('login_page/',  views.login_page, name='login_page'),
    path('register/',  views.register, name='register'),
    path('profile',  views.profile, name='profile'),


    path('custnotification_page',  views.custnotification_page, name='custnotification_page'),
    path('sellernotification_page',  views.sellernotification_page, name='sellernotification_page'),
    path('sellregister/',  views.sellregister, name='sellregister'),
    path('seller_details/<int:seller_id>/', views.seller_details, name='seller_details'),
    path('blockcustomer/<int:user_id>/', views.blockcustomer, name='blockcustomer'),
    path('unblockcustomer/<int:user_id>/', views.unblockcustomer, name='unblockcustomer'),
    path('editseller/', views.editseller, name='editseller'),
    path('sellerprofile', views.sellerprofile, name='sellerprofile'),
    path('sellerslist',  views.sellerslist, name='sellerslist'),
    path('sellerindex',  views.sellerindex, name='sellerindex'),

    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart_details/', views.cart_details, name='cart_details'),
    # path('update_cart_item_quantity/', views.update_cart_item_quantity, name='update_cart_item_quantity'),
    path('update_cart_item/<int:cart_item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove_cart_item/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
    # path('checkout/', views.checkout, name='checkout'),

    path('get_subcategories/', views.get_subcategories, name='get_subcategories'),
    path('index',  views.index, name='index'),
    path('productlist',  views.productlist, name='productlist'),
    path('view_detail/<int:product_id>/',  views.view_detail, name='view_detail'),
    path('categories/',  views.categories, name='categories'),
    path('subcategories/',  views.subcategories, name='subcategories'),
    path('add_da/',  views.add_da, name='add_da'),
    path('add_route/',  views.add_route, name='add_route'),
    path('view_da', views.view_da, name='view_da'),
    path('delivery_agent_details/<int:delivery_agent_id>/', views.delivery_agent_details, name='delivery_agent_details'),


    path('edit_subcategory/<int:subcategory_id>/',  views.edit_subcategory, name='edit_subcategory'),
    path('delete_subcategory/<int:subcategory_id>/',  views.delete_subcategory, name='delete_subcategory'),
    path('edit_profile/',  views.edit_profile, name='edit_profile'),
    path('view_customer',  views.view_customer, name='view_customer'),
    path('view_products_by_category/<slug:category_slug>/', views.view_products_by_category, name='view_products_by_category'),
    path('editproduct/<int:product_id>/', views.editproduct, name='editproduct'),
    path('productdelete/<int:product_id>/', views.productdelete, name='productdelete'),

    path('filter_orders/', views.filter_orders, name='filter_orders'),
    path('order_tracking/<int:order_item_id>/', views.order_tracking, name='order_tracking'),
    path('filter_orders_by_status/', views.filter_orders_by_status, name='filter_orders_by_status'),
    path('add_delivery_agent_review/<int:delivery_agent_id>/', views.add_delivery_agent_review, name='add_delivery_agent_review'),
    path('delivery_agent_reviews/<int:delivery_agent_id>/', views.delivery_agent_reviews, name='delivery_agent_reviews'),

    path('delete_customer/<int:customer_id>/',  views.delete_customer, name='delete_customer'),
    path('delete_customer/<int:customer_id>/',  views.delete_customer, name='delete_customer'),
    path('update_category/<slug:category_slug>/',  views.update_category, name='update_category'),
    path('delete_category/<slug:category_slug>/',  views.delete_category, name='delete_category'),
    path('approveseller/<int:seller_id>/', views.approveseller, name='approveseller'),
    path('rejectseller/<int:seller_id>/', views.rejectseller, name='rejectseller'),
    path('notifications/', views.notifications, name='notifications'),

    path('loggout',  views.loggout, name='loggout'),
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),

    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),

    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),

    path('password-change/', ChangePasswordView.as_view(), name='password_change'),
    # path('social-auth/', include('social_django.urls', namespace='social'))
    path("", include("allauth.urls")),
    path('social/signup/', signup_redirect, name='signup_redirect'),

    path('paymenthandler/cart/', views.paymenthandler,{'cart_order': True}, name='paymenthandler'),

    # For buy now (single product) orders
    path('paymenthandler/buynow/', views.paymenthandler, {'cart_order': False}, name='paymenthandler'),


]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
