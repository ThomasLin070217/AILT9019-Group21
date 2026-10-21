import base64
import io
import json
import os
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from PIL import Image

from ai_memory import AIError, build_payload, generate, public_settings, validate_output
import test_album_store as album_fixtures


class AITests(unittest.TestCase):
    def setUp(self):album_fixtures.AlbumTests.setUp(self)
    def tearDown(self):album_fixtures.AlbumTests.tearDown(self)

    def test_request_contains_only_selected_trip_and_sanitized_photos(self):
        trip=self.store.create(self.data);self.data['request_id']='12345678-1234-4234-8234-123456789012';self.data['notes']='OTHER_TRIP_SECRET';self.store.create(self.data)
        payload=build_payload(trip,self.store.cities[trip['city_id']],self.store,'test-vision')
        self.assertNotIn('OTHER_TRIP_SECRET',json.dumps(payload));self.assertNotIn('tools',payload);self.assertIs(payload['store'],False)
        content=payload['input'][0]['content'];self.assertEqual(len(content),2)
        raw=base64.b64decode(content[1]['image_url'].split(',')[1])
        with Image.open(io.BytesIO(raw)) as image:self.assertEqual(dict(image.getexif()),{});self.assertLessEqual(max(image.size),1024)

    def test_config_never_exposes_key_or_inherits_editor_base_url(self):
        with patch.dict(os.environ,{'TRAVEL_AI_API_KEY':'secret-test-only','TRAVEL_AI_MODEL':'vision','OPENAI_BASE_URL':'https://editor.invalid'}):
            config=public_settings(self.temp.name);self.assertTrue(config['configured']);self.assertEqual(config['endpoint'],'https://api.openai.com/v1');self.assertNotIn('secret-test-only',json.dumps(config))

    def test_missing_key_fails_without_touching_album(self):
        trip=self.store.create(self.data)
        with patch.dict(os.environ,{'TRAVEL_AI_API_KEY':'','TRAVEL_AI_MODEL':''}):
            with self.assertRaises(AIError) as error:generate(self.temp.name,self.store,trip)
        self.assertEqual(error.exception.status,503);self.assertEqual(self.store.list(),[trip])

    def test_valid_draft_and_clarification_shape(self):
        draft={'status':'draft','title':'A visit','memory_text':'A factual memory.','warnings':[],'questions':[]}
        self.assertEqual(validate_output(draft),draft)
        clarification={**draft,'status':'clarification','questions':['What happened?']}
        self.assertEqual(validate_output(clarification)['memory_text'],'')
        for invalid in [{}, {**draft,'memory_text':''},{**draft,'warnings':'wrong'},{**draft,'title':'x'*201}]:
            with self.assertRaises(AIError):validate_output(invalid)

    def test_adapter_success_is_unsaved_and_errors_are_sanitized(self):
        trip=self.store.create(self.data);result={'status':'draft','title':'Title','memory_text':'Memory','warnings':[],'questions':[]}
        envelope={'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(result)}]}]}
        with patch.dict(os.environ,{'TRAVEL_AI_API_KEY':'secret-test-only','TRAVEL_AI_MODEL':'vision'}):
            with patch('ai_memory.build_opener') as opener:
                opener.return_value.open.return_value=io.BytesIO(json.dumps(envelope).encode())
                self.assertEqual(generate(self.temp.name,self.store,trip)['status'],'draft')
            for failure,status in [(HTTPError('url',401,'secret-test-only',{},None),503),(HTTPError('url',429,'',{},None),429),(TimeoutError(),504)]:
                with patch('ai_memory.build_opener') as opener:
                    opener.return_value.open.side_effect=failure
                    with self.assertRaises(AIError) as error:generate(self.temp.name,self.store,trip)
                    self.assertEqual(error.exception.status,status);self.assertNotIn('secret-test-only',str(error.exception))
        self.assertEqual(self.store.list(),[trip])

    def test_malformed_and_refused_output_never_saves(self):
        trip=self.store.create(self.data)
        for body in [b'bad json',json.dumps({'output':[{'type':'message','content':[{'type':'refusal','refusal':'No'}]}]}).encode()]:
            with patch.dict(os.environ,{'TRAVEL_AI_API_KEY':'test','TRAVEL_AI_MODEL':'vision'}),patch('ai_memory.build_opener') as opener:
                opener.return_value.open.return_value=io.BytesIO(body)
                with self.assertRaises(AIError):generate(self.temp.name,self.store,trip)
        self.assertEqual(self.store.list(),[trip])

    def test_bailian_gateway_preserves_system_rules_and_limits_reasoning(self):
        trip=self.store.create(self.data)
        result={'status':'draft','title':'Title','memory_text':'Memory','warnings':[],'questions':[]}
        envelope={'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(result)}]}]}
        with patch.dict(os.environ,{'TRAVEL_AI_API_KEY':'fake-unit-key','TRAVEL_AI_MODEL':'qwen3.8-flash','TRAVEL_AI_BASE_URL':'https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1'}),patch('ai_memory.build_opener') as opener:
            opener.return_value.open.return_value=io.BytesIO(json.dumps(envelope).encode())
            generate(self.temp.name,self.store,trip)
            request=opener.return_value.open.call_args.args[0]
            payload=json.loads(request.data)
            self.assertEqual(payload['reasoning'],{'effort':'none'})
            self.assertNotIn('instructions',payload)
            self.assertEqual(payload['input'][0]['role'],'system')
            self.assertIn('completed trips',payload['input'][0]['content'])
            self.assertEqual(payload['input'][1]['role'],'user')
            self.assertEqual(len(payload['input'][1]['content']),2)
            self.assertIs(payload['store'],False)
            self.assertEqual(len(self.store.list()),1)
