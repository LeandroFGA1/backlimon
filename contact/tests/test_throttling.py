import time
from unittest.mock import patch
from django.test import RequestFactory, TestCase
from django.core.cache import cache
from contact.throttling import ContactMessageRateThrottle


class ContactMessageRateThrottleTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.throttle = ContactMessageRateThrottle()

    def tearDown(self):
        cache.clear()

    def test_allow_request_within_limit(self):
        request = self.factory.get('/')
        for _ in range(self.throttle.RATE):
            self.assertTrue(self.throttle.allow_request(request, None))

    def test_deny_request_when_limit_exceeded(self):
        request = self.factory.get('/')
        for _ in range(self.throttle.RATE):
            self.throttle.allow_request(request, None)
        self.assertFalse(self.throttle.allow_request(request, None))

    def test_reset_after_duration(self):
        request = self.factory.get('/')
        for _ in range(self.throttle.RATE):
            self.throttle.allow_request(request, None)

        # Simular el paso del tiempo para exceder `DURATION`
        with patch('time.time', return_value=time.time() + self.throttle.DURATION + 1):
            self.assertTrue(self.throttle.allow_request(request, None))

    def test_wait_calculation(self):
        request = self.factory.get('/')
        for _ in range(self.throttle.RATE):
            self.throttle.allow_request(request, None)

        # Simular tiempo justo antes de que la primera solicitud expire
        earliest = self.throttle.history[0]
        with patch('time.time', return_value=earliest + self.throttle.DURATION - 10):
            self.assertAlmostEqual(self.throttle.wait(), 10, delta=1)

    def test_get_ident_from_forwarded_for(self):
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.195, 198.51.100.17'
        ip = self.throttle.get_ident(request)
        self.assertEqual(ip, '203.0.113.195')

    def test_get_ident_from_remote_addr(self):
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        ip = self.throttle.get_ident(request)
        self.assertEqual(ip, '127.0.0.1')
