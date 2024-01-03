from django.db import models
from django.conf import settings
from apps.utils.models import validate_timezone
from django.utils.timezone import now, timezone
from datetime import timedelta

class UserDevice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='devices')
    device_fingerprint = models.CharField(max_length=128, blank=False, primary_key=True)

    device_model = models.CharField(max_length=100)
    device_brand = models.CharField(max_length=100)
    
    os_name = models.CharField(max_length=100)
    os_version = models.CharField(max_length=50)
    
    screen_width = models.IntegerField()
    screen_height = models.IntegerField()
    
    locales = models.JSONField(default=list)
    currencies = models.JSONField(default=list)
    
    font_scale = models.FloatField()
    accesibility_settings = models.JSONField(default=dict)

    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(default=now, editable=False)

    def __str__(self):
        return f"{self.device_brand} {self.device_model} - {self.os_name} {self.os_version}"

class DeviceSession(models.Model):
    user_device = models.ForeignKey('UserDevice', on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    session_start = models.DateTimeField(auto_now_add=True)
    session_end = models.DateTimeField(null=True, blank=True)
    timezone = models.CharField(max_length=100, validators=[validate_timezone])
    
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(default=now, editable=False)

    deleted_at = models.DateTimeField(null=True, blank=True)  # For soft deletion

    @classmethod
    def start_session(cls, user_device, ip, timezone_str):
        new_session = cls(
            user_device=user_device,
            session_start=now(),
            ip=ip,
            timezone=timezone_str,
        )
        new_session.save()
        return new_session
    
    def end_session(self):
        # This method can be called when ending a session due to inactivity or user action.
        self.session_end = now()
        self.save() 
    
    def session_duration(self):
        if self.is_active():
            return now() - self.session_start
        elif self.session_end is not None:
            return self.session_end - self.session_start
        return timedelta(0)
    
    def is_active(self):
        return self.session_end is None and self.deleted_at is None
    
    def soft_delete(self):
        self.deleted_at = now()
        self.save()

    def save(self, *args, **kwargs):
        self.full_clean()  # Ensure the model is validated before saving
        super(DeviceSession, self).save(*args, **kwargs)
        
    def __str__(self):
        return f"Session on {self.user_device} from IP {self.ip}"