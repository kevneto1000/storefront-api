from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError

from .models import Order, OrderItem, Product


def create_order(user, items):
    with transaction.atomic():
        order = Order.objects.create(user=user)
        total = 0

        # Always process products in the same order to avoid deadlocks
        for item in sorted(items, key=lambda i: i["product_id"]):
            product = Product.objects.filter(id=item["product_id"], is_active=True).first()
            if product is None:
                raise ValidationError({"items": f"Product {item['product_id']} not found."})

            # One atomic step: only decrement if enough stock remains
            updated = Product.objects.filter(
                id=product.id, stock__gte=item["quantity"]
            ).update(stock=F("stock") - item["quantity"])

            if updated == 0:
                raise ValidationError({"items": f"Not enough stock for {product.name}."})

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item["quantity"],
                unit_price_kobo=product.price_kobo,
            )
            total += product.price_kobo * item["quantity"]

        order.total_kobo = total
        order.save(update_fields=["total_kobo"])

    return order