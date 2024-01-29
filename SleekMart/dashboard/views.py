from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .models import Customer, CustomUser, Seller, AddWishlist,WishlistItems,AddCart, CartItems, Order, OrderItem, Review, ReviewRating
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Category, Product, Subcategory, Shippings, DeliveryAgent, Notification
from django.urls import reverse
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.db.models import F
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.db.models import F, FloatField,Func
from django.db.models.functions import Cos, Radians, Sin
class Acos(Func):
    function = 'ACOS'


# Create your views here.
from django.http import HttpResponse
def dashboard_home(request):
    categories = Category.objects.filter(status=False)
    category_data = []
    cart_count = 0  # Default to 0
    categories_with_subcategories = Category.objects.filter(subcategory__isnull=False, status=False)

    if request.user.is_authenticated:
        user = request.user
        cart_count = CartItems.objects.filter(cart__user=user).count()
    
    for category in categories:
        subcategories = Subcategory.objects.filter(category=category, status=False)
        products = Product.objects.filter(subcategory__in=subcategories, status=False)
        category_data.append({
            'category': category,
            'products': products,
            'subcategories': subcategories,
        })
    
    context = {
        'category_data': category_data,
        'categories': categories,
        'cart_count': cart_count,
        'categories_with_subcategories' : categories_with_subcategories
    }
    
    return render(request, 'dashboard_home.html', context)

def products(request, category_id):
    categories = Category.objects.filter(status=False)
    category = get_object_or_404(Category, id=category_id)
    subcategories = Subcategory.objects.filter(category=category,status=False)
    products = Product.objects.filter(subcategory__in=subcategories, status=False)
    cart_count = 0  # Default to 0
    wishlist_count = 0
    wishlist = None
    if request.user.is_authenticated:
        user = request.user
        user_id = request.user.id
        cart_count = CartItems.objects.filter(cart__user=user).count()
        wishlist = WishlistItems.objects.filter(wishlist__user_id=user_id).values_list('products__id', flat=True)
        wishlist_count = WishlistItems.objects.filter(wishlist__user=request.user).count()
    context = {
        'category':category,
        'subcategories': subcategories,
        'products': products,
        'categories':categories,
        'cart_count' : cart_count,
        'wishlist': wishlist,
        'wishlist_count': wishlist_count
    }
    return render(request,'products.html', context)
def about(request):
    categories = Category.objects.filter(status=False)
    # category = get_object_or_404(Category, id=category_id)
    # subcategories = Subcategory.objects.filter(category=category,status=False)
    # products = Product.objects.filter(subcategory__in=subcategories, status=False)
    cart_count = 0  # Default to 0
    wishlist_count = 0
    wishlist = None
    if request.user.is_authenticated:
        user = request.user
        user_id = request.user.id
        cart_count = CartItems.objects.filter(cart__user=user).count()
        wishlist = WishlistItems.objects.filter(wishlist__user_id=user_id).values_list('products__id', flat=True)
        wishlist_count = WishlistItems.objects.filter(wishlist__user=request.user).count()
    context = {
        # 'category':category,
        # 'subcategories': subcategories,
        # 'products': products,
        'categories':categories,
        'cart_count' : cart_count,
        'wishlist': wishlist,
        'wishlist_count': wishlist_count
    }
    return render(request,'about.html',context)
def contact(request):
    return render(request,'contact.html')

def search(request):
  
    search_term = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=search_term)
    return render(request, "Customer/search.html", {'search_term': search_term, 'products': products})
from django.core import serializers
def search_products(request):
    search_query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=search_query)
    serialized_products = serializers.serialize('json', products, fields=('id', 'name'))
    return JsonResponse({'products': serialized_products}, safe=False)

def single_product(request, subcategory_id):
    categories = Category.objects.filter(status=False)
    subcategory = get_object_or_404(Subcategory, id=subcategory_id)
    products = Product.objects.filter(subcategory=subcategory, status=False)
    cart_count = 0
    wishlist_count = 0  # Initialize wishlist_count to 0
    wishlist = []  # Initialize an empty list for the user's wishlist

    # Check if the user is authenticated
    if request.user.is_authenticated:
        user_id = request.user.id
        user=request.user
        # Fetch the user's wishlist products' IDs and count
        cart_count = CartItems.objects.filter(cart__user=user).count()
        # Fetch the user's wishlist products' IDs and count
        wishlist = WishlistItems.objects.filter(wishlist__user_id=user_id).values_list('products__id', flat=True)
        wishlist_count = WishlistItems.objects.filter(wishlist__user=request.user).count()

    context = {
        'categories': categories,
        'subcategory': subcategory,
        'products': products,
        'wishlist': wishlist,
        'wishlist_count': wishlist_count,
        'cart_count': cart_count,  # Pass the user's wishlist count to the template
    }
    return render(request, 'single-product.html', context)



def each_product(request, product_id):
    categories=Category.objects.filter(status=False)
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
     quantity=request.POST.get('quantity')
     print(quantity)
    wishlist_count = 0
    cart_count = 0  # Initialize wishlist_count to 0
    wishlist = []
    user_has_ordered_product = False
    average_rating_percentage = Decimal(0)
    average_rating = Decimal(0)
    if request.user.is_authenticated:
        user_id = request.user.id
        user=request.user
        average_rating = Decimal(product.calculate_average_rating()) 
        average_rating_percentage = Decimal((average_rating / Decimal('5.0'))) * Decimal('100')

        # Fetch the user's wishlist products' IDs and count
        cart_count = CartItems.objects.filter(cart__user=user).count()
        wishlist = WishlistItems.objects.filter(wishlist__user_id=user_id).values_list('products__id', flat=True)
        wishlist_count = WishlistItems.objects.filter(wishlist__user=user).count()
        user_has_ordered_product = OrderItem.objects.filter(order__user=user, product=product).exists()
    context = {
        'categories':categories,
        'product': product,
        'wishlist': wishlist,
        'wishlist_count': wishlist_count, 
        'cart_count':cart_count,
        'user_has_ordered_product': user_has_ordered_product,
        'average_rating' :average_rating,
        'average_rating_percentage': average_rating_percentage
    }
   
    return render(request, 'eachproduct.html', context)


@login_required
def plus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        product = Product.objects.get(id=prod_id)  # Retrieve the product
        user = request.user
        wishlist, created = AddWishlist.objects.get_or_create(user=user)
        # Check if the product already exists in the wishlist
        if user.is_authenticated:
            # Check if the product is already in the user's wishlist
            if WishlistItems.objects.filter(wishlist=wishlist, products=product).exists():
                message = 'Product is already in the wishlist.'
            else:
                # Create the wishlist item
                WishlistItems.objects.create(wishlist=wishlist, products=product)
                message = 'Product added to wishlist successfully.'
        else:
            message = 'You must be logged in to add products to your wishlist.'

        data = {
            'message': message,
        }
        return JsonResponse(data)

@login_required    
def minus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        product = get_object_or_404(Product, id=prod_id)
        user = request.user
        try:
            wishlist = WishlistItems.objects.get(wishlist__user=user, products=product)
            wishlist.delete()
            message = 'Product removed from wishlist successfully.'
        except WishlistItems.DoesNotExist:
            message = 'Product was not in the wishlist.'

        data = {
            'message': message,
        }
        return JsonResponse(data)

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        # Get the product and quantity from the form
        product = Product.objects.get(pk=product_id)
        quantity = int(request.POST.get('selected_quantity', 1))

        # Get or create the user's cart
        user = request.user
        cart, created = AddCart.objects.get_or_create(user=user)

        # Check if the product is already in the cart, if so, update the quantity
        existing_item = CartItems.objects.filter(cart=cart, product=product).first()
        
        # Get the maximum allowed quantity for the product
        max_quantity = product.quantity

        # Check if the quantity exceeds the maximum allowed
        if existing_item:
            new_quantity = existing_item.quantity + quantity
        else:
            new_quantity = quantity

        # If the new quantity exceeds the maximum, set it to the maximum allowed
        if new_quantity > max_quantity:
            new_quantity = max_quantity

        if existing_item:
            existing_item.quantity = new_quantity
            existing_item.save()
        else:
            # Create a new cart item
            CartItems.objects.create(cart=cart, product=product, quantity=new_quantity)

        return redirect('cart_details')  # Redirect to the cart page or wherever you want
    else:
        product = Product.objects.get(pk=product_id)
        return render(request, 'each_product.html', {'product': product})


@login_required
def cart_details(request):
    categories=Category.objects.filter(status=False)
    cart_items = []
    cart_empty = False
    total_price = 0
    # product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
           user_id = request.user.id
           user = request.user
        # Fetch the user's wishlist products' IDs and count
           wishlist = WishlistItems.objects.filter(wishlist__user_id=user_id).values_list('products__id', flat=True)
           wishlist_count = WishlistItems.objects.filter(wishlist__user=user).count()
           cart_count = CartItems.objects.filter(cart__user=user).count()
        #    cart = AddCart.objects.get(user=user)
        #    cart_items = CartItems.objects.filter(cart=cart)
        #    total_price = sum(item.total_price for item in cart_items)
           if AddCart.objects.filter(user=user).exists():
             cart = AddCart.objects.get(user=user)
             cart_items = CartItems.objects.filter(cart=cart)
             total_price = sum(item.total_price for item in cart_items)
           else:
             cart_empty = True
    context = {
        'categories':categories,
        # 'product': product,
        'wishlist': wishlist,
        'wishlist_count': wishlist_count, 
        'cart_count': cart_count,
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_empty': cart_empty,
    }
    return render(request, 'Customer/cart.html', context)
