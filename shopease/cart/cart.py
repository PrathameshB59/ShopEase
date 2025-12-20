# cart/cart.py

"""
Shopping Cart System - Session-Based Cart

We're building a cart that lives in the user's session.
Think of a session like a temporary note that belongs to one visitor.

Why session-based instead of database?
1. Works for guests (not logged in)
2. Faster - no database queries needed
3. Automatically clears when session expires
4. Simple to implement

When user logs in and checks out, we convert cart to Order in database.
"""

from decimal import Decimal
from products.models import Product


class Cart:
    """
    Shopping Cart Class
    
    This class wraps around the Django session to provide
    cart functionality with a clean interface.
    
    Instead of directly manipulating session data everywhere,
    we use this class which provides methods like:
    - cart.add(product, quantity)
    - cart.remove(product_id)
    - cart.clear()
    
    Much cleaner and easier to maintain!
    """
    
    def __init__(self, request):
        """
        Initialize the cart from the current session
        
        When someone visits your site, Django creates a session for them.
        We store the cart data in request.session['cart']
        
        If they don't have a cart yet, we create an empty one.
        """
        self.session = request.session
        
        # Try to get existing cart from session
        cart = self.session.get('cart')
        
        if not cart:
            # No cart exists, create empty one
            # We'll store cart as a dictionary:
            # {'product_id': {'quantity': 2, 'price': '29.99'}, ...}
            cart = self.session['cart'] = {}
        
        self.cart = cart
    
    def add(self, product, quantity=1, update_quantity=False):
        """
        Add a product to the cart or update its quantity
        
        Parameters:
            product: Product object to add
            quantity: How many to add (default 1)
            update_quantity: If True, set quantity. If False, add to existing.
        
        Example:
            cart.add(product, quantity=2)  # Add 2 of this product
            cart.add(product, quantity=5, update_quantity=True)  # Set to exactly 5
        """
        # Convert product ID to string (JSON requires string keys)
        product_id = str(product.id)
        
        # Get the current price (sale price if on sale, otherwise regular)
        price = str(product.get_display_price)
        
        if product_id not in self.cart:
            # Product not in cart, add it
            self.cart[product_id] = {
                'quantity': 0,
                'price': price,
                # Store product details for display
                'name': product.name,
                'slug': product.slug,
            }
        
        if update_quantity:
            # Set to exact quantity
            self.cart[product_id]['quantity'] = quantity
        else:
            # Add to existing quantity
            self.cart[product_id]['quantity'] += quantity
        
        # Make sure we don't exceed available stock
        if self.cart[product_id]['quantity'] > product.stock:
            self.cart[product_id]['quantity'] = product.stock
        
        self.save()
    
    def remove(self, product_id):
        """
        Remove a product from the cart completely
        
        Example:
            cart.remove('5')  # Remove product with ID 5
        """
        product_id = str(product_id)
        
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def save(self):
        """
        Mark the session as modified to ensure it's saved
        
        Django only saves session if you explicitly tell it the session changed.
        Otherwise, it assumes nothing changed and doesn't update the database.
        """
        self.session.modified = True
    
    def clear(self):
        """
        Empty the cart completely
        
        Used after successful checkout
        """
        del self.session['cart']
        self.save()
    
    def update_quantity(self, product_id, quantity):
        """
        Update quantity of a specific product
        
        Example:
            cart.update_quantity('5', 3)  # Set product 5 to quantity 3
        """
        product_id = str(product_id)
        
        if product_id in self.cart:
            if quantity > 0:
                self.cart[product_id]['quantity'] = quantity
            else:
                # If quantity is 0 or negative, remove item
                del self.cart[product_id]
            
            self.save()
    
    def __iter__(self):
        """
        Iterate through cart items and add product objects
        
        This allows you to do: for item in cart
        Each item will have full product details
        """
        # Get all product IDs in cart
        product_ids = self.cart.keys()
        
        # Fetch all products in one query (efficient!)
        products = Product.objects.filter(id__in=product_ids)
        
        # Create a lookup dictionary for quick access
        product_lookup = {str(product.id): product for product in products}
        
        # Iterate through cart and add product objects
        for product_id, item in self.cart.items():
            if product_id in product_lookup:
                # Add full product object to item
                item['product'] = product_lookup[product_id]
                
                # Calculate total price for this item
                item['total_price'] = Decimal(item['price']) * item['quantity']
                
                # Check if product is still available
                product = item['product']
                item['in_stock'] = product.is_in_stock
                item['available_quantity'] = product.stock
                
                yield item
    
    def __len__(self):
        """
        Count total items in cart
        
        This allows you to do: len(cart)
        Returns total quantity of all items
        """
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        """
        Calculate total price of all items in cart
        
        Returns: Decimal representing total cost
        """
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )
    
    def get_item_count(self):
        """
        Get total number of unique products
        
        Different from __len__ which counts quantities
        This just counts how many different products
        
        Example:
            Cart has 2x Product A and 3x Product B
            __len__() returns 5 (total items)
            get_item_count() returns 2 (unique products)
        """
        return len(self.cart)
    
    def is_empty(self):
        """Check if cart has any items"""
        return len(self.cart) == 0


