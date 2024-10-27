from models import storage
from models.product import Product
from models.store import Store

def update_all_product_relations():
    """Updates product relations for all products."""
    all_products = storage.all(Product).values()
    all_stores = storage.all(Store).values()
    
    for product in all_products:
        potential_matches = []
        for store in all_stores:
            if store.id != product.store_id:
                # This is a simple example. You might want to use more sophisticated
                # methods to find potential matches, such as text similarity on product names.
                store_products = store.products
                potential_matches.extend(store_products)
        
        Product.update_product_relations(product, potential_matches)

# Run this function periodically, e.g., daily or weekly
update_all_product_relations()
