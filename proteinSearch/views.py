from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg

# Create your views here.

from .models import Product, PowderType, ProteinOrigin, UserReview

def product_list(request):

    products = Product.objects.all()

    powder_filter = request.GET.getlist('powder_type')
    if powder_filter:
        for pt_id in powder_filter:
            products = products.filter(
                productpowdertype__powder_type__id=pt_id
            )

    origin_filter = request.GET.getlist('protein_origin')
    if origin_filter:
        for o_id in origin_filter:
            products = products.filter(
                productproteinorigin__protein_origin__id=o_id
            )

    #Nutrition Filters
    max_calories = request.GET.get('max_calories')
    if max_calories:
        products = products.filter(nutritionfacts__calories_per_scoop__lte=max_calories)
    
    min_protein = request.GET.get('min_protein')
    if min_protein:
        products = products.filter(nutritionfacts__protein_grams__gte=min_protein)

    max_carbs = request.GET.get('max_carbs')
    if max_carbs:
        products = products.filter(nutritionfacts__carbs_grams__lte=max_carbs)

    max_fats = request.GET.get('max_fats')
    if max_fats:
        products = products.filter(nutritionfacts__fat_grams__lte=max_fats)

    max_bcaas = request.GET.get('max_bcaas')
    if max_bcaas:
        products = products.filter(nutritionfacts__bcaas_grams__lte=max_bcaas)

    if request.GET.get('sugar_free'):
        products = products.filter(nutritionfacts__sugar_free=True)

    #Serving Filters
    min_servings = request.GET.get('min_servings')
    if min_servings:
        products = products.filter(servinginfo__servings_per_container__gte=min_servings)

    max_price = request.GET.get('max_price')
    if max_price:
        products = products.filter(servinginfo__price_per_serving__lte=max_price)

    #Feature Filters
    features = ['additives_and_sweeteners', 'lactose_free', 'gluten_free', 'third_party_tested', 'scoop_included']
    for feature in features:
        if request.GET.get(feature):
            products = products.filter(**{f'features__{feature}': True})

    products = products.distinct().order_by('brand', 'model')

    products = products.annotate(avg_rating=Avg('userreview__rating'))

    powder_types = PowderType.objects.all()
    protein_origins = ProteinOrigin.objects.all()

    context = {
        'products': products,
        'powder_types': powder_types,
        'protein_origins': protein_origins,
        'selected_powder_types': powder_filter,
        'selected_protein_origins': origin_filter,
        'features': features,
    }

    return render(request, 'proteinSearch/product_list.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.userreview_set.all().order_by('-review_date')

    context = {
        'product': product,
        'reviews': reviews,
    }
    return render(request, 'proteinSearch/product_detail.html', context)

@login_required
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        review_text = request.POST.get('review_text', '').strip()
        rating = int(request.POST.get('rating', 0))
        if 1 <= rating <= 5:
            UserReview.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={
                    'title': title,
                    'review_text': review_text,
                    'rating': rating
                }
            )
        return redirect('product_detail', product_id=product.id)

