from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Vendor, HistoricalPerformance,PurchaseOrder
from .serializers import VendorSerializer, HistoricalPerformanceSerializer,PurchaseOrderSerializer,PurchaseOrderAcknowledgeSerializer
from django.db.models import Count, F, Sum
from django.http import Http404
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import models



class VendorListCreateView(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

class VendorRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

# class VendorPerformanceView(generics.RetrieveAPIView):
#     queryset = Vendor.objects.all()
#     serializer_class = VendorSerializer

#     def retrieve(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance)
#         # Calculate performance metrics using database-level aggregations
#         completed_pos = instance.purchase_orders.filter(status='completed')
#         total_completed_pos = completed_pos.count()

#         performance_metrics = {
#             'on_time_delivery_rate': completed_pos.filter(delivery_date__lte=F('acknowledgment_date')).count() / total_completed_pos if total_completed_pos > 0 else 0,
#             'quality_rating_avg': completed_pos.filter(quality_rating__isnull=False).aggregate(avg_quality=Sum('quality_rating'))['avg_quality'] / total_completed_pos if total_completed_pos > 0 else 0,
#             'average_response_time': completed_pos.filter(acknowledgment_date__isnull=False).aggregate(avg_response_time=Sum(F('acknowledgment_date') - F('issue_date'), output_field=models.DurationField()))['avg_response_time'].total_seconds() / total_completed_pos if total_completed_pos > 0 else 0,
#             'fulfillment_rate': completed_pos.filter(quality_rating__isnull=True).count() / instance.purchase_orders.count() if total_completed_pos > 0 else 0,
#         }

#         data = serializer.data
#         data.update(performance_metrics)
#         return Response(data)


class VendorPerformanceView(generics.RetrieveAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Calculate performance metrics using database-level aggregations
        completed_pos = PurchaseOrder.objects.filter(vendor=instance, status='completed')
        total_completed_pos = completed_pos.count()

        performance_metrics = {
            'on_time_delivery_rate': completed_pos.filter(delivery_date__lte=F('acknowledgment_date')).count() / total_completed_pos if total_completed_pos > 0 else 0,
            'quality_rating_avg': completed_pos.filter(quality_rating__isnull=False).aggregate(avg_quality=Sum('quality_rating'))['avg_quality'] / total_completed_pos if total_completed_pos > 0 else 0,
            'average_response_time': completed_pos.filter(acknowledgment_date__isnull=False).aggregate(avg_response_time=Sum(F('acknowledgment_date') - F('issue_date'), output_field=models.DurationField()))['avg_response_time'].total_seconds() / total_completed_pos if total_completed_pos > 0 else 0,
            'fulfillment_rate': completed_pos.filter(quality_rating__isnull=True).count() /total_completed_pos  if total_completed_pos > 0 else 0,
        }

        data = serializer.data
        data.update(performance_metrics)
        # print(data)
        return Response(performance_metrics)

class AcknowledgePurchaseOrderView(generics.UpdateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderAcknowledgeSerializer

    def update(self, request, *args, **kwargs):
        po_id = kwargs.get('pk')

        try:
            purchase_order = self.get_object()
        except PurchaseOrder.DoesNotExist:
            raise Http404("Purchase Order does not exist")

        acknowledgment_date = request.data.get('acknowledgment_date', None)
        print(acknowledgment_date)
        if acknowledgment_date is not None:
            # Validate and set the provided acknowledgment date
            purchase_order.acknowledgment_date = acknowledgment_date
            purchase_order.save()
            return Response({'message': 'Acknowledgment updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Acknowledgment date is required'}, status=status.HTTP_400_BAD_REQUEST)

        

# Signal to update vendor metrics when a new purchase order is saved
@receiver(post_save, sender=PurchaseOrder)
def update_vendor_metrics(sender, instance, **kwargs):
    vendor = instance.vendor
    completed_pos = vendor.purchaseorder_set.filter(status='completed')
    total_completed_pos = completed_pos.count()

    if total_completed_pos > 0:
        vendor.on_time_delivery_rate = completed_pos.filter(delivery_date__lte=F('acknowledgment_date')).count() / total_completed_pos
        vendor.quality_rating_avg = completed_pos.filter(quality_rating__isnull=False).aggregate(avg_quality=Sum('quality_rating'))['avg_quality'] / total_completed_pos
        vendor.average_response_time = completed_pos.filter(acknowledgment_date__isnull=False).aggregate(avg_response_time=Sum(F('acknowledgment_date') - F('issue_date'), output_field=models.DurationField()))['avg_response_time'].total_seconds() / total_completed_pos
        vendor.fulfillment_rate = completed_pos.filter(quality_rating__isnull=True).count() / vendor.purchaseorder_set.count()
        vendor.save()

class PurchaseOrderListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

class PurchaseOrderRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer