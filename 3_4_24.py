import sqlite3;

class User:
    def __init__(self, user_id, username, password, email):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email

class Product:
    def __init__(self, product_id, name, description, price):
        self.product_id = product_id
        self.name = name
        self.description = description
        self.price = price

class Cart:
    def __init__(self, cart_id, user_id, status, total_price=0):
        self.cart_id = cart_id
        self.user_id = user_id
        self.status = status
        self.total_price = total_price

class CartService:
    def __init__(self, database):
        self.database = database

    def add_to_cart(self, user_id, product_id, quantity):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        try:
            # Check if the user already has an active cart
            cursor.execute("SELECT cart_id FROM Cart WHERE user_id = ? AND status = 'active'", (user_id,))
            cart_id = cursor.fetchone()

            if cart_id:
                cart_id = cart_id[0]
            else:
                # Create a new cart if the user doesn't have an active one
                cursor.execute("INSERT INTO Cart (user_id, status) VALUES (?, 'active')", (user_id,))
                cart_id = cursor.lastrowid

            # Check if the item is already in the cart
            cursor.execute("SELECT cart_item_id FROM CartItem WHERE cart_id = ? AND product_id = ?", (cart_id, product_id))
            cart_item = cursor.fetchone()

            if cart_item:
                # Update quantity if item is already in the cart
                cart_item_id = cart_item[0]
                cursor.execute("UPDATE CartItem SET quantity = quantity + ? WHERE cart_item_id = ?", (quantity, cart_item_id))
            else:
                # Insert new item into the cart
                cursor.execute("INSERT INTO CartItem (cart_id, product_id, quantity) VALUES (?, ?, ?)", (cart_id, product_id, quantity))

            conn.commit()
        finally:
            conn.close()

    def remove_from_cart(self, user_id, cart_item_id):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        try:
            # Check if the cart item belongs to the user
            cursor.execute("SELECT Cart.user_id FROM CartItem JOIN Cart ON CartItem.cart_id = Cart.cart_id WHERE cart_item_id = ?", (cart_item_id,))
            result = cursor.fetchone()

            if not result or result[0] != user_id:
                raise Exception("Cart item does not belong to the user.")

            # Remove the item from the cart
            cursor.execute("DELETE FROM CartItem WHERE cart_item_id = ?", (cart_item_id,))
            conn.commit()
        finally:
            conn.close()

    def sign_out_cart(self, user_id):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        try:
            # Update the status of the user's active cart to 'signed_out'
            cursor.execute("UPDATE Cart SET status = 'signed_out' WHERE user_id = ? AND status = 'active'", (user_id,))
            conn.commit()
        finally:
            conn.close()