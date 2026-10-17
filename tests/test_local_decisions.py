import importlib.util
import pathlib
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / 'skills/kakaotalk-review-local/scripts/classify.py'
spec = importlib.util.spec_from_file_location('decisions', SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class DecisionsTest(unittest.TestCase):
    def test_remote_endpoint_rejected(self):
        for url in ['https://example.com', 'http://localhost.evil:11435', 'http://user:pass@localhost:11435', 'http://127.0.0.1:11435/redirect']:
            with self.assertRaises(ValueError): m.validate_endpoint(url)
        self.assertEqual(m.validate_endpoint('http://127.0.0.1:11435'), 'http://127.0.0.1:11435')

    def test_truncation_and_invalid_answers_go_to_review(self):
        for reply in [{'state_truncated': True}, {}, {'answers':{'relevance':{'choice':'social'}}}]:
            out = m.interpret(reply)
            self.assertTrue(out['requires_review'])
            self.assertIsNone(out['relevance'])

    def test_non_object_answer_goes_to_review(self):
        for reply in [{'state_truncated':False,'answers':{'relevance':None}},
                      {'state_truncated':False,'answers':[]}, {'state_truncated':False,'answers':{'relevance':{'choice':[]}}}, None]:
            self.assertIsNone(m.interpret(reply)['relevance'])

    def test_existing_output_is_not_overwritten(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / 'run.json'
            m.write_private(path, {'private':'first'})
            with self.assertRaises(FileExistsError): m.write_private(path, {'private':'second'})
            self.assertIn('first',path.read_text())

    def test_high_probability_never_discards_message(self):
        reply = {'model':'laya:multilingual','state_truncated':False, 'answers':{
            'relevance':{'choice':'social','probabilities':{'relevant':0.001,'social':0.999,'unclear':0}},
            'intent':{'choice':'other','probabilities':{'request':0,'question':0,'plan':0,'completed':0,'cancelled':0,'information':0,'other':1}}}}
        out = m.interpret(reply)
        self.assertEqual(out['relevance'], 'social')
        self.assertTrue(out['requires_review'])
        self.assertTrue(out['retain'])

    def test_invalid_probability_is_not_trusted(self):
        reply = {'state_truncated':False,'answers':{'relevance':{'choice':'relevant','probabilities':{'relevant':float('nan')}}}}
        self.assertIsNone(m.interpret(reply)['relevance'])

    def test_unique_ids_required_without_deduping_text(self):
        rows=[{'id':'a','text':'네'},{'id':'b','text':'네'}]
        self.assertEqual(len(m.validate_rows(rows)),2)
        with self.assertRaises(ValueError): m.validate_rows([rows[0],rows[0]])

    def test_multiline_context_is_untrusted_data_and_bounded(self):
        state=m.make_state([{'id':'a','text':'앞 대화'*400},{'id':'b','text':'취소해주세요'}],1)
        self.assertEqual(state['target']['text'],'취소해주세요')
        self.assertLessEqual(len(state['previous'][0]['text']),m.CONTEXT_CHARS)
        self.assertTrue(state['context_clipped'])

if __name__ == '__main__': unittest.main()
