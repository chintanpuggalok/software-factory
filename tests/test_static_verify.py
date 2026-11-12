import unittest

from static_verify import check_document, report


class StaticVerifyTests(unittest.TestCase):
    def test_valid_document_is_structurally_checked_not_certified(self):
        document = '<html><head><title>x</title></head><body>y</body></html>'
        result = report(document)
        self.assertEqual(result['status'], 'passed')
        self.assertFalse(result['browser_verified'])
        self.assertIn('not a security audit', result['scope'])

    def test_external_resources_and_network_apis_fail(self):
        document = '<html><head><title>x</title><script src="https://example.com/x.js"></script></head><body><script>fetch("/api")</script></body></html>'
        findings = check_document(document)
        self.assertTrue(any('resource' in item for item in findings))
        self.assertTrue(any('Network API' in item for item in findings))

    def test_missing_structure_fails(self):
        self.assertTrue(check_document('<html>missing tags</html>'))


if __name__ == '__main__':
    unittest.main()
