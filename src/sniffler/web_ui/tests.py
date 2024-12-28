import json
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

from .models import ScanResult


class HomePageViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_homepage_status_code(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_homepage_accessibility(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_homepage_template_used(self):
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "web_ui/home.html")


class ScanViewTests(TestCase):
    fixtures = ["scan_results.json"]

    def setUp(self):
        self.client = Client()

    @patch("sniffler.web_ui.views.run_scan")
    def test_scan_form_valid(self, mock_run_scan):
        mock_run_scan.return_value = [
            {"size": "1234", "name": "file1.txt", "path": "/files/file1.txt"},
            {"size": "5678", "name": "file2.log", "path": "/files/file2.log"},
        ]
        data = {"path": "/valid/path"}
        response = self.client.post(reverse("scan"), data)
        self.assertRedirects(response, reverse("scan"))
        self.assertTrue(ScanResult.objects.filter(path="/valid/path").exists())

    def test_scan_form_invalid_path(self):
        data = {"path": "/invalid/path"}
        response = self.client.post(reverse("scan"), data)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Path not found." in message.message for message in messages))

    def test_scan_form_missing_path(self):
        data = {}
        response = self.client.post(reverse("scan"), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")

    @patch("sniffler.web_ui.views.run_scan")
    def test_scan_form_run_scan_exception(self, mock_run_scan):
        mock_run_scan.side_effect = Exception("Scan failed")
        data = {"path": "/path/that/causes/exception"}
        response = self.client.post(reverse("scan"), data)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("An error occurred during scanning." in message.message for message in messages))

    def test_set_active_scan(self):
        scan = ScanResult.objects.create(path="/test/path", result=json.dumps({}))
        data = {"scan_id": scan.id}
        response = self.client.post(reverse("scan"), data)
        self.assertRedirects(response, reverse("scan"))
        self.assertEqual(self.client.session["active_scan_id"], str(scan.id))

    def test_set_active_scan_invalid_id(self):
        data = {"scan_id": 9999}
        response = self.client.post(reverse("scan"), data)
        self.assertRedirects(response, reverse("scan"))
        self.assertNotIn("active_scan_id", self.client.session)

    def test_remove_scan(self):
        scan = ScanResult.objects.create(path="/remove/path", result=json.dumps({}))
        data = {"remove_scan_id": scan.id}
        response = self.client.post(reverse("scan"), data)
        self.assertRedirects(response, reverse("scan"))
        self.assertFalse(ScanResult.objects.filter(id=scan.id).exists())

    def test_remove_scan_nonexistent_id(self):
        data = {"remove_scan_id": 9999}
        response = self.client.post(reverse("scan"), data)
        self.assertRedirects(response, reverse("scan"))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Scan removed successfully." in message.message for message in messages))


class StatsViewTests(TestCase):
    fixtures = ["scan_results.json"]

    def setUp(self):
        self.client = Client()

    def test_stats_view_with_active_scan(self):
        scan = ScanResult.objects.create(
            path="/stats/path",
            result=json.dumps(
                [{"size": "1234", "path": "/files/file1.txt"}, {"size": "5678", "path": "/files/file2.log"}]
            ),
        )
        session = self.client.session
        session["active_scan_id"] = scan.id
        session.save()
        response = self.client.get(reverse("stats"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_size", response.context)

    def test_stats_view_no_active_scan(self):
        response = self.client.get(reverse("stats"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No active scan. Please run a new scan, or select one from Scans.")

    def test_stats_view_invalid_scan_data(self):
        scan = ScanResult.objects.create(path="/invalid/data/path", result="invalid_json")
        session = self.client.session
        session["active_scan_id"] = scan.id
        session.save()
        response = self.client.get(reverse("stats"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid scan data encountered.")


class ScanViewTemplateTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_scan_view_template_used(self):
        response = self.client.get(reverse("scan"))
        self.assertTemplateUsed(response, "web_ui/scan.html")


class StatsViewTemplateTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_stats_view_template_used(self):
        response = self.client.get(reverse("stats"))
        self.assertTemplateUsed(response, "web_ui/stats.html")
