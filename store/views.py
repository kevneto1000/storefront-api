from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Order, Product
from .serializers import OrderCreateSerializer, OrderSerializer, ProductSerializer
from .services import create_order


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).order_by("id")
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items__product")
            .order_by("-created_at")
        )

    def create(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = create_order(request.user, serializer.validated_data["items"])
        order = self.get_queryset().get(pk=order.pk)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
