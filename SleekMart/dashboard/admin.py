from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# from .models import UserProfile
from .models import CustomUser, Seller, Customer, DeliveryAgent, Shippings
from .models import Category,Product, Subcategory,AddWishlist,WishlistItems,AddCart,CartItems,OrderItem, Order,Review,ReviewRating

# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'name', 'mobile', 'profile_pic', 'address')


# # Register the UserProfile model and its admin class
# admin.site.register(UserProfile, UserProfileAdmin)

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Subcategory)
admin.site.register(AddWishlist)
admin.site.register(WishlistItems)

# class SellerAdmin(admin.ModelAdmin):
#     list_display = ('business_name', 'is_approved')
#     list_filter = ('is_approved',)
#     search_fields = ('business_name',)

# class CustomerAdmin(admin.ModelAdmin):
#     list_display = ('user',)

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'name', 'mobile', 'role' ,'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'role')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'mobile', 'profile_pic', 'address', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'name')
    ordering = ('email',)

# Register the CustomUser model with the custom admin class
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Seller)
admin.site.register(Customer)
admin.site.register(DeliveryAgent)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(AddCart)
admin.site.register(CartItems)
admin.site.register(Review)
admin.site.register(ReviewRating)
admin.site.register(Shippings)