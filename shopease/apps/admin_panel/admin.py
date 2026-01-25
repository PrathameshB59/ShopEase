from django.contrib import admin
from apps.admin_panel.models import AdminRole, AdminActivity, Refund


@admin.register(AdminRole)
class AdminRoleAdmin(admin.ModelAdmin):
    """Admin interface for AdminRole model."""
    list_display = ['user', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AdminActivity)
class AdminActivityAdmin(admin.ModelAdmin):
    """Admin interface for AdminActivity model."""
    list_display = ['user', 'action', 'timestamp', 'ip_address']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'description']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """Admin interface for Refund model."""
    list_display = ['refund_id_short', 'order_id_short', 'amount', 'status', 'created_at']
    list_filter = ['status', 'reason', 'created_at']
    search_fields = ['refund_id', 'order__order_id', 'description']
    readonly_fields = ['refund_id', 'created_at', 'processed_at', 'completed_at']
    date_hierarchy = 'created_at'

    def refund_id_short(self, obj):
        return f"#{str(obj.refund_id)[:8]}"
    refund_id_short.short_description = 'Refund ID'

    def order_id_short(self, obj):
        return f"#{str(obj.order.order_id)[:8]}"
    order_id_short.short_description = 'Order ID'
