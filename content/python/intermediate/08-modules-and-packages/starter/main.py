from shop import Cart

cart = Cart()
cart.add("coffee", 25000, 2)
cart.add("bread", 18000)
print("total:", cart.total(discount_percent=10))
