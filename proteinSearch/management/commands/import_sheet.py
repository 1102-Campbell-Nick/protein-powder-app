import json
import requests
import re
from django.core.management.base import BaseCommand
from proteinSearch.models import Product, PowderType, ProductPowderType, ProteinOrigin, ProductProteinOrigin, Features, NutritionFacts, ServingInfo, AmazonInfo
from decimal import Decimal, InvalidOperation

#Run with: "py manage.py import_sheet" when wanting to update database

SHEET_ID = '1miBRX60wdYAvMJO7sChEMXGnpIQHNqn6tnscHkXM7Qs'
GID = '92269346'

def get_sheet():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?gid={GID}&tqx=out:json"
    raw = requests.get(url).text
    match = re.search(r"setResponse\((.*)\);\s*$", raw, re.S)
    if not match:
        raise ValueError("Could not find JSON data in the response")
    return json.loads(match.group(1))

def clean_boolean(value):
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip().lower() == 'yes'
    return bool(value)

def clean_decimal(value, default = -1):
    if value is None:
        return default
    if isinstance(value, (int, float, Decimal)):
        return Decimal(value)
    
    value = str(value).strip()

    if value in ["", "-", "N/A", "NA", "n/a"]:
        return default
    
    try:
        return Decimal(value)
    except InvalidOperation:
        return default
    
def clean_int(value, default = -1):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

class Command(BaseCommand):
    help = 'Imports product data from a Google Sheet into the database'

    def handle(self, *args, **options):
        data = get_sheet()
        rows = data['table']['rows']

        for row in rows:
            c = row['c']

            if not c[1] or not c[1].get('v'):
                continue

            brand = c[0]["v"] if c[0] else ""
            model = c[1]["v"]
            link = c[30]["v"] if c[30] else ""

            product, created = Product.objects.update_or_create(brand=brand, model=model, defaults={"link": link})

            if c[3] and c[3].get("v"):
                ProductPowderType.objects.filter(product=product).delete()
                for pt in c[3]["v"].split(","):
                    pt = pt.strip()
                    obj, _ = PowderType.objects.get_or_create(name=pt)
                    ProductPowderType.objects.create(product=product, powder_type=obj)

            NutritionFacts.objects.update_or_create(
                product = product,
                defaults = {
                    "calories_per_scoop": clean_int(c[5]["v"] if c[5] else None),
                    "protein_grams": clean_decimal(c[6]["v"] if c[6] else None),
                    "carbs_grams": clean_decimal(c[7]["v"] if c[7] else None),
                    "fat_grams": clean_decimal(c[8]["v"] if c[8] else None),
                    "bcaas_grams": clean_decimal(c[10]["v"] if c[10] else None),
                    "sugar_free": clean_boolean(c[9]["v"] if c[9] else None),
                }
            )

            ServingInfo.objects.update_or_create(
                product = product,
                defaults = {
                    "servings_per_container": clean_int(c[12]["v"] if c[12] else None),
                    "price_per_serving": clean_decimal(c[13]["v"] if c[13] else None),
                    "unit_count_oz": clean_decimal(c[14]["v"] if c[14] else None),
                    "item_weight_lbs": clean_decimal(c[15]["v"] if c[15] else None),
                }
            )

            Features.objects.update_or_create(
                product = product,
                defaults = {
                    "additives_and_sweeteners": clean_boolean(c[19]["v"] if c[19] else None),
                    "gluten_free": clean_boolean(c[20]["v"] if c[20] else None),
                    "third_party_tested": clean_boolean(c[21]["v"] if c[21] else None),
                    "scoop_included": clean_boolean(c[22]["v"] if c[22] else None),
                    "lactose_free": clean_boolean(c[23]["v"] if c[23] else None),
                    "flavor_count": clean_int(c[17]["v"] if c[17] else 0),
                }
            )

            if c[24] and c[24].get("v"):
                ProductProteinOrigin.objects.filter(product=product).delete()
                for o in c[24]["v"].split(","):
                    o = o.strip()
                    obj, _ = ProteinOrigin.objects.get_or_create(name=o)
                    ProductProteinOrigin.objects.create(product=product, protein_origin=obj)

            AmazonInfo.objects.update_or_create(
                product = product,
                defaults = {
                    "price_usd": clean_decimal(c[26]["v"] if c[26] else None),
                    "available_on_amazon": clean_boolean(c[27]["v"] if c[27] else None),
                    "amazon_rating": clean_decimal(c[28]["v"] if c[28] else None),
                    "amazon_review_count": clean_int(c[29]["v"] if c[29] else None),
                }
            )