# from django.views.decorators.csrf import csrf_exempt
# @csrf_exempt  # Only for testing, do proper CSRF handling in production
# def update_cart_item_quantity(request):
#     if request.method == 'POST':
#         item_id = request.POST.get('item_id')
#         new_quantity = request.POST.get('new_quantity')

#         try:
#             print('got')
#             cart_item = CartItems.objects.get(id=item_id)
#             print(cart_item)
#             cart_item.quantity = new_quantity
#             print(cart_item.quantity)
#             cart_item.save()
            
#             # Debugging: Print the values and types
#             print('item_id:', item_id)
#             print('new_quantity:', new_quantity)
#             print('selling_price:', cart_item.product.selling_price)

#             # Calculate the new total price and convert it to a valid JSON format
#             itemTotalPrice = cart_item.product.selling_price * int(new_quantity)
#             itemTotalPrice = round(itemTotalPrice, 2)  # Round to 2 decimal places

#             # Send the updated itemTotalPrice as a valid JSON response
#             response_data = {
#                 'itemTotalPrice': str(itemTotalPrice)  # Convert to string for JSON
#             }
#             return JsonResponse(response_data)

#         except Exception as e:
#             print("An error occurred while updating quantity:", str(e))
#             return JsonResponse({'error': str(e)}, status=500)

#     return JsonResponse({'error': 'Invalid request method'}, status=400)
# @login_required
# def update_cart_item(request, cart_item_id):
#     cart_item = get_object_or_404(CartItems, pk=cart_item_id)
    
#     if request.method == 'POST':
#         new_quantity = int(request.POST.get('quantity', 1))
        
#         # Update the quantity of the cart item
#         if new_quantity > 0:
#             cart_item.quantity = new_quantity
#             cart_item.save()
#         else:
#             # Handle invalid quantity (e.g., remove the item from the cart)
#             cart_item.delete()
        
#     return redirect('cart_details')
def update_cart_item(request, cart_item_id):
    if request.method == 'POST':
        try:
            cart_item = CartItems.objects.get(id=cart_item_id)
        except CartItems.DoesNotExist:
            return JsonResponse({'error': 'Cart item not found'}, status=400)

        new_quantity = int(request.POST.get('quantity', 1))
        if new_quantity < 1:
            return JsonResponse({'error': 'Invalid quantity'}, status=400)

        cart_item.quantity = new_quantity
        cart_item.save()

        # Calculate the updated total price
        total_price = cart_item.product.selling_price * cart_item.quantity

        return JsonResponse({'total_price': total_price})

    return JsonResponse({'error': 'Invalid request method'}, status=400)
@login_required
def remove_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItems, pk=cart_item_id)
    
    if request.method == 'POST':
        # Delete the cart item
        cart_item.delete()
        return redirect('cart_details')
    
    return render(request, 'Customer/cart.html')

@login_required
def checkout(request):
    
    cart_items = CartItems.objects.filter(cart__user=request.user, product__quantity__gt=0)
    print(cart_items)
    return redirect('checkout_complete')

def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    shippings = Shippings.objects.get(user=request.user)
    if request.method=='POST':
        print("Submit")
        quantity=request.POST.get('quantityinput')
        print(quantity)
        return redirect('buyNowComplete', product_id=product_id, quantity=quantity)

    # Fixed quantity for Buy Now
    # quantity = int(1)
    # price = product.selling_price
    # total_price = Decimal(quantity) * Decimal(price)
    # print(total_price)

    # user = request.user
    # order, created = Order.objects.get_or_create(user=user)

    # order_item = OrderItem.objects.create(
    #     order=order,
    #     product=product,
    #     quantity=quantity,
    #     price=price,
    
    # )

    # order.total_price = Decimal(str(total_price))
    # print(order.total_price)
    # order.save()
    
    # Redirect to a purchase success page
    return render(request, 'Customer/single_checkout.html',{'product':product,'shippings':shippings}) 

from django.views import View
class ConfirmOrderView(View):
    def post(self, request, *args, **kwargs):
        print('got')
        print(request.POST)

        product_id = kwargs.get('product_id')
        quantity = int(request.POST.get('quantityinput', 1))  # Use the correct name (quantityInput) from your HTML

        print(quantity)
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            messages.error(request, "Product not found.")
            return redirect('dashboard_home')

        # return redirect('order_details')
        return redirect('dashboard_home')
    
# class OrderDetailsView(View):
#     template_name = 'Customer/order_details.html'  # Replace with your actual template name

#     def get(self, request, *args, **kwargs):
#         order_item_id = kwargs.get('order_item_id')
#         order_item = OrderItem.objects.get(id=order_item_id)  # Assuming you can retrieve the order item using its ID
#         return render(request, self.template_name, {'order_item': order_item})
  # Redirect to the product listing page or appropriate page

class OrderDetailsView(View):
    template_name = 'Customer/order_details.html'

    def get(self, request, *args, **kwargs):
        order_item_id = kwargs.get('order_item_id')
        order_item = OrderItem.objects.get(id=order_item_id)

        # Assign the first available delivery agent based on the seller
        delivery_agent = self.get_first_available_delivery_agent(order_item.seller)

        # Update the order item with the assigned delivery agent
        order_item.delivery_agent = delivery_agent
        order_item.save()

        self.send_assignment_email(order_item)

        return render(request, self.template_name, {'order_item': order_item})

    def get_first_available_delivery_agent(self, seller):
        # Get the first available delivery agent for the seller
        available_agents = DeliveryAgent.objects.filter(assigned_seller=seller, is_available=True).order_by('id')

        if available_agents.exists():
            return available_agents.first()
        else:
            # Handle the case where no available agents are found
            # You might want to queue the order for later processing or take appropriate action
            return None
        
    def send_assignment_email(self, order_item):
        subject = 'Order Assignment'
        message = f'You have been assigned to deliver the product: {order_item.product.name}\n'
        message += f'To the user at address: {order_item.order.user.address}\n'
        message += 'Please proceed with the delivery as soon as possible.'

        from_email = 'your-email@example.com'  # Update with your email address
        to_email = order_item.delivery_agent.user.email

        send_mail(subject, message, from_email, [to_email])

#payment


razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

def checkout_complete(request):
    user = request.user
    shippings = Shippings.objects.get(user=user)
    print(shippings)
    cart = get_object_or_404(AddCart, user=user)
    cart_items = CartItems.objects.filter(cart=cart)
    if not cart_items:
        return render(request, 'Customer/checkout_complete.html')
    total_price = Decimal(sum(cart_item.product.selling_price * cart_item.quantity for cart_item in cart_items))
    # total_price = cart_item.product.selling_price * cart_item.quantity    
    currency = 'INR'

    # Set the 'amount' variable to 'total_price'
    amount = int(total_price*100)
    # amount=20000
    
    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(
        amount=amount,
        currency=currency,
        payment_capture='0'
    ))

    # Order id of the newly created order
    razorpay_order_id = razorpay_order['id']
    callback_url = '/paymenthandler/cart/'


    order = Order.objects.create(
        user=request.user,
        total_price=total_price,
        razorpay_order_id=razorpay_order_id,
        payment_status=Order.PaymentStatusChoices.PENDING,
    )

    # Add the products to the order
    for cart_item in cart_items:
        product = cart_item.product
        price = product.selling_price
        quantity = cart_item.quantity
        total_item_price = price * quantity

        # Create an OrderItem for this product
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            seller=product.seller,  # Set the seller of the product as the seller of the order item
            quantity=quantity,
            price=price,
            total_price=total_item_price,
        )

    # Save the order to generate an order ID
    order.save()

    # Create a context dictionary with all the variables you want to pass to the template
    context = {
        'order_items': cart_items,
        'total_price': total_price,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_merchant_key': settings.RAZOR_KEY_ID,
        'razorpay_amount': amount,  # Set to 'total_price'
        'currency': currency,
        'callback_url': callback_url,
        'shippings': shippings
    }

    return render(request, 'Customer/checkout_complete.html', context=context)

def buyNowComplete(request, product_id, quantity):
    try:
        product = get_object_or_404(Product, id=product_id)
        total_price = Decimal(product.selling_price * quantity)
        print(total_price)
        seller_id = product.seller_id
        amount = int(total_price * 100)
        # Convert total price to paise and round to 2 decimal places
        # amount_in_paise = int(total_price * 100)
        # rounded_amount = Decimal(amount_in_paise).quantize(Decimal('1.00'))

        # Create a Razorpay Order
        razorpay_order = razorpay_client.order.create(dict(
            amount=amount,
            currency='INR',
            payment_capture='0'
        ))

        razorpay_order_id = razorpay_order['id']
        callback_url = '/paymenthandler/buynow/'



        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            razorpay_order_id=razorpay_order_id,
            payment_status=Order.PaymentStatusChoices.PENDING,
        )

        # Add the product to the order
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            seller_id=seller_id,
            quantity=quantity,
            price=product.selling_price,
            total_price=amount,
        )
        
        # Save the order to generate an order ID
        order.save()
        cart_items=Product.objects.get(id=product_id)
        # Create a context dictionary with variables for the template
        context = {
            'product': cart_items,
            'quantity':quantity,
            'total_price': total_price,
            'razorpay_order_id': razorpay_order_id,
            'razorpay_merchant_key': settings.RAZOR_KEY_ID,
            'razorpay_amount': amount,
            'currency': 'INR',
            'callback_url': callback_url,
        }

        return render(request, 'Customer/checkout_complete.html', context=context)

    except (Product.DoesNotExist, Seller.DoesNotExist) as e:
        # Handle cases where product or seller does not exist
        return HttpResponseBadRequest("Product or Seller does not exist.")

