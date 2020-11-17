import os
import csv

from .models import Product


def calculate_retail_price(vendor_price: int) -> float:
    if vendor_price < 1000:
        return vendor_price * 1.2
    return vendor_price * 1.1


def upload_vendor_products(path_to_file):
    data = convert_csv_to_dict(path_to_file)

    prepare_products = list()

    for d in data[1:]:
        _code, _name, _price = d

        price = int(_price)

        r_price = calculate_retail_price(price)
        p_price = .9 * price
        name = str(_name)
        sku = f"{str(_code)}{name}"

        prepare_products.append(
            Product(
                retail_price=r_price,
                purchase_price=p_price,
                name=name,
                sku=sku)
        )

    return Product.objects.bulk_create(prepare_products)


def convert_csv_to_dict(file_to_path) -> list:
    file_exist(file_to_path)

    with open(file_to_path) as fp:
        products = [row for row in csv.reader(fp, delimiter=';')]

    return products


def file_exist(file_to_path):
    if os.path.isfile(file_to_path):
        return True
    raise FileNotFoundError
