from django.contrib import admin
from django.utils.html import format_html
from .models import MonitoredChannel, MonitoringSchedule


@admin.register(MonitoredChannel)
class MonitoredChannelAdmin(admin.ModelAdmin):
    """Admin interface for MonitoredChannel model."""
    
    list_display = [
        'user',
        'channel_name',
        'platform',
        'fetch_frequency',
        'status_badge',
        'is_active',
        'message_count',
        'health_score_display',
        'last_fetched_at',
        'created_at'
    ]
    list_filter = [
        'is_active',
        'fetch_frequency',
        'created_at',
        'channel__connection__platform'
    ]
    search_fields = [
        'user__email',
        'channel__channel_name',
        'channel__channel_id'
    ]
    readonly_fields = [
        'id',
        'status',
        'monitoring_duration',
        'next_fetch_time',
        'health_score',
        'message_count',
        'fetch_success_count',
        'fetch_failure_count',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Monitoring Configuration', {
            'fields': (
                'id',
                'user',
                'channel',
                'is_active',
                'fetch_frequency'
            )
        }),
        ('Monitoring Period', {
            'fields': (
                'monitoring_start_date',
                'monitoring_end_date',
                'monitoring_duration'
            )
        }),
        ('Status & Health', {
            'fields': (
                'status',
                'health_score',
                'last_fetched_at',
                'next_fetch_time'
            )
        }),
        ('Statistics', {
            'fields': (
                'message_count',
                'fetch_success_count',
                'fetch_failure_count'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def channel_name(self, obj):
        """Display channel name."""
        return obj.channel.channel_name
    channel_name.short_description = 'Channel'
    channel_name.admin_order_field = 'channel__channel_name'
    
    def platform(self, obj):
        """Display platform."""
        return obj.channel.connection.get_platform_display()
    platform.short_description = 'Platform'
    platform.admin_order_field = 'channel__connection__platform'
    
    def status_badge(self, obj):
        """Display status with color badge."""
        status = obj.status
        colors = {
            'active': 'green',
            'paused': 'orange',
            'stale': 'red',
            'ended': 'gray'
        }
        color = colors.get(status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            color,
            status.upper()
        )
    status_badge.short_description = 'Status'
    
    def health_score_display(self, obj):
        """Display health score with color."""
        score = obj.health_score
        if score >= 0.8:
            color = 'green'
        elif score >= 0.6:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.0%}</span>',
            color,
            score
        )
    health_score_display.short_description = 'Health'
    health_score_display.admin_order_field = 'fetch_success_count'
    
    actions = ['activate_monitoring', 'deactivate_monitoring']
    
    def activate_monitoring(self, request, queryset):
        """Activate selected monitoring configurations."""
        count = 0
        for obj in queryset:
            obj.activate()
            count += 1
        self.message_user(request, f'{count} monitoring configuration(s) activated.')
    activate_monitoring.short_description = 'Activate selected monitoring'
    
    def deactivate_monitoring(self, request, queryset):
        """Deactivate selected monitoring configurations."""
        count = 0
        for obj in queryset:
            obj.deactivate()
            count += 1
        self.message_user(request, f'{count} monitoring configuration(s) deactivated.')
    deactivate_monitoring.short_description = 'Deactivate selected monitoring'


@admin.register(MonitoringSchedule)
class MonitoringScheduleAdmin(admin.ModelAdmin):
    """Admin interface for MonitoringSchedule model."""
    
    list_display = [
        'monitored_channel_display',
        'schedule_type',
        'is_active',
        'cron_expression',
        'next_run_at',
        'last_run_at',
        'run_count',
        'success_rate_display',
        'created_at'
    ]
    list_filter = [
        'schedule_type',
        'is_active',
        'created_at'
    ]
    search_fields = [
        'monitored_channel__user__email',
        'monitored_channel__channel__channel_name',
        'cron_expression'
    ]
    readonly_fields = [
        'id',
        'success_rate',
        'time_until_next_run',
        'run_count',
        'failure_count',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Schedule Configuration', {
            'fields': (
                'id',
                'monitored_channel',
                'schedule_type',
                'cron_expression',
                'is_active'
            )
        }),
        ('Execution Tracking', {
            'fields': (
                'last_run_at',
                'next_run_at',
                'time_until_next_run',
                'run_count',
                'failure_count',
                'success_rate'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def monitored_channel_display(self, obj):
        """Display monitored channel info."""
        return f"{obj.monitored_channel.user.email} - {obj.monitored_channel.channel.channel_name}"
    monitored_channel_display.short_description = 'Monitored Channel'
    monitored_channel_display.admin_order_field = 'monitored_channel__channel__channel_name'
    
    def success_rate_display(self, obj):
        """Display success rate with color."""
        rate = obj.success_rate
        if rate >= 0.9:
            color = 'green'
        elif rate >= 0.7:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.0%}</span>',
            color,
            rate
        )
    success_rate_display.short_description = 'Success Rate'
    success_rate_display.admin_order_field = 'failure_count'
    
    actions = ['activate_schedules', 'deactivate_schedules']
    
    def activate_schedules(self, request, queryset):
        """Activate selected schedules."""
        count = 0
        for obj in queryset:
            obj.activate()
            count += 1
        self.message_user(request, f'{count} schedule(s) activated.')
    activate_schedules.short_description = 'Activate selected schedules'
    
    def deactivate_schedules(self, request, queryset):
        """Deactivate selected schedules."""
        count = 0
        for obj in queryset:
            obj.deactivate()
            count += 1
        self.message_user(request, f'{count} schedule(s) deactivated.')
    deactivate_schedules.short_description = 'Deactivate selected schedules'
    
    def has_add_permission(self, request):
        """Disable manual creation through admin."""
        return False


# Made with Bob
