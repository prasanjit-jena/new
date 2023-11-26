from rest_framework import serializers
from .models import Vendor, HistoricalPerformance,PurchaseOrder

class HistoricalPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalPerformance
        fields = '__all__'

class VendorSerializer(serializers.ModelSerializer):
    # performance_metrics = HistoricalPerformanceSerializer(many=True, read_only=True, source='historicalperformance_set')
    class Meta:
        model = Vendor
        fields = '__all__'

class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'

class PurchaseOrderAcknowledgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = ['acknowledgment_date']