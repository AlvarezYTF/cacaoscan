"""
Factory classes for creating test data using factory_boy.

This module provides factories for creating unique test instances,
preventing IntegrityError issues with duplicate usernames and emails.
"""
import factory
from factory import Faker, Sequence
from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User instances with unique usernames and emails."""
    
    class Meta:
        model = User
        django_get_or_create = ('username',)
    
    username = Faker("user_name")
    email = Sequence(lambda n: f"user{n}@example.com")
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    is_active = True
    is_staff = False
    is_superuser = False
    
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """Set password after user creation."""
        if not create:
            return
        password = extracted if extracted else 'testpass123'
        self.set_password(password)
        self.save()


class AdminUserFactory(factory.django.DjangoModelFactory):
    """Factory for creating admin User instances with unique usernames and emails."""
    
    class Meta:
        model = User
        django_get_or_create = ('username',)
    
    username = Faker("user_name")
    email = Sequence(lambda n: f"user{n}@example.com")
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    is_active = True
    is_staff = True
    is_superuser = True
    
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """Set password after user creation."""
        if not create:
            return
        password = extracted if extracted else 'adminpass123'
        self.set_password(password)
        self.save()


class StaffUserFactory(factory.django.DjangoModelFactory):
    """Factory for creating staff User instances with unique usernames and emails."""
    
    class Meta:
        model = User
        django_get_or_create = ('username',)
    
    username = Faker("user_name")
    email = Sequence(lambda n: f"user{n}@example.com")
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    is_active = True
    is_staff = True
    is_superuser = False
    
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """Set password after user creation."""
        if not create:
            return
        password = extracted if extracted else 'staffpass123'
        self.set_password(password)
        self.save()

