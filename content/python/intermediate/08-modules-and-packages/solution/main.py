from shop import Cart


def main():
    cart = Cart()
    cart.add("coffee", 25000, 2)
    cart.add("bread", 18000)
    print("total:", cart.total(discount_percent=10))


if __name__ == "__main__":
    main()