"""
How the Cart Works in Practice:

1. USER ADDS PRODUCT TO CART:
   
   In views.py:
   ```python
   def add_to_cart(request, product_id):
       product = get_object_or_404(Product, id=product_id)
       cart = Cart(request)  # Initialize cart from session
       quantity = int(request.POST.get('quantity', 1))
       cart.add(product, quantity)
       messages.success(request, f'{product.name} added to cart!')
       return redirect('cart:cart_detail')
   ```

2. VIEWING THE CART:
   
   In views.py:
   ```python
   def cart_detail(request):
       cart = Cart(request)
       return render(request, 'cart/detail.html', {'cart': cart})
   ```
   
   In template:
   ```html
   {% for item in cart %}
       <div>{{ item.product.name }} - Qty: {{ item.quantity }}</div>
   {% endfor %}
   Total: ₹{{ cart.get_total_price }}
   ```

3. REMOVING FROM CART:
   
   ```python
   def remove_from_cart(request, product_id):
       cart = Cart(request)
       cart.remove(product_id)
       return redirect('cart:cart_detail')
   ```

4. CHECKOUT PROCESS:
   
   ```python
   def checkout(request):
       cart = Cart(request)
       
       if cart.is_empty():
           messages.error(request, 'Your cart is empty')
           return redirect('products:product_list')
       
       # Create order from cart
       order = Order.objects.create(
           user=request.user,
           ... shipping details ...
       )
       
       # Create order items from cart
       for item in cart:
           OrderItem.objects.create(
               order=order,
               product=item['product'],
               quantity=item['quantity'],
               price=item['price']
           )
       
       # Calculate totals
       order.calculate_totals()
       
       # Clear cart after successful order
       cart.clear()
       
       return redirect('orders:order_confirmation', order.order_number)
   ```

5. WHY SESSION-BASED?
   
   Database-based cart would require:
   - User must be logged in to add to cart
   - More database queries (slower)
   - Abandoned carts fill up database
   - Need cleanup job to remove old carts
   
   Session-based cart:
   - Works for guests
   - Fast (no DB queries until checkout)
   - Automatically cleans up (sessions expire)
   - Simple to implement

6. SESSION DATA STRUCTURE:
   
   request.session['cart'] looks like:
   {
       '1': {
           'quantity': 2,
           'price': '29.99',
           'name': 'Blue T-Shirt',
           'slug': 'blue-t-shirt'
       },
       '5': {
           'quantity': 1,
           'price': '49.99',
           'name': 'Running Shoes',
           'slug': 'running-shoes'
       }
   }

This cart system is production-ready and handles:
- Adding/removing products
- Updating quantities
- Stock validation
- Price calculation
- Guest shopping
- Easy conversion to orders
"""