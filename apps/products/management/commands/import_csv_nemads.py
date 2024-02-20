#import urllib
#import urllib.request
#import pandas as pd
#import uuid
#import os
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'i will insert data from csv file '

    def add_arguments(self, parser):
        parser.add_argument('csv_path',type=str,help='specifies csv path for exam : /csv/data.csv ')

    def handle(self, *args, **kwargs):
        
       # df = pd.read_csv("csv/data.csv")
         self.stdout.write(self.style.SUCCESS("read  data.csv "))

    # for id, vendor_id, title, image, total_sales, post_content, status, stock_qty, price, category in zip(df.ID, df.post_author, df.post_title, df.images, df.total_sales, df.post_content, df.post_status, df.stock, df.regular_price, df.product_cat):
    # Check if the product with the same 'id' already exists in the database
    # product_check = Product.objects.filter(id=id).first()
    # if product_check:
    #     self.stdout.write(self.style.ERROR(f"Product {id} already exists"))
    # else:
    #     # Fetch the 'Vendor' and 'User' objects based on 'vendor_id'
    #     vendor = Vendor.objects.get(id=vendor_id)
    #     user = User.objects.get(id=vendor_id)

    #     # Create a new 'Product' object
    #     product = Product(
    #         id=id,
    #         vendor=vendor,
    #         user=user,
    #         title=title,
    #         stock_qty=stock_qty,
    #         price=price or 0,
    #         orders=total_sales,
    #         description=post_content,
    #         status=("published" if status == "publish" else "draft")
    #     )
    #     product.save()

    # Generate a unique slug for the product
    # uuid_key = uuid.uuid4()
    # uniqueid = uuid_key[:4]
    # product.slug = slugify(product.title) + "-" + str(uniqueid.lower())

    # Save the image URL to the database and download the image
    # image_url = image
    # image_name = image_url.split('/')[-1]
    # response = urllib.request.urlopen(image_url)
    # image_file = File(response)
    # product.image.save(image_name, image_file)
    # product.save()

    # # Add categories to the product
    # category_list = category.split(",")
    # for c in category_list:
    #     print("Category =============", c)
    #     category_ = Category.objects.get(title=c)
    #     product.category.add(category_)

    # product.save()

    # self.stdout.write(self.style.SUCCESS(f"Product {id} created"))
