from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .models import Customer, CustomUser, Seller, AddWishlist,WishlistItems,AddCart, CartItems, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Category, Product, Subcategory, Rating
from django.urls import reverse
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect


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

def search_categories(request):
    search_query = request.GET.get('q', '')

    if search_query:
        # Use a case-insensitive filter to find matching categories
        categories = Category.objects.filter(name__icontains=search_query)

        # Create a list of dictionaries containing category information
        results = [{'name': category.name, 'description': category.description, 'slug': category.slug, 'image_url': category.image.url} for category in categories]

        return JsonResponse({'results': results})
    else:
        return JsonResponse({'results': []})


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
    if request.user.is_authenticated:
        user_id = request.user.id
        user=request.user
        # Fetch the user's wishlist products' IDs and count
        cart_count = CartItems.objects.filter(cart__user=user).count()
        wishlist = WishlistItems.objects.filter(wishlist__user_id=user_id).values_list('products__id', flat=True)
        wishlist_count = WishlistItems.objects.filter(wishlist__user=user).count()
    context = {
        'categories':categories,
        'product': product,
        'wishlist': wishlist,
        'wishlist_count': wishlist_count, 
        'cart_count':cart_count
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
     
    print('entered')
    
    if request.method == 'POST':
        print('entered')

        
        # Get the product and quantity from the form
        product = Product.objects.get(pk=product_id)
        quantity = int(request.POST.get('selected_quantity', 1))
        
        # Get or create the user's cart
        user = request.user
        cart, created = AddCart.objects.get_or_create(user=user)

        # Check if the product is already in the cart, if so, update the quantity
        existing_item = CartItems.objects.filter(cart=cart, product=product).first()
        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()
        else:
            # Create a new cart item
            CartItems.objects.create(cart=cart, product=product, quantity=quantity)

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
@login_required
def update_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItems, pk=cart_item_id)
    
    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity', 1))
        
        # Update the quantity of the cart item
        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            # Handle invalid quantity (e.g., remove the item from the cart)
            cart_item.delete()
        
    return redirect('cart_details')
# def update_cart_item(request, cart_item_id):
#     if request.method == 'POST':
#         try:
#             cart_item = CartItems.objects.get(id=cart_item_id)
#         except CartItems.DoesNotExist:
#             return JsonResponse({'error': 'Cart item not found'}, status=400)

#         new_quantity = int(request.POST.get('quantity', 1))
#         if new_quantity < 1:
#             return JsonResponse({'error': 'Invalid quantity'}, status=400)

#         cart_item.quantity = new_quantity
#         cart_item.save()

#         # Calculate the updated total price
#         total_price = cart_item.product.selling_price * cart_item.quantity

#         return JsonResponse({'total_price': total_price})

#     return JsonResponse({'error': 'Invalid request method'}, status=400)
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
    # Get the user's cart items
    cart_items = CartItems.objects.filter(cart__user=request.user)

    # Calculate the total price for the order
    total_price = sum(cart_item.total_price for cart_item in cart_items)

    # Create a new order
    order = Order.objects.create(user=request.user, total_price=total_price)

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

    # Clear the user's cart
    # cart_items.delete()

    return redirect('checkout_complete', order_id=order.id)

@login_required  # Ensure the user is logged in to access this view
def checkout_complete(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        order_items = order.items.all()  # Retrieve order items associated with the order
    except Order.DoesNotExist:
        # Handle the case where the order doesn't exist or doesn't belong to the user
        return render(request, 'error.html', {'error_message': 'Order not found.'})

    # Pass order and order items to the template for display
    return render(request, 'Customer/checkout_complete.html', {'order': order, 'order_items': order_items})

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

@csrf_protect
def rate_product(request):
    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        product_id = request.POST.get('product_id')

        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'You must be logged in to rate products.'}, status=403)

        # Check if the rating value is valid (1 to 5)
        try:
            rating_value = int(rating_value)
            if rating_value < 1 or rating_value > 5:
                raise ValueError('Invalid rating value')
        except ValueError:
            return JsonResponse({'error': 'Invalid rating value'}, status=400)

        # Check if the product exists
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)

        # Check if the user has already rated this product
        existing_rating = Rating.objects.filter(user=request.user, product=product).first()
        if existing_rating:
            return JsonResponse({'error': 'You have already rated this product.'}, status=403)

        # Create a new rating entry
        new_rating = Rating(user=request.user, product=product, rating=rating_value)
        new_rating.save()

        return JsonResponse({'message': 'Rating saved successfully'})
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
    
@login_required
def index(request):
    customers = CustomUser.objects.filter(role='customer', is_active = True)
    products = Product.objects.filter(status=False)
    sellers = Seller.objects.filter(is_approved='approved')
    product_count = products.count()
    customer_count = customers.count() 
    seller_count = sellers.count()
    context = {'customer_count': customer_count, 'product_count':product_count, 'seller_count':seller_count}
    return render(request, 'MainUser/index.html', context)
@login_required
def sellerindex(request):
    categories = Category.objects.filter(status=False)
    category_count = categories.count() 
    seller = Seller.objects.get(user=request.user)
    product_count = Product.objects.filter(seller=seller, status=False).count()
    context = {'category_count': category_count, 'product_count': product_count}
    return render(request, 'Seller/sellerindex.html', context)
@login_required
def sellerprofile(request):
    return render(request, 'Seller/sellerprofile.html')
@login_required
def editseller(request):
    user_profile = CustomUser.objects.get(pk=request.user.pk)  # Get the CustomUser object
    seller_profile = Seller.objects.get(user=user_profile)
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
        
        if 'seller_proof' in request.FILES:
            seller_proof = request.FILES['seller_proof']
            seller_profile.seller_proof = seller_proof
        
        seller_profile.business_name = business_name
        seller_profile.business_address = business_address
        seller_profile.business_website = business_website
            

        
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
        description = request.POST['description']

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
@login_required
def profile(request):
    
    cart_count = 0
    if request.user.is_authenticated:
        user = request.user
        cart_count = CartItems.objects.filter(cart__user=user).count()
    context = {
        'cart_count' : cart_count
    }
    return render(request, 'Customer/profile.html', context)
@login_required
def edit_profile(request):
    user_profile = CustomUser.objects.get(pk=request.user.pk)  # Get the CustomUser object
    cart_count = 0
    if request.user.is_authenticated:
        user = request.user
        cart_count = CartItems.objects.filter(cart__user=user).count()
    
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

        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')  # Redirect to the profile page
    context = {
        'cart_count' : cart_count,
        'user_profile': user_profile
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

  


  # Display the category creation form



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

