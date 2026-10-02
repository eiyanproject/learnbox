import base64

ORIGINAL = {
    "readme.txt": b"project files",
    "logo.png": base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4//8/AAX+Av4N70a4AAAAAElFTkSuQmCC"),
    "config.ini": b"mode=prod",
}
CURRENT = {
    "readme.txt": b"project files",
    "logo.png": base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4//8/AAX+Av4N70a4AAAAAElFTkSuQmCCZmxhZ3toaWRkZW5fYWZ0ZXJfdGhlX2ltYWdlX2VuZHN9"),
    "config.ini": b"mode=prod",
}
