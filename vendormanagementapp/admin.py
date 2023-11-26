from django.contrib import admin
from .models import Vendor,HistoricalPerformance,PurchaseOrder

# Register your models here.

class VendorAdmin(admin.ModelAdmin):
    list_display = ['id','name','contact_details','address','vendor_code','on_time_delivery_rate','quality_rating_avg','average_response_time','fulfillment_rate']
    search_fields = ['name','vendor_code']

admin.site.register(Vendor,VendorAdmin)

class HistoricalPerformanceAdmin(admin.ModelAdmin):
    list_display = ['vendor','date','on_time_delivery_rate','quality_rating_avg','average_response_time','fulfillment_rate']
    search_fields = ['vendor']

admin.site.register(HistoricalPerformance,HistoricalPerformanceAdmin)


class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['id','po_number','vendor','order_date','delivery_date','items','quantity','status','quality_rating','issue_date','issue_date','acknowledgment_date']
    search_fields = ['po_number','vendor','items']

admin.site.register(PurchaseOrder,PurchaseOrderAdmin)