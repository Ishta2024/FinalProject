from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.conf import settings
# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)
#     mobile = models.CharField(max_length=15)
#     profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
#     address = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return self.name
class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, mobile=None, role=None):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, mobile=mobile, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, role=None, mobile=None):
        role='admin'
        user = self.create_user(email=email, name=name, password=password, role=role, mobile=mobile)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):

    USER_ROLES = (
        ('customer', 'Customer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
        ('delivery_agent', 'Delivery Agent'),
    )
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100,null=True, blank=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    role = models.CharField(max_length=15, choices=USER_ROLES, blank=True, null=True,default='customer')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

class Seller(models.Model):
    APPROVED = 'approved'
    DECLINED = 'declined'
    PENDING = 'pending'
    
    APPROVAL_CHOICES = [
        (APPROVED, 'Approved'),
        (DECLINED, 'declined'),
        (PENDING, 'Pending'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=100)
    business_address = models.TextField()
    business_website = models.URLField(blank=True, null=True)
    seller_proof = models.FileField(upload_to='seller_proofs/')
    is_approved = models.CharField(
        max_length=20,
        choices=APPROVAL_CHOICES,
        default=PENDING,  # Default to Pending
    )

    def __str__(self):
        return self.business_name

class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    # Add any customer-specific fields here

    def __str__(self):
        return self.user.email
    
class Category(models.Model):
    slug = models.CharField(max_length=50, null=False, blank=False)
    name=models.CharField(max_length=50, null=False, blank=False)
    image=models.ImageField(upload_to="category_images", null=False, blank=False)
    status=models.BooleanField(default=False, help_text="0=default,1=Hidden")
    trending=models.BooleanField(default=False, help_text="0=default,1=Hidden")
    description=models.CharField(max_length=500, null=False, blank=False, default="Default description")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=False, blank=False)
    description = models.CharField(max_length=500, null=False, blank=False, default="Default subcategory description")
    image = models.ImageField(upload_to="subcategory_images", null=False, blank=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False, help_text="0=default, 1=Hidden")
    trending = models.BooleanField(default=False, help_text="0=default, 1=Trending")

    def __str__(self):
        return self.name

class Product(models.Model):
    # category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, null=True, blank=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    slug = models.CharField(max_length=100, null=False, blank=False)
    name=models.CharField(max_length=100, null=False, blank=False)
    product_image=models.ImageField(upload_to="product_images", null=False, blank=False)
    description = models.CharField(max_length=500, null=False, blank=False)
    quantity = models.IntegerField(null=False, blank=False)
    original_price = models.FloatField(null=False, blank=False)
    selling_price = models.FloatField(null=False, blank=False)
    status = models.BooleanField(default=False, help_text="0=default,1=Hidden")
    trending = models.BooleanField(default=False, help_text="0=default,1=Trending")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def reduce_quantity(self, quantity_to_reduce):
        """
        Reduce the product quantity.
        """
        # Ensure quantity_to_reduce is an integer
        quantity_to_reduce = int(quantity_to_reduce)

        # Ensure self.quantity is an integer
        self.quantity = int(self.quantity)

        if quantity_to_reduce <= self.quantity:
            self.quantity -= quantity_to_reduce
            self.save()
            return True
        return False

    def __str__(self):
        return self.name

class AddWishlist(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    wishlist_date = models.DateTimeField(auto_now_add=True)
    # products = models.ForeignKey(Product, on_delete=models.CASCADE, default=None)
    
    def __str__(self):
       return self.user.name
    
class WishlistItems(models.Model):
    wishlist = models.ForeignKey(AddWishlist, on_delete=models.CASCADE)
    products = models.ForeignKey(Product, on_delete=models.CASCADE)
    def __str__(self):
       return self.products.name

class Rating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Assuming you have a Product model
    rating = models.IntegerField(choices=[(1, '1 star'), (2, '2 stars'), (3, '3 stars'), (4, '4 stars'), (5, '5 stars')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.name} rated {self.product.name} {self.get_rating_display()}'
    

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Order #{self.id} by {self.user.email}"
    

class OrderItem(models.Model):
    CONFIRMED = 'confirmed'
    CANCELED = 'canceled'
    PENDING = 'pending'

    ORDER_CONFIRMATION_CHOICES = [
        (CONFIRMED, 'Confirmed'),
        (CANCELED, 'Canceled'),
        (PENDING, 'Pending'),
    ]

    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order_confirmation = models.CharField(
        max_length=20,
        choices=ORDER_CONFIRMATION_CHOICES,
        default=PENDING,
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.order_confirmation == OrderItem.CONFIRMED:
            self.product.reduce_quantity(self.quantity)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"
    
class AddCart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE) 
    cart_date = models.DateTimeField(auto_now_add=True)
    order = models.OneToOneField(Order, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.user.email

class CartItems(models.Model):
    cart = models.ForeignKey(AddCart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    cart_item_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.SET_NULL)
    order_item = models.ForeignKey(OrderItem, null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        # Calculate the total price based on the quantity and the price of the associated product
        if self.product:
            self.total_price = self.quantity * self.product.selling_price
        super().save(*args, **kwargs)
    
class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.name}"
    
class ReviewRating(models.Model):
    review = models.OneToOneField(Review, related_name='rating', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=0)  # Rating out of 5
    comment = models.TextField()

    def __str__(self):
        return f"Rating for Review ID {self.review.id}"