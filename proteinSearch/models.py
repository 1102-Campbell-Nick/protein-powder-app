from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Product(models.Model):
    brand = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    link = models.URLField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['brand', 'model'],
                name = 'unique_product'
            )
        ]

    @property
    def average_rating(self):
        reviews = self.userreview_set.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return None

class PowderType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class ProductPowderType(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    powder_type = models.ForeignKey(PowderType, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['product', 'powder_type'],
                name = 'unique_product_powdertype'
            )
        ]
    
class ProteinOrigin(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class ProductProteinOrigin(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    protein_origin = models.ForeignKey(ProteinOrigin, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['product', 'protein_origin'],
                name = 'unique_product_proteinorigin'
            )
        ]
    
class Features(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True)
    additives_and_sweeteners = models.BooleanField()
    gluten_free = models.BooleanField()
    third_party_tested = models.BooleanField()
    scoop_included = models.BooleanField()
    lactose_free = models.BooleanField()
    flavor_count = models.IntegerField()
    
class NutritionFacts(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True)
    calories_per_scoop = models.IntegerField(null=True, blank=True)
    protein_grams = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    carbs_grams = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fat_grams = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    bcaas_grams = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sugar_free = models.BooleanField()

class ServingInfo(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True)
    servings_per_container = models.IntegerField(null=True, blank=True)
    price_per_serving = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    unit_count_oz = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    item_weight_lbs = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

class AmazonInfo(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True)
    price_usd = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    available_on_amazon = models.BooleanField()
    amazon_rating = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    amazon_review_count = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

class UserReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    review_text = models.TextField()
    rating = models.PositiveSmallIntegerField()
    review_date = models.DateField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['product', 'user'],
                name = 'unique_review_per_user_per_product'
            )
        ]