@csrf_exempt
def paymenthandler(request, cart_order=False):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')
       
        # Verify the payment signature.
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        result = razorpay_client.utility.verify_payment_signature(params_dict)

        if not result:
            # Signature verification failed.
            return render(request, 'paymentfail.html')

        # Signature verification succeeded.
        # Retrieve the order from the database
        try:
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
        except Order.DoesNotExist:
            return HttpResponseBadRequest("Order not found")

        if order.payment_status == Order.PaymentStatusChoices.SUCCESSFUL:
            # Payment is already marked as successful, ignore this request.
            return HttpResponse("Payment is already successful")

        if order.payment_status != Order.PaymentStatusChoices.PENDING:
            # Order is not in a pending state, do not proceed with stock update.
            return HttpResponseBadRequest("Invalid order status")

        
        amount = int(order.total_price * 100) 
        razorpay_client.payment.capture(payment_id, amount)

        
        order.payment_id = payment_id
        order.payment_status = Order.PaymentStatusChoices.SUCCESSFUL
        order.save()
        
        add_cart, created = AddCart.objects.get_or_create(user=request.user)

        
        add_cart.order = order
        add_cart.save()
        
        try:
            cart = AddCart.objects.get(order=order)
        except AddCart.DoesNotExist:
            return HttpResponseBadRequest("Cart not found for the order")

        # Retrieve the cart items associated with the cart
        # cart_items = CartItems.objects.filter(cart=cart)
        # for cart_item in cart_items:
        #     product = cart_item.product
        #     if product.selling_price >= cart_item.quantity:
        #         # Decrease the product stock and update ProductSummary
        #         product.selling_price -= cart_item.quantity
                
        #         product.save()
        #         # Remove the item from the cart
        #         cart_item.delete()
        # cart_items = CartItems.objects.filter(cart=cart)
        # for cart_item in cart_items:
        #     product = cart_item.product
        #     if product.quantity >= cart_item.quantity:
        #         # Decrease the product stock and update ProductSummary
        #         product.quantity -= cart_item.quantity
                
        #         product.save()
        #         # Remove the item from the cart
        #         cart_item.delete()
        #     else:
                
        #         return HttpResponseBadRequest("Insufficient stock for some items")
        # order_items = OrderItem.objects.filter(order=order)
        # order_item_id = order_items.first().id
        # for order_item in order_items:
        #     product = order_item.product
        #     if product.quantity >= order_item.quantity:
        #         # Decrease the product quantity by the ordered quantity
        #         product.quantity -= order_item.quantity
        #         product.save()
        #     else:
        #         # Handle the case where there is insufficient product quantity
        #         return HttpResponseBadRequest("Insufficient product quantity")
        # return redirect(reverse('order_details', kwargs={'order_item_id': order_item_id}))
        # return redirect('order_summary', order_id=order.id)
        if cart_order:
           cart_items = CartItems.objects.filter(cart=cart)
           order_items = OrderItem.objects.filter(order=order)
           if cart_items.exists():
               order_item_id = order_items.first().id
               print(order_item_id)
               for cart_item in cart_items:
                  product = cart_item.product
                  if product.quantity >= cart_item.quantity:
                # Decrease the product quantity by the quantity in the cart
                    product.quantity -= cart_item.quantity
                    product.save()
                  else:
                # Handle the case where there is insufficient product quantity
                      return HttpResponseBadRequest("Insufficient product quantity")

            # Remove the item from the cart
                  cart_item.delete()

        # Retrieve the first order item ID for redirection
               

           return redirect(reverse('order_details', kwargs={'order_item_id': order_item_id}))
        else:
            order_items = OrderItem.objects.filter(order=order)
            if order_items.exists():
                order_item_id = order_items.first().id
                for order_item in order_items:
                    product = order_item.product
                    if product.quantity >= order_item.quantity:
                        # Decrease the product quantity by the ordered quantity
                        product.quantity -= order_item.quantity
                        product.save()
                    else:
                        # Handle the case where there is insufficient product quantity
                        return HttpResponseBadRequest("Insufficient product quantity")
            else:
                return HttpResponseBadRequest("Order items not found")

            # Retrieve the first order item ID for redirection

            return redirect(reverse('order_details', kwargs={'order_item_id': order_item_id}))

    return HttpResponseBadRequest("Invalid request method")

from decimal import Decimal
@login_required 
def order_placed_successfully(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        order_items = order.items.all()  # Retrieve order items associated with the order
    except Order.DoesNotExist:
        # Handle the case where the order doesn't exist or doesn't belong to the user
        return render(request, 'error.html', {'error_message': 'Order not found.'})
    new_total_price = Decimal(0)
   
    print('entered')
    cart_items = CartItems.objects.filter(cart__user=request.user)
    if request.method == 'POST':
        print('hlo')
        for item in order_items:
            # Retrieve the updated quantity and price from the request
            updated_quantity = request.POST.get(f'quantity{item.id}',item.quantity)
            print(updated_quantity)
            if item.order_confirmation == OrderItem.PENDING:
                item.order_confirmation = OrderItem.CONFIRMED
            # Update the order item with the new quantity and price
            item.quantity = updated_quantity
            print(item.quantity)
            item.order_confirmation = OrderItem.CONFIRMED  # Update order confirmation status
            item.save()
            
            new_total_price += Decimal(updated_quantity) * Decimal(item.price)

            # new_total_quantity += updated_quantity

            order.total_price = new_total_price
            order.save()
            cart_items.delete()
    # Pass order and order items to the template for display
    return render(request, 'Customer/order_placed.html', {'order': order, 'order_items': order_items})
# @login_required
# def order_history(request):
#     orders = Order.objects.filter(user=request.user)
#     confirmed_orders = Order.objects.filter(order_confirmation='confirmed')
#     return render(request, 'Customer/order_history.html', {'orders': orders,'confirmed_orders': confirmed_orders})
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user, payment_status=Order.PaymentStatusChoices.SUCCESSFUL).order_by('-order_date')
    page_number = request.GET.get('page', 1)
    paginator = Paginator(orders, 2)  # 2 orders per page
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }
    return render(request, 'Customer/order_history.html', {'orders': orders, 'page_obj':page_obj})

def remove_from_order(request, item_id, cart_item_id):
    # Get the cart item
    cart_item = get_object_or_404(CartItems, id=cart_item_id)
    product = cart_item.product
    print(product)
    # Get the item's total price
    item_total_price = cart_item.quantity * product.selling_price
    cart_item.delete()
    # Delete the cart item
    # order = cart_item.order
    # order.total_price -= item_total_price  # Subtract the item's price
    # order.save()

    # Delete the cart item
    

    return JsonResponse({'message': 'Item removed from order.'}, status=200)
def single_cancel_order(request, order_id):
    # Retrieve the order
    order = get_object_or_404(Order, id=order_id)
    
    # Retrieve the total price from the query parameter
    total_price = request.GET.get('total_price', None)
    return render(request, 'Customer/single_cancel_order.html', {'order': order}) 
def cancel_order(request,order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    print(order)
    order_items = order.items.all()
    print(order_items)
    for item in order_items:
      print(item)
      item.order_confirmation = OrderItem.CANCELED
      print(item.order_confirmation)
      item.save()
    return redirect('cart_details')
    
def cancel_order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'Customer/cancel_order_confirmation.html', {'order': order})

def add_review(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    user=request.user
        # Fetch the user's wishlist products' IDs and count
   
    if request.method == 'POST':
        comment = request.POST.get('review', '')
        rating = request.POST.get('rating')

        # Validate rating (you can adjust this based on your needs)
        if float(rating) < 0 or float(rating) > 5:
            messages.error(request, 'Invalid rating. Please provide a rating between 0 and 5.')
            return redirect('each_product', product_id=product_id)

        # Create the review
        review = Review.objects.create(product=product, user=user)

        # Create the review rating
        review_rating = ReviewRating.objects.create(review=review, comment=comment, rating=rating)

        # Redirect to the product detail page
        return redirect('each_product', product_id=product_id)

    return render(request, 'Customer/add_review.html', {'product': product})
@login_required
def order_itemdetails(request, order_id):
    
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    print(order)
    return render(request, 'Seller/order_details.html', {'order': order,'order_items': order_items})

@login_required
def delivery_order_itemdetails(request, order_id):
    
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    print(order)
    return render(request, 'DeliveryAgent/order_details.html', {'order': order,'order_items': order_items})

@login_required
def create_order(request):
    # Get the user's cart items
    cart_items = CartItems.objects.filter(cart__user=request.user)
    
    # Create a new order
    order = Order.objects.create(user=request.user)
    
    # Create order items based on the cart items
    for cart_item in cart_items:
        order_item = OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=cart_item.product.selling_price
        )
    
    # Update the cart items to associate them with this order
    cart_items.update(order=order, order_item=order_item)
    
    # Update the order total price based on order items
    order.total_price = sum(order_item.price * order_item.quantity for order_item in order.items.all())
    order.save()
    
    # Clear the user's cart
    cart_items.delete()
    
    return JsonResponse({'order_id': order.id})

# View to display a list of orders for a user
@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'order_list.html', {'orders': orders})

# View to display details of a specific order
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})


from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa 
from django.shortcuts import get_object_or_404


