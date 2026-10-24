import unicodedata


# alphabetical key that ignores accents so "josé" becomes "jose"
def name_sort_key(name):
    folded = "".join(c for c in unicodedata.normalize("NFD", name) if not unicodedata.combining(c))
    return folded, name
