from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.conf import settings
from django.db.models import Avg
import qrcode
from PIL import ImageFile, Image
from io import BytesIO
import qrcode
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import pre_save
from django.db.models.signals import post_save
import logging
from django.dispatch import receiver
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db import transaction







     
from django.contrib.auth import get_user_model
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
    nearby_delivery_agents = models.ManyToManyField('DeliveryAgent', blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_approved = models.CharField(
        max_length=20,
        choices=APPROVAL_CHOICES,
        default=PENDING,  # Default to Pending
    )

    def __str__(self):
        return self.business_name
    def assign_nearby_agents(self, nearby_agents):
        self.nearby_delivery_agents.clear()
        self.nearby_delivery_agents.add(*nearby_agents)

class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True) 
    # Add any customer-specific fields here

    def __str__(self):
        return self.user.email
    
class Route(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    Route_number = models.IntegerField()
    location = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return self.name
    
class DeliveryAgent(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    place = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    assigned_seller = models.ForeignKey(Seller, on_delete=models.CASCADE, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    distance = models.FloatField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    # assigned_route = models.ForeignKey(Route, null=True, blank=True, on_delete=models.SET_NULL)
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
    def calculate_average_rating(self):
        # Calculate the average rating for the product
        average_rating = self.reviews.aggregate(Avg('rating__rating'))['rating__rating__avg']
        return average_rating or 0.0

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

   

class Order(models.Model):
    class PaymentStatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESSFUL = 'successful', 'Successful'
        FAILED = 'failed', 'Failed'
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    
    products = models.ManyToManyField(Product)  
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    order_date = models.DateTimeField(auto_now_add=True)
    razorpay_order_id = models.CharField(max_length=255, default=1)
    
    payment_status = models.CharField(max_length=20, choices=PaymentStatusChoices.choices, default=PaymentStatusChoices.PENDING)

    def __str__(self):
       return self.user.name
#     def generate_qr_code(self):
#         # Only generate QR code if payment_status is successful and there is no existing QR code
#         if self.payment_status == self.PaymentStatusChoices.SUCCESSFUL and not self.qr_code:
#             # Generate QR code data based on order information
#             qr_code_data = f"Order ID: {self.id}, User: {self.user.name}, Total Price: ${self.total_price}"

#             # Create a QR code instance
#             qr = qrcode.QRCode(
#                 version=1,
#                 error_correction=qrcode.constants.ERROR_CORRECT_L,
#                 box_size=10,
#                 border=4,
#             )
#             qr.add_data(qr_code_data)
#             qr.make(fit=True)

#             # Create an image from the QR code
#             img = qr.make_image(fill_color="black", back_color="white")

#             # Save the image to a BytesIO buffer
#             buffer = BytesIO()
#             img.save(buffer, format="PNG")
#             buffer.seek(0)

#             # Save the QR code image to a file
#             image_name = f"order_{self.id}_qr_code.png"
#             self.qr_code.save(image_name, ContentFile(buffer.read()), save=True)

# # Connect the Order model's save method to generate the QR code when an order is saved
# @receiver(pre_save, sender=Order)
# def order_pre_save(sender, instance: Order, **kwargs):
#     instance.generate_qr_code()




class OrderItem(models.Model):
  
    order = models.ForeignKey(Order, on_delete=models.CASCADE, default=1)
    delivery_agent = models.ForeignKey(DeliveryAgent, blank=True, null=True, on_delete=models.SET_NULL)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    class DeliveryStatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_TRANSIT = 'in_transit', 'In Transit'
        DELIVERED = 'delivered', 'Delivered'

    delivery_status = models.CharField(
        max_length=20,
        choices=DeliveryStatusChoices.choices,
        default=DeliveryStatusChoices.PENDING,
    )
    delivery_date = models.DateTimeField(null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=1)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, default=1)  # Assuming the seller is also a User
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    def generate_qr_code(self):
        # Only generate QR code if payment_status is successful and there is no existing QR code
        # Only generate QR code if payment_status is successful and there is no existing QR code
        if not self.qr_code:
            # Use a database transaction to ensure the object is saved before retrieving the ID
            with transaction.atomic():
                # Reload the object to get the updated ID
                self.refresh_from_db()

                # Generate QR code data based on order information
                qr_code_data = f"OrderItem ID: {self.id}, Product: {self.product.name}, Total Price: ${self.total_price}"

                # Create a QR code instance
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_code_data)
                qr.make(fit=True)

            try:
                    # Create an image from the QR code
                img = qr.make_image(fill_color="black", back_color="white")

                    # Save the image to a BytesIO buffer
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)

                    # Save the QR code image to a file
                image_name = f"order_item_{self.id}_qr_code.png"
                self.qr_code.save(image_name, ContentFile(buffer.read()), save=True)
                return image_name, ContentFile(buffer.read())
            except Exception as e:
                    # Log the exception
                    logging.error(f"Error generating QR code for OrderItem ID {self.id}: {e}")
                    # Return default name and content
                    return f"default_qr_code_{self.id}.png", ContentFile(b"default content")

        # Return a default name and ContentFile if no QR code is generated
        return f"default_qr_code_{self.id}.png", ContentFile(b"default content")

    def assign_delivery_agent(self):
    # Get the associated seller
        seller = self.seller

        # Get all delivery agents associated with the seller
        delivery_agents = DeliveryAgent.objects.filter(seller=seller)

        # Iterate through delivery agents to find the one with the fewest assigned products
        min_assigned_agent = min(delivery_agents, key=lambda agent: OrderItem.objects.filter(
            seller=seller, delivery_agent=agent
        ).exclude(id=self.id).count())

        # Check if the selected delivery agent has fewer than 4 assigned products
        if OrderItem.objects.filter(seller=seller, delivery_agent=min_assigned_agent).count() < 4:
            self.delivery_agent = min_assigned_agent
        else:
            # If the selected delivery agent already has 4 or more assigned products, find another available agent
            available_agents = [agent for agent in delivery_agents if OrderItem.objects.filter(
                seller=seller, delivery_agent=agent
            ).exclude(id=self.id).count() < 4]

            if available_agents:
                self.delivery_agent = available_agents[0]
            else:
                # Handle the case when all agents have 4 or more assigned products
                # You may want to implement additional logic here (e.g., notify admin, log the issue)
                pass

        self.send_assignment_email()

        OrderItem.objects.filter(pk=self.pk).update(delivery_agent=self.delivery_agent)

    # def assign_delivery_agent(self):
    #     # Get the associated seller
    #     seller = self.seller

    #     # Get all delivery agents associated with the seller
    #     delivery_agents = DeliveryAgent.objects.filter(seller=seller)
        
    #     for agent in delivery_agents:
    #         assigned_products_count = OrderItem.objects.filter(
    #             seller=seller, delivery_agent=agent
    #         ).exclude(id=self.id).count()

    #         if assigned_products_count < 4:
    #             # Assign the next delivery agent to the order item
    #             self.delivery_agent = agent
    #             break
              
    #         else:
    #         # Find the delivery agent with the fewest assigned order items
    #             min_assigned_agent = min(delivery_agents, key=lambda agent: OrderItem.objects.filter(
    #             seller=seller, delivery_agent=agent
    #         ).exclude(id=self.id).count())

           
    #             self.delivery_agent = min_assigned_agent
    #     self.send_assignment_email()

    #     OrderItem.objects.filter(pk=self.pk).update(delivery_agent=self.delivery_agent)   
                
    
    def send_assignment_email(self):
        subject = 'Order Assignment'
        message = f'You have been assigned to deliver the product: {self.product.name}\n'
        message += f'To the user at address: {self.order.user.address}\n'
        message += 'Please proceed with the delivery as soon as possible.'

        from_email = 'mailtoshowvalidationok@gmail.com'  # Update with your email address
        to_email = self.delivery_agent.user.email

        send_mail(subject, message, from_email, [to_email])

    def save(self, *args, **kwargs):
        # Calculate the total price for this order item based on quantity and price
        self.total_price = self.quantity * self.price

        if not self.delivery_agent:
            self.assign_delivery_agent()

        super(OrderItem, self).save(*args, **kwargs)

        # Generate and save the QR code after the object is saved
        image_name, image_content = self.generate_qr_code()
        self.qr_code.save(image_name, image_content, save=False)

        # Update the total order price in the associated Order model
        order = self.order
        order.total_price = sum(order_item.total_price for order_item in order.orderitem_set.all())
        order.save()

