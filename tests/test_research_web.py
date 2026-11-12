import io
import json
import unittest
from unittest.mock import patch

import research_web


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class ResearchTests(unittest.TestCase):
    def test_search_is_bounded_and_returns_attributed_leads(self):
        payload = {'query': {'search': [{'title': 'Task manager', 'snippet': '<b>example</b>',
                                         'timestamp': '2026-01-01T00:00:00Z'}]}}
        with patch('research_web.urllib.request.build_opener') as build:
            build.return_value.open.return_value = FakeResponse(json.dumps(payload).encode())
            result = research_web.discover('task management')
            self.assertEqual(result['results'][0]['snippet'], 'example')
            self.assertEqual(result['results'][0]['url'], 'https://en.wikipedia.org/wiki/Task_manager')
            self.assertIn('not verified', result['limitation'])
            self.assertIn('en.wikipedia.org/w/api.php', build.return_value.open.call_args.args[0].full_url)
            self.assertEqual(build.return_value.open.call_args.kwargs['timeout'], 15)

    def test_reference_inspection_extracts_static_controls(self):
        with patch('research_web.urllib.request.build_opener') as build:
            build.return_value.open.return_value = FakeResponse(b'<button aria-label="Add">+</button><script>secret</script>')
            result = research_web.inspect_references(['https://www.calculator.net/'])
            self.assertIn('Add', result[0]['text'])
            self.assertNotIn('secret', result[0]['text'])
            self.assertIn('Static HTML only', result[0]['limitation'])

    def test_reference_rejects_unapproved_host(self):
        with self.assertRaises(ValueError):
            research_web.inspect_references(['https://127.0.0.1/'])

    def test_rejects_large_query_without_network(self):
        with patch('research_web.urllib.request.build_opener') as build:
            with self.assertRaises(ValueError):
                research_web.discover('x' * 201)
            build.assert_not_called()

    def test_rejects_large_response(self):
        with patch('research_web.urllib.request.build_opener') as build:
            build.return_value.open.return_value = FakeResponse(b'x' * (research_web.MAX_BYTES + 1))
            with self.assertRaises(ValueError):
                research_web.discover('test')


if __name__ == '__main__':
    unittest.main()
