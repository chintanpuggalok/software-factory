"""Optional isolated browser checks. Not a functional or security audit."""
import glob
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def find_chromium():
    configured = os.environ.get('CHROME_BIN')
    if configured:
        return configured if Path(configured).is_file() else None
    for name in ('chromium', 'chromium-browser', 'google-chrome'):
        found = shutil.which(name)
        if found:
            return found
    candidates = sorted(glob.glob(str(Path.home() / '.cache/ms-playwright/chromium-*/chrome-linux64/chrome')))
    return candidates[-1] if candidates else None


def validate_acceptance(contract):
    if not isinstance(contract, dict) or contract.get('version') != 1 or not isinstance(contract.get('actions'), list):
        raise ValueError('Invalid acceptance contract')
    actions = contract['actions']
    if not actions or len(actions) > 50:
        raise ValueError('Acceptance contract must have 1 to 50 actions')
    required = {'click': ('selector',), 'key': ('key',), 'expect_text': ('selector', 'text'),
                'expect_exists': ('selector',), 'reset': ()}
    if not any(isinstance(x, dict) and x.get('action') in ('expect_text', 'expect_exists') for x in actions):
        raise ValueError('Acceptance contract needs at least one assertion')
    for action in actions:
        if not isinstance(action, dict) or action.get('action') not in required:
            raise ValueError('Invalid acceptance action')
        names = required[action['action']]
        if set(action) != {'action', *names}:
            raise ValueError('Unexpected acceptance fields')
        for name in names:
            if not isinstance(action[name], str) or len(action[name]) > 300:
                raise ValueError('Invalid acceptance value')
            if name != 'text' and not action[name]:
                raise ValueError('Empty acceptance value')
    return contract


def probe(path, *, timeout=30, acceptance=None):
    if acceptance is not None:
        validate_acceptance(acceptance)
    path = Path(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    node = shutil.which('node')
    bubblewrap = shutil.which('bwrap')
    chromium = find_chromium()
    if not node or not bubblewrap or not chromium:
        return {'status': 'unavailable', 'sha256': digest,
                'reason': 'Node, Bubblewrap, or Chromium is unavailable'}
    try:
        command = [node, str(ROOT / 'browser_probe.mjs'), str(path.resolve()), chromium]
        if acceptance is not None:
            command.append('--acceptance')
        result = subprocess.run(command, input=json.dumps(acceptance) if acceptance is not None else None,
                                capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return {'status': 'failed', 'sha256': digest, 'reason': 'Browser check timed out'}
    if result.returncode != 0:
        return {'status': 'unavailable', 'sha256': digest,
                'reason': 'Browser sandbox could not complete: ' + result.stderr[-600:]}
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {'status': 'unavailable', 'sha256': digest, 'reason': 'Invalid browser probe output'}
    if not isinstance(data, dict) or data.get('status') not in ('passed', 'failed'):
        return {'status': 'unavailable', 'sha256': digest, 'reason': 'Invalid browser probe status'}
    data['sha256'] = digest
    return data
