# utils.py
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_content_based_recommendations(query, subcategory_id, Product, top_n=5):
    """
    دالة توصية تعتمد على المحتوى:
    - جلب جميع المنتجات من القسم الفرعي.
    - دمج الحقول المهمة: اسم المنتج، الوصف، اسم القسم الفرعي واسم القسم الرئيسي.
    - حساب تمثيل TF-IDF للنصوص وحساب التشابه الكوني مع الاستعلام.
    - إرجاع أعلى المنتجات من حيث التشابه.
    """
    products = Product.objects.filter(sub_category_id=subcategory_id)
    if not products.exists():
        return []
    
    product_texts = []
    product_list = []
    for product in products:
        text = f"{product.name} {product.description} {product.sub_category.name} {product.sub_category.parent_category.name}"
        product_texts.append(text)
        product_list.append(product)
    
    # إضافة الاستعلام في بداية القائمة للمقارنة
    texts = [query] + product_texts

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(texts)

    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    top_indices = cosine_sim.argsort()[::-1][:top_n]
    recommended_products = [product_list[i] for i in top_indices]
    
    return recommended_products


