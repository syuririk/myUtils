from ..services.children import children
from ..services.category import category

def searchCategory(category_id):
    data = category(category_id)
    try:
        result = data[0]
        result['children'] = children(category_id)
    except:
        result = data
    return data