# @receiver(pre_save, sender=OrderItem)
# def order_pre_save(sender, instance: OrderItem, **kwargs):
#      instance.generate_qr_code()
 
# @receiver(pre_save, sender=OrderItem)
# def order_pre_save(sender, instance: OrderItem, **kwargs):
#     # Pass the correct order_item_id when calling generate_qr_code
#     image_name, image_content = instance.generate_qr_code(instance.id)
    
#     if image_name and image_content:
#         instance.qr_code.save(image_name, image_content, save=False)


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
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    comment = models.TextField()


    def __str__(self):
        return f"Rating for Review ID {self.review.id}"
    
class Shippings(models.Model):
     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
     order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.SET_NULL)
     shipname = models.CharField(max_length=100, null=False, blank=False)
     shipaddress = models.TextField(blank=True, null=True)
     shipcity = models.TextField(blank=True, null=True)
     shippingpincode = models.IntegerField()

     def __str__(self):
        return self.shipname
     
NOTIFICATION_TYPES = [
    ('delivery_agent_assignment', 'Delivery Agent Assignment'),
    ('other_notification_type', 'Other Notification Type'),
    # Add more notification types as needed
]

class Notification(models.Model):
    recipient = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    delivery_agent = models.ForeignKey(DeliveryAgent, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES,null=True, blank=True)
    def __str__(self):
        return self.message
    
