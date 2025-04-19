from django.db import connection
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django_tenants.utils import get_tenant_domain_model, schema_context
from django.contrib.auth.models import User, Group
from django.urls import reverse
from esports.models import Organization, Org_League


class LeagueViewTests(TenantTestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a tenant for testing with the schema name 'gse'
        cls.tenant = Organization.objects.create(
            name='Garden State Esports',
            schema_name='gse',  # Required field for schema routing
        )

        # Create a domain associated with the tenant
        Domain = get_tenant_domain_model()
        cls.domain = Domain.objects.create(
            domain='gse.esportsforedu.com',
            tenant=cls.tenant,
            is_primary=True
        )

    def setUp(self):
        # Use the TenantClient to make requests in the tenant context
        self.client = TenantClient(self.tenant)
        self.domain_url = self.domain.domain  # Used as HTTP_HOST in test requests

        # Create an Org_League within the active tenant schema
        Org_League.objects.create(
            org_name='Garden State Esports',
            org_schema='gse',
            org_email='test@gse.com'
        )

        # Create a user and assign them to the 'Site Manager' group
        self.user = User.objects.create_user(username='testuser', password='12345')
        group = Group.objects.create(name='Site Manager')
        self.user.groups.add(group)

        # Log in the user using the tenant-aware client
        self.client.force_login(self.user)

    def test_login_view(self):
        # Test that the login view loads and uses the expected template
        response = self.client.get(reverse('login'), HTTP_HOST=self.domain_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'esports/login.html')

    def test_index_view_defaults_to_gse(self):
        response = self.client.get(reverse('index'), HTTP_HOST=self.domain_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('org', response.context)
        self.assertEqual(response.context['org'].org_schema, 'gse')

        # Check that the "Team Login" button is visible for authenticated users
        self.assertContains(response, 'Team Login')

        # Check that the "Login" button is NOT visible for authenticated users
        self.assertNotContains(response, '>Login<')

        # Check that the "Dashboard" button is visible for admins
        self.assertContains(response, 'Dashboard')

    def test_index_view_anonymous_user(self):
        self.client.logout()  # Ensure no user is logged in
        response = self.client.get(reverse('index'), HTTP_HOST=self.domain_url)
        self.assertEqual(response.status_code, 200)

        # Should show login button
        self.assertContains(response, '>Login<')

        # Should not show dashboard or team login buttons
        self.assertNotContains(response, 'Team Login')
        self.assertNotContains(response, 'Dashboard')


    def test_privacy_policy_view_fallback(self):
        # Test that the privacy policy page loads and pulls correct org data
        response = self.client.get(reverse('privacy_policy'), HTTP_HOST=self.domain_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('org', response.context)
        self.assertEqual(response.context['org'].org_schema, 'gse')

    def test_ticker_view_renders(self):
        # Test that the ticker page loads and uses the correct template
        response = self.client.get(reverse('ticker'), HTTP_HOST=self.domain_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'esports/ticker.html')