class GenerateBillPDF(View):
    def get(self, request, order_item_id, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=order_item_id)

        # Render the HTML content using a Django template
        template_path = 'Customer/bill_template.html'  # Provide the path to your HTML template
        context = {'order_item': order_item}
        template = get_template(template_path)
        html = template.render(context)

        # Create a PDF document
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="bill_{order_item.id}.pdf"'

        # Generate PDF using xhtml2pdf library
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')

        return response

@login_required
def view_wishlist(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        added_to_wishlist = request.GET.get('added_to_wishlist', False)
        removed_from_wishlist = request.GET.get('removed_from_wishlist', False)
        user = request.user
        cart_count = CartItems.objects.filter(cart__user=user).count()
        wishlist_products = WishlistItems.objects.filter(wishlist__user=user)
        wishlist_count = WishlistItems.objects.filter(wishlist__user=user).count()
        categories=Category.objects.filter(status=False)
        
    else:
        # If the user is not authenticated, set wishlist_products to an empty queryset
        wishlist_products = []

    context = {
        'wishlist_products': wishlist_products,
        'categories':categories,
        'wishlist_count':wishlist_count,
        'cart_count':cart_count,
        'added_to_wishlist': added_to_wishlist,
        'removed_from_wishlist': removed_from_wishlist
    }

    return render(request, 'Customer/wishlist_products.html', context)
@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    # Ensure the user is authenticated before removing from the wishlist
    if not request.user.is_authenticated:
        response_data = {'message': 'User is not authenticated'}
        return JsonResponse(response_data, status=401)  # Return a 401 Unauthorized status

    try:
        # Check if the product exists in the user's wishlist
        wishlist_item = WishlistItems.objects.get(wishlist__user=request.user, products_id=product_id)
        # Remove the product from the wishlist
        wishlist_item.delete()
        response_data = {'message': 'Product removed from wishlist successfully'}
        return JsonResponse(response_data)
    except WishlistItems.DoesNotExist:
        response_data = {'message': 'Product not found in wishlist'}
        return JsonResponse(response_data, status=404)

# @csrf_protect
# def rate_product(request):
#     if request.method == 'POST':
#         rating_value = request.POST.get('rating')
#         product_id = request.POST.get('product_id')

#         # Check if the user is authenticated
#         if not request.user.is_authenticated:
#             return JsonResponse({'error': 'You must be logged in to rate products.'}, status=403)

#         # Check if the rating value is valid (1 to 5)
#         try:
#             rating_value = int(rating_value)
#             if rating_value < 1 or rating_value > 5:
#                 raise ValueError('Invalid rating value')
#         except ValueError:
#             return JsonResponse({'error': 'Invalid rating value'}, status=400)

#         # Check if the product exists
#         try:
#             product = Product.objects.get(id=product_id)
#         except Product.DoesNotExist:
#             return JsonResponse({'error': 'Product not found'}, status=404)

#         # Check if the user has already rated this product
#         existing_rating = Rating.objects.filter(user=request.user, product=product).first()
#         if existing_rating:
#             return JsonResponse({'error': 'You have already rated this product.'}, status=403)

#         # Create a new rating entry
#         new_rating = Rating(user=request.user, product=product, rating=rating_value)
#         new_rating.save()

#         return JsonResponse({'message': 'Rating saved successfully'})
    
#     return JsonResponse({'error': 'Invalid request method'}, status=405)
    
@login_required
def index(request):
    customers = CustomUser.objects.filter(role='customer', is_active = True)
    products = Product.objects.filter(status=False)
    sellers = Seller.objects.filter(is_approved='approved')
    orders = Order.objects.filter(payment_status=Order.PaymentStatusChoices.SUCCESSFUL)
    orders_count = orders.count()
    product_count = products.count()
    customer_count = customers.count() 
    seller_count = sellers.count()
    seller_totals = {}
    for seller in sellers:
        seller_orders = OrderItem.objects.filter(seller=seller)
        successful_orders = seller_orders.filter(order__payment_status=Order.PaymentStatusChoices.SUCCESSFUL)
        
        total_earnings = sum(order_item.total_price for order_item in successful_orders)
        total_products_sold = sum(order_item.quantity for order_item in successful_orders)
        
       
        order_count = successful_orders.count()
        seller_totals[seller] = {
            'total_earnings': total_earnings,
            'total_products_sold': total_products_sold,
            'order_count': order_count
        }
    context = {'customer_count': customer_count, 'orders_count':orders_count,'product_count':product_count, 'seller_count':seller_count,'seller_totals': seller_totals}
    return render(request, 'MainUser/index.html', context)

@login_required
def sellerindex(request):
    categories = Category.objects.filter(status=False)
    category_count = categories.count() 
    seller = Seller.objects.get(user=request.user)
    orders = Order.objects.all()
    
    order_count = Order.objects.filter(orderitem__seller=seller, payment_status=Order.PaymentStatusChoices.SUCCESSFUL).count()
    print(seller)
    product_count = Product.objects.filter(seller=seller, status=False).count()
    user = request.user
  
    if user.seller.latitude is None or user.seller.longitude is None:
            # Check if a similar notification already exists
            existing_notification = Notification.objects.filter(
                recipient=user,
                message='Please update your location for better service.',
                notification_type='other_notification_type'
            ).exists()

            if not existing_notification:
                # Create a notification only if a similar one doesn't exist
                Notification.objects.create(
                    recipient=user,
                    message='Please update your location for better service.',
                    notification_type='other_notification_type'
                )
    # Fetch unread notifications for the seller
    notifications = Notification.objects.filter(recipient=user)
    unread_notifications_count = request.user.notification_set.filter(is_read=False).count()
    
    confirmed_orders = OrderItem.objects.filter(
        product__seller=seller,
        order__payment_status=Order.PaymentStatusChoices.SUCCESSFUL
    ).distinct

    # Retrieve products associated with confirmed orders
    # products = Product.objects.filter(order__in=confirmed_orders).distinct()
    print(confirmed_orders)
    context = {'unread_notifications_count': unread_notifications_count, 'notifications': notifications, 'category_count': category_count, 'product_count': product_count,'confirmed_orders': confirmed_orders,'order_count':order_count,'orders':orders}
    return render(request, 'Seller/sellerindex.html', context)
@login_required
def seller_orders(request):
    
    seller = Seller.objects.get(user=request.user)

    seller_orders = Order.objects.filter(orderitem__seller=seller).distinct()

    context = {
        'seller_orders': seller_orders,
    }

    return render(request, 'Seller/orderview.html', context)
@login_required
def delivery_orders(request):
    
    delivery_agent = DeliveryAgent.objects.get(user=request.user)

    delivery_orders = Order.objects.filter(orderitem__delivery_agent=delivery_agent).distinct()

    context = {
        'delivery_orders': delivery_orders,
    }

    return render(request, 'DeliveryAgent/orderview.html', context)
@login_required
def sellerprofile(request):
    return render(request, 'Seller/sellerprofile.html')
@login_required
def editseller(request):
    user_profile = CustomUser.objects.get(pk=request.user.pk)  # Get the CustomUser object
    seller_profile = Seller.objects.get(user=user_profile)
    current_latitude = request.GET.get('currentLatitude', seller_profile.latitude)
    current_longitude = request.GET.get('currentLongitude', seller_profile.longitude)
    print('Hello')
    print(current_latitude)
    seller_profile.latitude = current_latitude
    seller_profile.longitude = current_longitude
    seller_profile.save()
    if request.method == "POST":
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        address = request.POST.get('address')
       
        # Check if a profile picture was uploaded
        if 'profile_pic' in request.FILES:
            profile_pic = request.FILES['profile_pic']
            user_profile.profile_pic = profile_pic

        user_profile.name = name
        user_profile.mobile = mobile
        user_profile.address = address
        user_profile.email = email  # Update the email field of the CustomUser object
        user_profile.save()

        business_name = request.POST.get('business_name')
        business_address = request.POST.get('business_address')
        business_website = request.POST.get('business_website')
        
        current_latitude = request.POST.get('latitude') or request.GET.get('currentLatitude')
        current_longitude = request.POST.get('longitude') or request.GET.get('currentLongitude')
        
        if 'seller_proof' in request.FILES:
            seller_proof = request.FILES['seller_proof']
            seller_profile.seller_proof = seller_proof
        
        seller_profile.business_name = business_name
        seller_profile.business_address = business_address
        seller_profile.business_website = business_website
        seller_profile.latitude = current_latitude
        seller_profile.longitude = current_longitude

        
        seller_profile.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('sellerprofile')  # Redirect to the profile page

    return render(request, 'Seller/editseller.html', {'user_profile': user_profile, 'seller_profile': seller_profile})  
@login_required
def sellerslist(request):
    sellers = Seller.objects.all()  # Fetch all customer profiles from the database
    seller_count = sellers.count() 
    context = {'sellers': sellers, 'seller_count': seller_count}
    return render(request, 'MainUser/sellerslist.html', context)
@login_required
def seller_details(request, seller_id):
    seller = get_object_or_404(Seller, pk=seller_id)
    product_count = Product.objects.filter(seller=seller, status=False).count()
    context = {'seller': seller, 'product_count' : product_count}
    return render(request, 'MainUser/seller_details.html', context)
@login_required
def productlist(request):
    role = request.user.role
    subcategories = Subcategory.objects.filter(status=False)  # Fetch all categories from the database
    selected_subcategory = request.POST.get('subcategory', 'all_subcategory')
    if role == 'seller':
        seller = Seller.objects.get(user=request.user)
    if selected_subcategory == 'all_subcategory':
        if role == 'seller':
            # For sellers, display only their added products with status=False
            products = Product.objects.filter(seller=seller, status=False)
            if not products.exists():
                messages.success(request, 'No Products Are Yet Added By You')
        else:
            # If 'All category' is selected, show all products
            products = Product.objects.filter(status=False)
            if not products.exists():
                messages.success(request, 'No Products Are Yet Added')
    else:
        selected_subcategory_id = int(selected_subcategory)
        if role == 'seller':
            # For sellers, display only their added products within the selected category with status=False
            products = Product.objects.filter(Q(subcategory__id=selected_subcategory_id) & Q(seller=seller, status=False))
            if not products.exists():
                messages.success(request, 'No Products Are Yet Added To This SubCategory By You')
        else:
            # Check if there are products available for the selected category
            products = Product.objects.filter(Q(subcategory__id=selected_subcategory_id) & Q(status=False))
            if not products.exists():
                messages.success(request, 'No Products Are Added To This SubCategory')

    if role == 'admin':
        template_name = 'MainUser/products-list.html'
    elif role == 'seller':
        template_name = 'Seller/products-list.html'

    context = {
        'subcategories': subcategories,
        'products': products,
        'selected_subcategory': selected_subcategory,
    }
    return render(request, template_name, context)
@login_required
def reviews(request):
    reviews = Review.objects.all()
    # products = Product.objects.all()

    # for product in products:
    #     product.avg_rating = product.calculate_average_rating()
    return render(request, 'MainUser/reviews.html', {'reviews': reviews,'products': products})
@login_required
def sellerreviews(request):
    reviews = Review.objects.all()
    # products = Product.objects.all()

    # for product in products:
    #     product.avg_rating = product.calculate_average_rating()
    return render(request, 'Seller/sellerevview.html', {'reviews': reviews,'products': products})
@login_required
def editproduct(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        # Retrieve the updated data from the request and update the product fields
        
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.quantity = request.POST.get('quantity')
        product.original_price = request.POST.get('original_price')
        product.selling_price = request.POST.get('selling_price')

        # Check if an updated image was provided
        if 'product_image' in request.FILES:
            product.product_image = request.FILES['product_image']

        product.save()
        messages.success(request, 'Product updated successfully.')
        return redirect('productlist')  # Redirect to the product list page or any other page as needed

    context = {'product': product}
    return render(request, 'Seller/editproduct.html', context)
@login_required
def view_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    context = {'product': product}
    return render(request, 'Seller/view_detail.html', context)
@login_required
def addproduct(request):
    categories = Category.objects.filter(status=False)
    seller = Seller.objects.get(user=request.user)
    selected_category = None
    selected_subcategory = None  # Initialize selected_subcategory to None
    subcategories = Subcategory.objects.none()  # Initialize subcategories queryset

    if request.method == 'POST':
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory')

        try:
            category = Category.objects.get(pk=category_id)
            selected_category = category

            if subcategory_id:
                try:
                    subcategory = Subcategory.objects.get(pk=subcategory_id)
                    selected_subcategory = subcategory
                except Subcategory.DoesNotExist:
                    messages.error(request, 'Selected subcategory not found.')
                    return redirect('productlist')

            # slug = request.POST.get('slug')
            name = request.POST.get('name')
            product_image = request.FILES.get('product_image')
            description = request.POST.get('description')
            quantity = request.POST.get('quantity')
            original_price = request.POST.get('original_price')
            selling_price = request.POST.get('selling_price')
            
            existing_product = Product.objects.filter(name=name, seller=seller, subcategory=selected_subcategory).first()
            if existing_product:
                if existing_product.status == True:
                # If the category exists and its status is False, update its status to True
                    # existing_product.slug = slug
                    existing_product.product_image = product_image
                    existing_product.description = description
                    existing_product.quantity = quantity
                    existing_product.original_price = original_price
                    existing_product.selling_price = selling_price
                    existing_product.status = False
                    existing_product.save()
                    messages.success(request, 'Product Added successfully.')
                    return redirect('productlist')
                else:
              
                    messages.warning(request, 'Product Already Exists.')
                    return redirect('productlist')

            else:
                 product = Product.objects.create(
                 subcategory=selected_subcategory,
                 seller=seller,
                #  slug=slug,
                 name=name,
                 product_image=product_image,
                 description = description,
                 quantity = quantity,
                 original_price=original_price,
                 selling_price=selling_price
            
                 )   
                 messages.success(request, 'Product Added Successfully.')
                 return redirect('productlist')      

        except Category.DoesNotExist:
            messages.error(request, 'Selected category not found.')

    context = {
        'categories': categories,
        'subcategories': subcategories,
        'selected_category': selected_category,
        'selected_subcategory': selected_subcategory, 
    }
    
    return render(request, 'Seller/addproduct.html', context)

def get_subcategories(request):
    category_id = request.GET.get('category_id')
    print(f'Category ID: {category_id}')
    subcategories = Subcategory.objects.filter(category_id=category_id, status=False).values('id', 'name')
    print('Subcategories:', list(subcategories))
    return JsonResponse({'subcategories': list(subcategories)})
@login_required
def productdelete(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    if request.method == 'POST':
       
        product.status = True  # Assuming True represents a hidden category
        product.save()
        messages.success(request, 'Product Deleted successfully.')
        return redirect('productlist')

    context = {'product': product}
    return render(request, 'Seller/productdelete.html', context)
@login_required
def categories(request):
    
    if request.method == 'POST':
        slug = request.POST['slug']
        name = request.POST['name']
        image = request.FILES['image']
        description = request.POST['catdescription']

        existing_category = Category.objects.filter(slug=slug).first()
        if existing_category:
            if existing_category.status == True:
                existing_category.slug=slug
                existing_category.name=name
                existing_category.image=image
                existing_category.description=description
                existing_category.status = False
                existing_category.save()
                messages.success(request, 'Category Added successfully.')
                return redirect('categories')
            else:
                # If the category exists and its status is already True, show a message
                messages.warning(request, 'Category Already Exists.')
                return redirect('categories')

        else:
            category = Category.objects.create(
            slug=slug,
            name=name,
            image=image,
            description = description
            
        )   
            messages.success(request, 'Category Added Successfully.')
            return redirect('categories') 
    role = request.user.role  # Assuming you have a 'role' field in your CustomUser model

    if role == 'admin':
        template_name = 'MainUser/categories.html'
        categories = Category.objects.filter(status=False)
    elif role == 'seller':
        template_name = 'Seller/categories.html' # Redirect to the category list page
        categories = Category.objects.filter(status=False)
 # Fetch all categories
    context = {'categories': categories}
    return render(request, template_name, context)
@login_required
def update_category(request, category_slug):
    category = Category.objects.get(slug=category_slug)
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        slug = request.POST['slug']
        image = request.FILES.get('image') 
        category = Category.objects.get(slug=category_slug)
        existing_category = Category.objects.filter(name=name).exclude(slug=category_slug).first()
        if existing_category:
            if existing_category.status==True:
                existing_category.name=name
                existing_category.description=description
                existing_category.image=image
                existing_category.status = False
                existing_category.save()
                messages.success(request, 'Category Updated successfully.')
                return redirect('categories') 
            else:
                messages.warning(request, 'A Category with this name already exists in the selected category.')
                return redirect('categories')
        else:
          category.name = name
          category.slug = slug
        # category.image = request.FILES['image']
          category.description = description
          if 'image' in request.FILES:
            category.image = image
       
          category.save()
          messages.success(request, 'Category updated successfully.')
        return redirect('categories')

    context = {'category': category}
    return render(request, 'MainUser/editcategory.html', context)
@login_required
def delete_category(request, category_slug):
    category = Category.objects.get(slug=category_slug)
    
    if request.method == 'POST':
        subcategories_with_products = Subcategory.objects.filter(category=category, product__isnull=False)
        if subcategories_with_products.exists():
            messages.error(request, 'Category cannot be deleted as associated subcategories have products.')
            return redirect('categories')
        else:
        # Handle deleting category logic here
            category.status = True  # Assuming True represents a hidden category
            category.save()
            messages.success(request, 'Category Deleted successfully.')
            return redirect('categories')

    context = {'category': category}
    return render(request, 'MainUser/deletecategory.html', context)
@login_required
def subcategories(request):

    categories = Category.objects.filter(status=False)
    if request.method == 'POST':
        print('Entered')
        name = request.POST['name']
        category_id = request.POST['category']
        print(category_id)
        image = request.FILES['image']
        description = request.POST['description']
        
        category = Category.objects.get(id=category_id)
        existing_category = Category.objects.filter(name=name).first()
        existing_subcategory = Subcategory.objects.filter(name=name, category=category).first()

        if existing_category:
            messages.warning(request, 'Category with the same name already exists.')
            return redirect('subcategories')
        
        if existing_subcategory:
            if existing_subcategory.status == True:
                existing_subcategory.name=name
                existing_subcategory.image=image
                existing_subcategory.description=description
                existing_subcategory.category=category
                existing_subcategory.status = False
                existing_subcategory.save()
                messages.success(request, 'Subcategory Added successfully.')
                return redirect('subcategories') 
            else:
                messages.warning(request, 'Subcategory Already Exists In The Category You Have Chosen')
                return redirect('subcategories') 

        else:
            subcategory = Subcategory.objects.create(
            name=name,
            image=image,
            description = description,
            category=category
            
        )   
            messages.success(request, 'SubCategory Added Successfully.')
        
        return redirect('subcategories') 
    role = request.user.role  

    if role == 'admin':
        template_name = 'MainUser/subcategory.html'
        categories = Category.objects.filter(status=False)
        subcategories = Subcategory.objects.filter(status=False)
    elif role == 'seller':
        template_name = 'Seller/subcategory.html' 
        categories = Category.objects.filter(status=False)
        subcategories = Subcategory.objects.filter(status=False)

    context = {'categories': categories, 'subcategories': subcategories}
    return render(request, template_name, context)
@login_required
def edit_subcategory(request, subcategory_id):
    categories = Category.objects.filter(status=False)
    subcategory = get_object_or_404(Subcategory, pk=subcategory_id)

    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        category_id = request.POST['category']
        image = request.FILES.get('image')  # Use get() to avoid errors if no image is provided
        
        category = Category.objects.get(id=category_id)

        existing_subcategory = Subcategory.objects.filter(Q(name=name) & Q(category=category)).exclude(id=subcategory.id).first()
        if existing_subcategory:
            if existing_subcategory.status==True:
                existing_subcategory.name=name
                existing_subcategory.description=description
                existing_subcategory.image=image
                existing_subcategory.category=category
                existing_subcategory.status = False
                existing_subcategory.save()
                messages.success(request, 'Subcategory Updated successfully.')
                return redirect('subcategories') 
            else:
                messages.warning(request, 'A subcategory with this name already exists in the selected category.')
                return redirect('subcategories')
        else:
           subcategory.name = name
           subcategory.description = description
           if 'image' in request.FILES:
            subcategory.image = image
           subcategory.category=category

           subcategory.save()
           messages.success(request, 'Subcategory updated successfully.')
        return redirect('subcategories')  # Redirect back to the subcategories page

    context = {'subcategory': subcategory, 'categories': categories}
    return render(request, 'MainUser/editsubcategory.html', context)
@login_required
def delete_subcategory(request, subcategory_id):
    subcategory = get_object_or_404(Subcategory, pk=subcategory_id)
    
    if request.method == 'POST':
        # Handle deleting category logic here
        subcategory.status = True  # Assuming True represents a hidden category
        subcategory.save()
        messages.success(request, 'SubCategory Deleted successfully.')
        return redirect('subcategories')

    context = {'subcategory': subcategory}
    return render(request, 'MainUser/deletesubcategory.html', context)

def signup_redirect(request):
    messages.error(request, "Something Wrong Here, It May Be That You Already Have Account!")
    return redirect('dashboard_home')

def login_page(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        # role = request.POST['role']  # Get the user's role from the form

        # Authenticate the user using the custom authentication backend
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            # if user.is_superuser:
            #     return redirect('index')  # Redirect superuser to admin homepage
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            if user.role == 'customer':
                customer = user.customer
                if customer.user.is_active:
                    login(request, user)
                    return redirect('dashboard_home')
                else:
                    messages.error(request, "Your Account is Blocked.")
                    return redirect('login_page')
            elif user.role == 'seller':
                seller = user.seller  # Assuming the seller profile is associated with the user
                if seller.is_approved == 'approved':
                    login(request, user)
                    return redirect('sellerindex')
                elif seller.is_approved == 'declined':
                    messages.error(request, "Your seller Account is Rejected.")
                    return redirect('login_page')
                else:
                    messages.error(request, "Your Seller Account Is Not Yet Approved.")
                    return redirect('login_page')
            elif user.role == 'admin':
                return redirect('index')  # Redirect admins to their dashboard page
            elif user.role == 'delivery_agent':
                return redirect('delivery_agent_dashboard')  # Redirect delivery agents to their dashboard page
            else:
                messages.error(request, "Invalid Role for User")
                return redirect('login_page')
        else:
            messages.error(request, "Invalid Login")
            return redirect('login_page')
    else:
        return render(request, 'Customer/login.html')
@login_required
def delivery_agent_dashboard(request):
    return render(request, 'DeliveryAgent/dashboard.html')
@login_required
def da_details(request):
    return render(request, 'DeliveryAgent/da_details.html')
@login_required
def edit_details(request):
    user_profile = CustomUser.objects.get(pk=request.user.pk)  # Get the CustomUser object
    delivery_profile = DeliveryAgent.objects.get(user=user_profile)
    # current_latitude = request.POST.get('latitude') or request.GET.get('currentLatitude')
    # current_longitude = request.POST.get('longitude') or request.GET.get('currentLongitude')
    current_latitude = request.GET.get('currentLatitude', delivery_profile.latitude)
    current_longitude = request.GET.get('currentLongitude', delivery_profile.longitude)
    print('Hello')
    print(current_latitude)
    delivery_profile.latitude = current_latitude
    delivery_profile.longitude = current_longitude
    delivery_profile.save()
    if request.method == "POST":
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        address = request.POST.get('address')
       
        # Check if a profile picture was uploaded
        if 'profile_pic' in request.FILES:
            profile_pic = request.FILES['profile_pic']
            user_profile.profile_pic = profile_pic

        user_profile.name = name
        user_profile.mobile = mobile
        user_profile.address = address
        user_profile.email = email  # Update the email field of the CustomUser object
        user_profile.save()

        
        
        current_latitude = request.POST.get('latitude') or request.GET.get('currentLatitude')
        current_longitude = request.POST.get('longitude') or request.GET.get('currentLongitude')
        
       
        delivery_profile.latitude = current_latitude
        delivery_profile.longitude = current_longitude

        
        delivery_profile.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('da_details')  # Redirect to the profile page

    return render(request, 'DeliveryAgent/edit_details.html',{'user_profile': user_profile, 'delivery_profile': delivery_profile})
from django.db.models import ExpressionWrapper, F, FloatField
from django.db.models.functions import ACos, Cos, Radians, Sin


# def calculate_distance(lat1, lon1, lat2, lon2):
#     def convert_coord(coord):
#         if isinstance(coord, F):
#             return coord
#         else:
#             return radians(coord)

#     lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(convert_coord, [lat1, lon1, lat2, lon2])

#     distance_expr = ExpressionWrapper(
#         6371.0 * Acos(Sin(lat1_rad) * Sin(lat2_rad) + Cos(lat1_rad) * Cos(lat2_rad) * Cos(lon2_rad - lon1_rad)),
#         output_field=FloatField()
#     )
#     return distance_expr
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    # Helper function to calculate distance between two points on the Earth's surface
    def convert_coord(coord):
      if coord is not None:
        return float(coord)
      else:
        return 0.0



    # Convert latitude and longitude to radians
    lat1, lon1, lat2, lon2 = map(convert_coord, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = 6371.0 * c  # Radius of Earth in kilometers

    return distance

def assign_nearby_agents_to_seller(seller, nearby_agents):

    for agent in nearby_agents:
        agent.assigned_seller = seller
        agent.save()
    # Clear existing assignments
    seller.nearby_delivery_agents.clear()
    # Add the new nearby agents
    seller.nearby_delivery_agents.add(*nearby_agents)
# def display_nearby_agents(request, seller_id):
#     seller = get_object_or_404(Seller, id=seller_id)
#     seller_latitude = seller.latitude
#     seller_longitude = seller.longitude

#     # Retrieve all sellers with the same location
#     sellers_with_same_location = Seller.objects.filter(
#         latitude=seller_latitude,
#         longitude=seller_longitude
#     ).exclude(id=seller_id)

#     # Retrieve all delivery agents not assigned to any seller
#     available_agents = DeliveryAgent.objects.filter(
#         latitude__isnull=False,
#         longitude__isnull=False,
#         seller__isnull=True  # Filter agents not assigned to any seller
#     )

#     # Calculate distances for each agent and print details
#     print("Seller:", seller)
#     print("Seller Location:", seller_latitude, seller_longitude)

#     for agent in available_agents:
#         # Calculate distance for each agent using haversine
#         distance = haversine(agent.latitude, agent.longitude, seller_latitude, seller_longitude)
#         print(f"Agent: {agent.user.email} - Latitude: {agent.latitude}, Longitude: {agent.longitude}")
#         print(f"Distance: {distance} km\n")

#         # Update the agent's distance field in the database
#         DeliveryAgent.objects.filter(pk=agent.pk).update(distance=distance)

#     # Filter nearby agents based on distance
#     nearby_agents = available_agents.order_by('distance')[:3]

#     print("Nearby Agents:")
#     for agent in nearby_agents:
#         print(f"{agent.user.email} - Distance: {agent.distance} km")

#     # Assign the top three nearby agents to the seller
#     seller.nearby_delivery_agents.set(nearby_agents)

#     # Assign remaining nearest agents to other sellers with the same location
#     remaining_agents = available_agents.exclude(id__in=nearby_agents.values_list('id', flat=True))
    
#     for other_seller in sellers_with_same_location:
#         other_seller_nearby_agents = remaining_agents.order_by('distance')[:3]
#         remaining_agents = remaining_agents.exclude(id__in=other_seller_nearby_agents.values_list('id', flat=True))
#         other_seller.nearby_delivery_agents.set(other_seller_nearby_agents)

#     context = {
#         'seller': seller,
#         'delivery_agents': nearby_agents,
#     }

#     return render(request, 'Seller/display_nearby_agents.html', context)
def display_nearby_agents(request, seller_id):
    # Retrieve the seller's location
    seller = get_object_or_404(Seller, id=seller_id)
    seller_latitude = seller.latitude
    seller_longitude = seller.longitude

    # Retrieve all delivery agents
    delivery_agents = DeliveryAgent.objects.all()

    # Calculate distances for each agent and print details
    print("Seller:", seller)
    print("Seller Location:", seller_latitude, seller_longitude)

    for agent in delivery_agents:
        # Calculate distance for each agent using haversine
        distance = haversine(agent.latitude, agent.longitude, seller_latitude, seller_longitude)
        print(f"Agent: {agent.user.email} - Latitude: {agent.latitude}, Longitude: {agent.longitude}")
        print(f"Distance: {distance} km\n")

        # Update the agent's distance field in the database
        DeliveryAgent.objects.filter(pk=agent.pk).update(distance=distance)

    # Filter nearby agents based on distance
    nearby_agents = delivery_agents.filter(
        latitude__isnull=False, 
        longitude__isnull=False, 
        distance__lte=10
    ).order_by('distance')[:3]

    print("Nearby Agents:")
    for agent in nearby_agents:
        print(f"{agent.user.email} - Distance: {agent.distance} km")

    # Assign the nearby agents to the seller
    assign_nearby_agents_to_seller(seller, nearby_agents)

    context = {
        'seller': seller,
        'delivery_agents': nearby_agents,
    }

    return render(request, 'Seller/display_nearby_agents.html', context)
def display_nearby_agents_map(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)
    seller_latitude = seller.latitude
    seller_longitude = seller.longitude

    # Retrieve all delivery agents
    delivery_agents = DeliveryAgent.objects.all()

    # Calculate distances for each agent and print details
    print("Seller:", seller)
    print("Seller Location:", seller_latitude, seller_longitude)

    for agent in delivery_agents:
        # Calculate distance for each agent using haversine
        distance = haversine(agent.latitude, agent.longitude, seller_latitude, seller_longitude)
        print(f"Agent: {agent.user.email} - Latitude: {agent.latitude}, Longitude: {agent.longitude}")
        print(f"Distance: {distance} km\n")

        # Update the agent's distance field in the database
        DeliveryAgent.objects.filter(pk=agent.pk).update(distance=distance)

    # Filter nearby agents based on distance
    nearby_agents = delivery_agents.filter(
        latitude__isnull=False, 
        longitude__isnull=False, 
        distance__lte=10
    ).order_by('distance')[:3]

    print("Nearby Agents:")
    for agent in nearby_agents:
        print(f"{agent.user.email} - Distance: {agent.distance} km")

    # Assign the nearby agents to the seller
    

    context = {
        'seller': seller,
        'delivery_agents': nearby_agents,
        'seller_latitude': seller_latitude,
        'seller_longitude': seller_longitude,
    }

    return render(request, 'Seller/display_nearby_agents_map.html', context)
@login_required
def blockcustomer(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
    
        user.is_active = False  # Block the user associated with the customer
        user.save()
        messages.success(request, "Customer successfully blocked.")
        return redirect('view_customer')
        
    context={'customer': user}
    return render(request, 'MainUser/blockcustomer.html', context)
@login_required
def unblockcustomer(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
    
        user.is_active = True  # Block the user associated with the customer
        user.save()
        messages.success(request, "Customer successfully Unblocked.")
        return redirect('view_customer')
        
    context={'customer': user}
    return render(request, 'MainUser/unblockcustomer.html', context)

# def delete_category(request, category_slug):
#     category = Category.objects.get(slug=category_slug)
    
#     if request.method == 'POST':
#         # Handle deleting category logic here
#         category.status = True  # Assuming True represents a hidden category
#         category.save()
#         messages.success(request, 'Category Deleted successfully.')
#         return redirect('categories')

#     context = {'category': category}
#     return render(request, 'MainUser/deletecategory.html', context)
@login_required
def approveseller(request, seller_id):
    seller = get_object_or_404(Seller, pk=seller_id)
    seller.is_approved = Seller.APPROVED  # Set the status to 'approved'
    seller.save()  # Call the approve method to change the status to 'approved'
    login_url = request.build_absolute_uri(reverse('login_page'))
    subject = 'Seller Account Approved'
    message = f'Your seller account has been approved. You can now log in using the following link:\n\n{login_url}'
    from_email = 'mailtoshowvalidationok@gmail.com'  # Replace with your email
    recipient_list = [seller.user.email]
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    messages.success(request, 'Seller approval successful. An approval email with the login link has been sent to the seller.')
    return redirect('sellerslist')
@login_required
def rejectseller(request, seller_id):
    seller = get_object_or_404(Seller, pk=seller_id)
    seller.is_approved = Seller.DECLINED  # Set the status to 'approved'
    seller.save() # Call the reject method to change the status to 'declined'
    subject = 'Seller Account Rejected'
    message = f'Your seller account has been rejected.'
    from_email = 'mailtoshowvalidationok@gmail.com'  # Replace with your email
    recipient_list = [seller.user.email]
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    messages.success(request, 'Seller Requestt Rejected')
    return redirect('sellerslist') 



def sellregister(request):
    if request.method == 'POST':
        # Extract form data from request.POST
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        mobile = request.POST.get('mobile')
        business_name = request.POST.get('business_name')
        business_address = request.POST.get('business_address')
        business_website = request.POST.get('business_website')
        seller_proof = request.FILES.get('seller_proof')  # Handle file upload
        role="seller"
        if password == confirm_password:
            if CustomUser.objects.filter(email=email, role=role).exists():
                return render(request, 'Seller/register.html', {'username_exists': True})
            else:
                user = CustomUser.objects.create_user(email=email, name=name, password=password, mobile=mobile, role=role)
                user_profile = Seller(user=user, business_name=business_name, business_address=business_address, business_website=business_website,seller_proof=seller_proof)
                user_profile.save()

                subject = 'Seller Registration Confirmation'
                message = 'Thank You For Registering As a Seller. Your Registration Was Successful And Your Account Will Be Activated Soon. You Can Login After Approved By Admin'
                from_email = 'mailtoshowvalidationok@gmail.com'  # Replace with your email
                recipient_list = [email]

                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                # messages.success(request, 'Seller Registration successful.')
                # return redirect('login_page')
                return redirect('sellernotification_page')
        else:
            messages.error(request, 'Password confirmation does not match')
            return redirect('register')
    else:
        return render(request, 'Seller/register.html')
def sellernotification_page(request):
    return render(request, 'Seller/sellernotification.html')          
        

# def activate_seller(request, uidb64, token):
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         seller = Seller.objects.get(pk=uid)
#         if default_token_generator.check_token(seller, token):
#             seller.is_approved = True
#             seller.save()
#             messages.success(request, 'Seller account activated successfully.')
#             # Send an email to the seller notifying them of approval
#             # You can use the same email sending logic as in the registration view
#             return redirect('login_page')
#         else:
#             messages.error(request, 'Activation link is invalid.')
#     except (TypeError, ValueError, OverflowError, Seller.DoesNotExist):
#         seller = None
#         messages.error(request, 'Activation link is invalid.')
    
#     return render(request, 'dashboard_home.html')
@login_required
def add_da(request):
    sellers = Seller.objects.all()
    print("Sellers:", sellers)
    if request.method == 'POST':
        # Extract form data
        agent_name = request.POST.get('agent_name')
        place = request.POST.get('place')
        mobile_number = request.POST.get('mobile')
        pincode = request.POST.get('pincode')
        # location = request.POST.get('location')
        email = request.POST.get('email')
        password = request.POST.get('password')
        # business_name = request.POST.get('seller') 
     
        role = 'delivery_agent'
        user = CustomUser.objects.create_user(email=email, password=password, name=agent_name, mobile=mobile_number, role=role)
        delivery_agent = DeliveryAgent.objects.create(
            user=user,
            place=place,
            pincode=pincode,
            location=place,
                         # Corrected value to store Seller instance
        )
 

        subject = 'Welcome to SleekMart Delivery Team'
        message = f'Hi {agent_name},\n\nYou have been added as a delivery agent on SleekMart.\n\nYour login credentials:\nEmail: {email}\nPassword: {password}\n\nThank you for joining our team!'
        from_email = 'mailtoshowvalidationok@gmail.com'  # Replace with your email
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        messages.success(request, 'Agent Added Successfully')
        return redirect('view_da')

    return render(request, 'MainUser/add_DA.html', {'sellers': sellers})

def view_da(request):
    delivery_agents = DeliveryAgent.objects.all()
    
    context = {
        'delivery_agents': delivery_agents,
    }
    return render(request, 'MainUser/delivery_agent_list.html', context)

def delivery_agent_details(request, delivery_agent_id):
    delivery_agent = get_object_or_404(DeliveryAgent, id=delivery_agent_id)
    return render(request, 'Seller/delivery_agent_details.html', {'delivery_agent': delivery_agent})

def register(request):
    if request.method == "POST":
        name=request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        mobile = request.POST['mobile']
        confirm_password = request.POST['confirmPassword']
        role = 'customer'
        if password == confirm_password:
            if CustomUser.objects.filter(email=email, role=role).exists():
                return render(request, 'Customer/register.html', {'username_exists': True})
            else:
                user = CustomUser.objects.create_user(email=email, name=name, password=password, mobile=mobile, role=role)
                user_profile = Customer(user=user)
                user_profile.save()
                login_url = request.build_absolute_uri(reverse('login_page'))
                subject = 'Customer Registration Confirmation'
                message = f'Thank You For Registering As A Customer. Your Registration Was Successful. You can now log in using the following link:\n\n{login_url}'
                from_email = 'mailtoshowvalidationok@gmail.com'  # Replace with your email
                recipient_list = [email]
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                # messages.success(request, 'Registration successful. You can now log in.')
                # return redirect('login_page')
                return redirect('custnotification_page')
        else:
            messages.error(request, 'Password confirmation does not match')
            return redirect('register')
    else:
        return render(request, 'Customer/register.html')
def custnotification_page(request):
    return render(request, 'Customer/notification.html')

def add_route(request):
    return render(request, 'Seller/add_route.html')

@login_required
def notifications(request):
    user = request.user
    
    notifications = Notification.objects.filter(recipient=user)
    print(notifications)
    notification_count = notifications.filter(is_read=False).count()
    
   
    if 'visited_notifications' not in request.session:
        # Mark all unread notifications as read
        notifications.filter(is_read=False).update(is_read=True)
        request.session['visited_notifications'] = True
    
    return render(request, 'notifications.html', {'notifications': notifications,  'notification_count' : notification_count})

@login_required
def profile(request):
    user_profile = CustomUser.objects.get(pk=request.user.pk)
    customer_profile = Customer.objects.get(user=user_profile)
    print(customer_profile)
    cart_count = 0
    if request.user.is_authenticated:
        user = request.user
        cart_count = CartItems.objects.filter(cart__user=user).count()
    context = {
        'cart_count' : cart_count,
        'customer_profile' : customer_profile,
    }
    return render(request, 'Customer/profile.html', context)
@login_required
def edit_profile(request):
    user_profile = CustomUser.objects.get(pk=request.user.pk)
    customer_profile = Customer.objects.get(user=user_profile)
    print(customer_profile)
      # Get the CustomUser object
    cart_count = 0
    if request.user.is_authenticated:
        user = request.user
        cart_count = CartItems.objects.filter(cart__user=user).count()
     
    current_latitude = request.GET.get('currentLatitude', customer_profile.latitude)
    print(current_latitude)
    current_longitude = request.GET.get('currentLongitude', customer_profile.longitude)
    customer_profile.latitude = current_latitude
    customer_profile.longitude = current_longitude
    customer_profile.save()
    if request.method == "POST":
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        # email = request.POST.get('email')
        address = request.POST.get('address')
        
        # Check if a profile picture was uploaded
        if 'profile_pic' in request.FILES:
            profile_pic = request.FILES['profile_pic']
            user_profile.profile_pic = profile_pic

        user_profile.name = name
        user_profile.mobile = mobile
        user_profile.address = address
        # user_profile.email = email  # Update the email field of the CustomUser object

        user_profile.save()

        current_latitude = request.POST.get('latitude') or request.GET.get('currentLatitude')
        current_longitude = request.POST.get('longitude') or request.GET.get('currentLongitude')
        
       
        customer_profile.latitude = current_latitude
        customer_profile.longitude = current_longitude

        
        customer_profile.save()


        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')  # Redirect to the profile page
    context = {
        'cart_count' : cart_count,
        'user_profile': user_profile,
        'customer_profile' : customer_profile
    }

    return render(request, 'Customer/edit-profile.html', context)  
@login_required
def view_customer(request):
    customers = CustomUser.objects.filter(role='customer')  # Fetch all customer profiles from the database
    customer_count = customers.count() 
    context = {'customers': customers, 'customer_count': customer_count}
    return render(request, 'MainUser/userslist.html', context)
@login_required
def delete_customer(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
        user_account = customer.user
        customer.delete()
        user_account.delete()
        messages.success(request, 'Customer deleted successfully.')
        return redirect('view_customer')
    except Customer.DoesNotExist:
      
        return render(request, 'profile_not_found.html')

  


from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.platypus import PageBreak, Spacer
from django.http import HttpResponse
from django.db.models import Sum  # Import the Sum function
from datetime import datetime
from .models import Seller, Product, Customer  # Import your Customer model
from reportlab.lib.styles import getSampleStyleSheet

def generate_report(request):
    # Fetch the data for the report
    sellers = Seller.objects.all()
    customers = Customer.objects.all()  # Fetch customer details

    # Get the current date
    current_date = datetime.now().strftime("%Y-%m-%d")

    products_sold_by_seller = []
    products_added_by_seller = []

    for seller in sellers:
        # Calculate total products sold by the seller
        total_sold = OrderItem.objects.filter(product__seller=seller).aggregate(total_sold=Sum('quantity'))['total_sold'] or 0
        products_sold_by_seller.append({
            'seller__name': seller.user.name,
            'total_sold': total_sold
        })

        # Calculate total products added by the seller for the current month
        total_added = Product.objects.filter(seller=seller).count()
        products_added_by_seller.append({
            'seller__name': seller.user.name,
            'month': datetime.now().month,
            'total_added': total_added
        })

    # Create a PDF document
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Sleek_Mart_Report.pdf'

    doc = SimpleDocTemplate(response, pagesize=letter)
    story = []

    # Define the data for the table
    table_data = []
    table_data.append(["Seller Name", "Products Added", "Total Quantity of Products Sold"])
    
    for item in products_added_by_seller:
        table_data.append([item['seller__name'], item['total_added'], 0])

    for item in products_sold_by_seller:
        for row in table_data[1:]:
            if row[0] == item['seller__name']:
                row[2] = item['total_sold']
                break

    # Create the table and set its style
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.9, 0.9, 0.9)),
        ('TEXTCOLOR', (0, 0), (-1, 0), (0, 0, 0)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), (0.85, 0.85, 0.85)),
        ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),
    ]))

    # Add the heading and current date to the story
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading1']

    report_heading = Paragraph("SLEEKMART REPORT GENERATION", styleH)
    story.append(report_heading)

    story.append(Spacer(1, 12))

    report_date = Paragraph(f"Date: {current_date}", styleN)
    story.append(report_date)
    story.append(Spacer(1, 12))

    # Add the customer details table
    customer_table_data = [["Customer Name", "Email", "Phone"]]  # Define customer table structure
    for customer in customers:
        customer_table_data.append([customer.user.name, customer.user.email, customer.user.mobile])  # Populate customer data

    customer_table = Table(customer_table_data)
    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.9, 0.9, 0.9)),
        ('TEXTCOLOR', (0, 0), (-1, 0), (0, 0, 0)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), (0.85, 0.85, 0.85)),
        ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),
    ]))
    story.append(Paragraph("Customer and Seller Details:", styleH))
    story.append(customer_table)
    story.append(Spacer(1, 12))

    story.append(table)

    # Add a page break
    story.append(PageBreak())

    # Add a table for listing products by seller
    for seller in sellers:
        seller_products = Product.objects.filter(seller=seller)
        if seller_products:
            product_table_data = [["Product Name", "Price"]]
            for product in seller_products:
                product_table_data.append([product.name, product.selling_price])
            product_table = Table(product_table_data)
            product_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), (0.9, 0.9, 0.9)),
                ('TEXTCOLOR', (0, 0), (-1, 0), (0, 0, 0)),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), (0.85, 0.85, 0.85)),
                ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),
            ]))
            story.append(Paragraph(f"Products added by {seller.user.name}:", styleH))
            story.append(product_table)
            story.append(Spacer(1, 12))

    doc.build(story)
    return response





