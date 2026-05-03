import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class MonitoredChannel(models.Model):
    """
    Represents a channel that a user has chosen to monitor.
    Links users to specific channels from their platform connections
    and manages monitoring configuration.
    """
    
    FREQUENCY_CHOICES = [
        ('HOURLY', 'Hourly'),
        ('EVERY_6_HOURS', 'Every 6 Hours'),
        ('DAILY', 'Daily'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('stale', 'Stale'),
        ('ended', 'Ended'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='monitored_channels',
        help_text=_('User who owns this monitoring configuration')
    )
    channel = models.ForeignKey(
        'integrations.Channel',
        on_delete=models.CASCADE,
        related_name='monitoring_configs',
        help_text=_('Channel being monitored')
    )
    
    # Monitoring configuration
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_('Whether monitoring is currently active')
    )
    fetch_frequency = models.CharField(
        _('fetch frequency'),
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='HOURLY',
        help_text=_('How often to fetch messages from this channel')
    )
    
    # Monitoring period
    monitoring_start_date = models.DateField(
        _('monitoring start date'),
        auto_now_add=True,
        help_text=_('Date when monitoring started')
    )
    monitoring_end_date = models.DateField(
        _('monitoring end date'),
        null=True,
        blank=True,
        help_text=_('Date when monitoring should end (optional)')
    )
    
    # Tracking fields
    last_fetched_at = models.DateTimeField(
        _('last fetched at'),
        null=True,
        blank=True,
        help_text=_('Timestamp of last successful message fetch')
    )
    message_count = models.IntegerField(
        _('message count'),
        default=0,
        help_text=_('Total number of messages fetched (denormalized)')
    )
    fetch_success_count = models.IntegerField(
        _('fetch success count'),
        default=0,
        help_text=_('Number of successful fetches')
    )
    fetch_failure_count = models.IntegerField(
        _('fetch failure count'),
        default=0,
        help_text=_('Number of failed fetches')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'monitored_channels'
        verbose_name = _('Monitored Channel')
        verbose_name_plural = _('Monitored Channels')
        unique_together = [['user', 'channel']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['is_active']),
            models.Index(fields=['last_fetched_at']),
            models.Index(fields=['fetch_frequency']),
        ]
    
    def __str__(self):
        return f"{self.user.email} monitoring {self.channel.channel_name}"
    
    @property
    def status(self):
        """
        Calculate current monitoring status.
        Returns: 'active', 'paused', 'stale', or 'ended'
        """
        # Check if monitoring has ended
        if self.monitoring_end_date and timezone.now().date() > self.monitoring_end_date:
            return 'ended'
        
        # Check if paused
        if not self.is_active:
            return 'paused'
        
        # Check if stale (no fetch in 2x the frequency)
        if self.last_fetched_at:
            expected_interval = self._get_frequency_timedelta() * 2
            if timezone.now() - self.last_fetched_at > expected_interval:
                return 'stale'
        
        return 'active'
    
    @property
    def monitoring_duration(self):
        """Calculate how long this channel has been monitored."""
        end_date = self.monitoring_end_date or timezone.now().date()
        return end_date - self.monitoring_start_date
    
    @property
    def next_fetch_time(self):
        """Calculate when the next fetch should occur."""
        if not self.is_active or not self.last_fetched_at:
            return None
        
        interval = self._get_frequency_timedelta()
        return self.last_fetched_at + interval
    
    @property
    def health_score(self):
        """
        Calculate health score based on fetch success rate.
        Returns: Float between 0.0 and 1.0
        """
        total_fetches = self.fetch_success_count + self.fetch_failure_count
        if total_fetches == 0:
            return 1.0  # No fetches yet, assume healthy
        
        success_rate = self.fetch_success_count / total_fetches
        
        # Penalize if stale
        if self.status == 'stale':
            success_rate *= 0.5
        
        return round(success_rate, 2)
    
    def _get_frequency_timedelta(self):
        """Convert fetch frequency to timedelta."""
        frequency_map = {
            'HOURLY': timedelta(hours=1),
            'EVERY_6_HOURS': timedelta(hours=6),
            'DAILY': timedelta(days=1),
        }
        return frequency_map.get(self.fetch_frequency, timedelta(hours=1))
    
    def should_fetch_now(self):
        """
        Check if a fetch should be triggered now.
        Returns: Boolean
        """
        if not self.is_active:
            return False
        
        if self.status == 'ended':
            return False
        
        if not self.last_fetched_at:
            return True  # Never fetched, should fetch now
        
        return timezone.now() >= self.next_fetch_time
    
    def calculate_next_fetch_time(self):
        """
        Calculate the next fetch time based on frequency.
        Returns: datetime or None
        """
        if not self.is_active:
            return None
        
        base_time = self.last_fetched_at or timezone.now()
        interval = self._get_frequency_timedelta()
        return base_time + interval
    
    def activate(self):
        """Activate monitoring and clear any stale status."""
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])
    
    def deactivate(self):
        """Deactivate monitoring (pause)."""
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])
    
    def mark_fetch_success(self, message_count=0):
        """Mark a successful fetch and update statistics."""
        self.last_fetched_at = timezone.now()
        self.fetch_success_count += 1
        self.message_count += message_count
        self.save(update_fields=[
            'last_fetched_at',
            'fetch_success_count',
            'message_count',
            'updated_at'
        ])
    
    def mark_fetch_failure(self):
        """Mark a failed fetch attempt."""
        self.fetch_failure_count += 1
        self.save(update_fields=['fetch_failure_count', 'updated_at'])
    
    def end_monitoring(self, end_date=None):
        """End monitoring by setting end date."""
        self.monitoring_end_date = end_date or timezone.now().date()
        self.is_active = False
        self.save(update_fields=['monitoring_end_date', 'is_active', 'updated_at'])


