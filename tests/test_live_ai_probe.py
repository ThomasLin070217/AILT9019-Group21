"""Evidence capture checks: offline only, never access a live credential."""
import asyncio
import base64
import json

import httpx

from backend.config import Settings
from scripts.live_ai_probe import AuditTransport, request_summary
from conftest import jpeg_bytes


def test_summary_excludes_image_bytes_and_measures_prepared_photos():
    blob = jpeg_bytes(size=(100, 100))
    encoded = base64.b64encode(blob).decode()
    summary = request_summary({'model': 'test', 'temperature': 0.2, 'max_tokens': 600,
        'messages': [{'role': 'system', 'content': 'private system text'},
                     {'role': 'user', 'content': [{'type': 'text', 'text': 'Osaka'},
                      {'type': 'image_url', 'image_url': {'url': 'data:image/jpeg;base64,' + encoded}}]}]})
    assert summary['images'][0]['exif_entries'] == 0
    assert summary['images'][0]['width'] == 100
    assert encoded not in json.dumps(summary)
    assert 'private system text' not in json.dumps(summary)


def test_capture_preserves_content_and_usage_but_excludes_headers_and_reasoning():
    async def check():
        record = {}
        transport = AuditTransport(Settings(), record)
        await transport.client.aclose()
        text = '{"status":"clarification"}'
        body = {'model': 'test', 'choices': [{'finish_reason': 'stop', 'message': {
            'role': 'assistant', 'content': text, 'reasoning_content': 'not-for-evidence'}}],
            'usage': {'total_tokens': 10}, 'id': 'omit-provider-id'}
        def handler(req):
            assert req.headers['authorization'] == 'Bearer test-secret'
            return httpx.Response(200, json=body, headers={'x-secret': 'never-record'})
        transport.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        payload = {'model': 'test', 'temperature': 0.2, 'max_tokens': 600,
            'messages': [{}, {'content': [{'type': 'text', 'text': 'fictional notes'}]}]}
        req = httpx.Request('POST', 'https://example.com/v1/chat/completions', json=payload,
                            headers={'Authorization': 'Bearer test-secret'})
        response = await transport.handle_async_request(req)
        assert response.json() == body
        assert record['provider_response']['choices'][0]['message']['content'] == text
        assert record['provider_response']['usage']['total_tokens'] == 10
        for excluded in ('test-secret', 'never-record', 'not-for-evidence', 'omit-provider-id'):
            assert excluded not in json.dumps(record)
        await transport.aclose()
    asyncio.run(check())
