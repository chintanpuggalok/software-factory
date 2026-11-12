"""Limited, deterministic checks for a generated static HTML prototype."""
from html.parser import HTMLParser
import hashlib
import re

MAX_CHARS = 500000


class Inspector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = set()
        self.errors = []

    def handle_starttag(self, tag, attrs):
        self.tags.add(tag)
        values = dict(attrs)
        if tag in ('script', 'img', 'audio', 'video', 'source', 'embed', 'object') and values.get('src'):
            self.errors.append('External resource sources are not allowed')
        if tag == 'iframe':
            self.errors.append('Embedded frames are not allowed')
        if tag == 'link' and values.get('href'):
            self.errors.append('External linked resources are not allowed')


def check_document(document):
    """Return structural findings; a clean result is not a security audit."""
    findings = []
    if not isinstance(document, str) or not document.strip():
        return ['Document is empty']
    if len(document) > MAX_CHARS:
        return ['Document exceeds size limit']
    if document.lstrip().startswith('```'):
        findings.append('Return raw HTML, not Markdown')
    parser = Inspector()
    try:
        parser.feed(document)
        parser.close()
    except (ValueError, AssertionError):
        return ['HTML could not be parsed']
    for tag in ('html', 'head', 'body', 'title'):
        if tag not in parser.tags:
            findings.append(f'Missing {tag} element')
    if '</html>' not in document.lower():
        findings.append('Missing closing html element')
    findings.extend(parser.errors)
    if re.search(r'\b(?:fetch|XMLHttpRequest|WebSocket|EventSource)\s*\(', document, re.IGNORECASE):
        findings.append('Network API usage is not allowed')
    if re.search(r'@import\b|\burl\s*\(', document, re.IGNORECASE):
        findings.append('CSS resource references are not allowed')
    return findings


def report(document):
    findings = check_document(document)
    return {'sha256': hashlib.sha256(document.encode('utf-8')).hexdigest(),
            'status': 'failed' if findings else 'passed', 'findings': findings,
            'scope': 'basic static checks only; not a security audit or functional verification',
            'browser_verified': False}
