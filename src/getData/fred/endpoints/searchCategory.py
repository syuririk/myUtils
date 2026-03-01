from getData.fred.services.children import children
from getData.fred.services.category import category

def searchCategory(category_id):
    data = category(category_id)
    try:
        result = data.get('categories')[0]
        result['children'] = children(category_id)
    except:
        result = data
    return data