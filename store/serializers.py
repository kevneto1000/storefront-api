from rest_framework import serializers
from .models import Product, Order, OrderItem


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "description", "price_kobo", "stock"]


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "unit_price_kobo"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "status", "total_kobo", "created_at", "paid_at", "items"]


class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, max_value=100)


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemInputSerializer(many=True, allow_empty=False)

    def validate_items(self, items):
        ids = [item["product_id"] for item in items]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Each product can appear only once.")
        return items