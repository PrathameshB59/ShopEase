"""
Quick script to check and add phone numbers to user profiles
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import Profile
from django.contrib.auth.models import User

print("\n" + "="*60)
print("📱 USER PHONE NUMBERS")
print("="*60)

# Get all profiles
profiles = Profile.objects.all()

if not profiles:
    print("❌ No profiles found!")
else:
    print(f"\nTotal profiles: {profiles.count()}\n")

    for profile in profiles:
        phone = profile.phone or "(No phone)"
        print(f"👤 {profile.user.username:20} | 📞 {phone}")

print("\n" + "="*60)
print("💡 TO ADD A PHONE NUMBER:")
print("="*60)
print("""
Option 1 - Django Shell:
    python manage.py shell
    >>> from apps.accounts.models import Profile
    >>> profile = Profile.objects.get(user__username='YOUR_USERNAME')
    >>> profile.phone = '+919372258976'
    >>> profile.save()

Option 2 - Admin Panel:
    1. Go to http://127.0.0.1:8000/admin/
    2. Login with superuser
    3. Click 'Profiles'
    4. Edit your profile
    5. Add phone: +919372258976
    6. Save
""")
print("="*60 + "\n")
