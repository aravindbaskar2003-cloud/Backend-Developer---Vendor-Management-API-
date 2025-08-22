from django.db import models
from django.contrib.auth.models import AbstractUser

class Vendor(AbstractUser):
    company_name = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    rating = models.FloatField(default=0)
    location = models.CharField(max_length=100)

class Service(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    price = models.FloatField()

class Availability(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateField()
    is_blocked = models.BooleanField(default=False)

class Booking(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    date = models.DateField()
    guests = models.IntegerField()
    total_cost = models.FloatField()
    confirmed = models.BooleanField(default=False)

class Review(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=100)
    rating = models.IntegerField()
    comment = models.TextField()

python manage.py makemigrations
python manage.py migrate

from rest_framework import serializers
from .models import Vendor, Service, Availability, Booking, Review

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Vendor, Service, Availability, Booking, Review
from .serializers import VendorSerializer, ServiceSerializer, AvailabilitySerializer, BookingSerializer, ReviewSerializer

class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [IsAuthenticated]

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

class AvailabilityViewSet(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer
    permission_classes = [IsAuthenticated]

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

from rest_framework import routers
from .views import VendorViewSet, ServiceViewSet, AvailabilityViewSet, BookingViewSet, ReviewViewSet

router = routers.DefaultRouter()
router.register(r'vendors', VendorViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'availability', AvailabilityViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = router.urls

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('vendors.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# inside BookingViewSet
def perform_create(self, serializer):
    service = serializer.validated_data['service']
    date = serializer.validated_data['date']
    if Availability.objects.filter(service=service, date=date, is_blocked=True).exists():
        raise serializers.ValidationError("Date is blocked")
    guests = serializer.validated_data['guests']
    total_cost = service.price * guests * 1.18  # 18% tax
    serializer.save(total_cost=total_cost, confirmed=True)

python manage.py runserver