def view_products_by_category(request, category_slug):
    category = Category.objects.get(slug=category_slug)
    products = Product.objects.filter(category=category)
    context = {'category': category, 'products': products}
    return render(request, 'MainUser/view_products.html', context)

# def update_category(request, category_slug):
#     category = Category.objects.get(slug=category_slug)
    
#     if request.method == 'POST':
#         category.name = request.POST['name']
#         category.slug = request.POST['slug']
#         category.image = request.FILES.get('image', category.image)  # Use the existing image if not provided
#         category.description = request.POST('description')
        
#         category.save()
#         messages.success(request, 'Category updated successfully.')
#         return redirect('categories')

#     context = {'category': category}
#     return render(request, 'Seller/editcategory.html', context)

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('dashboard_home')


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'registration/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('dashboard_home')

def loggout(request):
    print('Logged Out')
    logout(request)

    return redirect('dashboard_home')
       
# def register(request):
#     if request.method == "POST":
#         username=request.POST['name']
#         mobile=request.POST['mobile']
#         email=request.POST['email']
#         password=request.POST['password']
#         confirmPassword=request.POST['confirmPassword']
#         if(password==confirmPassword):
#             if(User.objects.filter(username=username).exists()):
#                 messages.info('Username Exists')
#                 return redirect('register')
#             elif User.objects.filter(email=email).exists():
#                 messages.info(request,"Email Already Exists") 
#                 return redirect('register')
#             else:
#                 user=User.objects.create_user(username=username,mobile=mobile,email=email,password=password)
#                 user.save()
#                 return redirect('login_page')
#         else:
#             messages.info(request,"Password doesnt match") 
#             return redirect('register')
#     else:
#         return render (request, "Customer/register.html")
            # else:
            #     user=User.objects.create_user(username=username, mobile=mobile, email=email,password=password,confirmPassword=confirmPassword)
            #     user.set_password(password)
            #     user.save()
            #     return redirect('login_page')
        # if User.objects.filter(username=username).exists():
        #     messages.info(request,"Username Already Exists")
        #     return redirect('register')
        # elif User.objects.filter(email=email).exists():
        #     messages.info(request,"Email Already Exists") 
        #     return redirect('register')
        # else:
        #     user=User.objects.create_user(username=username,email=email,password=password)
        #     user.save()
        #     return redirect('login_page')
        # else:
        #     return render (request, "Customer/register.html")