class MonitoringSchedule(models.Model):
    """
    Manages the scheduling of fetch and summarize tasks for monitored channels.
    Uses cron expressions for flexible scheduling.
    """
    
    SCHEDULE_TYPE_CHOICES = [
        ('FETCH', 'Fetch Messages'),
        ('SUMMARIZE', 'Generate Summary'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    monitored_channel = models.ForeignKey(
        MonitoredChannel,
        on_delete=models.CASCADE,
        related_name='schedules',
        help_text=_('Monitored channel this schedule belongs to')
    )
    
    # Schedule configuration
    schedule_type = models.CharField(
        _('schedule type'),
        max_length=20,
        choices=SCHEDULE_TYPE_CHOICES,
        help_text=_('Type of task to schedule')
    )
    cron_expression = models.CharField(
        _('cron expression'),
        max_length=100,
        help_text=_('Cron expression for scheduling (e.g., "0 * * * *" for hourly)')
    )
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_('Whether this schedule is currently active')
    )
    
    # Execution tracking
    last_run_at = models.DateTimeField(
        _('last run at'),
        null=True,
        blank=True,
        help_text=_('When this schedule last executed')
    )
    next_run_at = models.DateTimeField(
        _('next run at'),
        help_text=_('When this schedule should run next')
    )
    run_count = models.IntegerField(
        _('run count'),
        default=0,
        help_text=_('Total number of times this schedule has run')
    )
    failure_count = models.IntegerField(
        _('failure count'),
        default=0,
        help_text=_('Number of failed executions')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'monitoring_schedules'
        verbose_name = _('Monitoring Schedule')
        verbose_name_plural = _('Monitoring Schedules')
        ordering = ['next_run_at']
        indexes = [
            models.Index(fields=['next_run_at', 'is_active']),
            models.Index(fields=['schedule_type']),
            models.Index(fields=['monitored_channel', 'schedule_type']),
        ]
    
    def __str__(self):
        return f"{self.get_schedule_type_display()} for {self.monitored_channel}"
    
    @property
    def success_rate(self):
        """
        Calculate success rate for this schedule.
        Returns: Float between 0.0 and 1.0
        """
        if self.run_count == 0:
            return 1.0  # No runs yet, assume healthy
        
        success_count = self.run_count - self.failure_count
        return round(success_count / self.run_count, 2)
    
    @property
    def time_until_next_run(self):
        """Calculate time remaining until next run."""
        if not self.next_run_at:
            return None
        
        delta = self.next_run_at - timezone.now()
        return delta if delta.total_seconds() > 0 else timedelta(0)
    
    def is_due(self):
        """
        Check if this schedule is due to run.
        Returns: Boolean
        """
        if not self.is_active:
            return False
        
        if not self.next_run_at:
            return False
        
        return timezone.now() >= self.next_run_at
    
    def calculate_next_run(self, from_time=None):
        """
        Calculate next run time from cron expression.
        Returns: datetime
        """
        from croniter import croniter
        
        base_time = from_time or timezone.now()
        cron = croniter(self.cron_expression, base_time)
        return cron.get_next(datetime)
    
    def mark_run_complete(self, success=True):
        """Mark a schedule run as complete and calculate next run time."""
        from datetime import datetime
        
        self.last_run_at = timezone.now()
        self.run_count += 1
        
        if not success:
            self.failure_count += 1
        
        # Calculate next run time
        try:
            self.next_run_at = self.calculate_next_run()
        except Exception:
            # If cron calculation fails, use frequency-based calculation
            if self.schedule_type == 'FETCH':
                interval = self.monitored_channel._get_frequency_timedelta()
                self.next_run_at = timezone.now() + interval
            else:
                # Default to daily for summarize
                self.next_run_at = timezone.now() + timedelta(days=1)
        
        self.save(update_fields=[
            'last_run_at',
            'next_run_at',
            'run_count',
            'failure_count',
            'updated_at'
        ])
    
    def mark_run_failed(self):
        """Mark a schedule run as failed."""
        self.mark_run_complete(success=False)
    
    def activate(self):
        """Activate this schedule."""
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])
    
    def deactivate(self):
        """Deactivate this schedule."""
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])


# Made with Bob
