from io import BytesIO
from pathlib import Path
import zipfile
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
from storage import Store
from vendor_core import classify

APP=Path(__file__).resolve().parents[1]/'app.py'


def seed(path):
    store=Store(path)
    for company in ['Alpha Medical','Beta Devices']:
        store.save_document(f'{company}/GST.pdf',company.encode(),classify(f'{company}/GST.pdf'))
    return store


def app(path):
    at=AppTest.from_file(str(APP),default_timeout=40)
    at.secrets['VENDOR_DATA_DIR']=str(path)
    return at


def test_default_search_reset_totals_and_dropdown(tmp_path):
    store=seed(tmp_path)
    at=app(tmp_path).run(); assert not at.exception
    assert at.metric[0].value=='2'
    assert at.get('plotly_chart')
    at.text_input(key='company_search').set_value('Beta').run()
    assert not at.exception and at.metric[0].value=='2' # Global count stays global.
    selector=at.selectbox(key='company_selection')
    assert selector.options==['Beta Devices']
    assert any('Showing 1 of 2 companies' in item.value for item in at.caption)
    at.text_input(key='company_search').set_value('Not found').run()
    assert not at.exception and at.metric[0].value=='2'
    assert not any(x.label=='Select company' for x in at.selectbox)
    at.button(key='reset_filters').click().run()
    assert not at.exception and at.metric[0].value=='0'
    assert len(Store(tmp_path).documents())==2
    at.button(key='show_saved_data').click().run()
    assert not at.exception and at.metric[0].value=='2'


def test_password_gate_and_empty_state(tmp_path):
    at=app(tmp_path)
    at.secrets['APP_PASSWORD']='unit-test-only-not-a-real-secret'
    at.run(); assert not at.exception and not at.metric
    at.text_input[0].set_value('unit-test-only-not-a-real-secret')
    at.button[0].click().run()
    assert not at.exception and at.metric[0].value=='0'


def test_upload_duplicate_export_and_navigation(tmp_path):
    buffer=BytesIO()
    with zipfile.ZipFile(buffer,'w') as z:
        z.writestr('Example vendor/01 - Alpha Medical/GST.txt',b'Synthetic GST test fixture')
        z.writestr('Sample vendor/02 - Beta Devices/PAN Card.txt',b'Synthetic PAN test fixture')
        z.writestr('Example vendor/Alpha Medical/scan001.txt',b'Synthetic unclear fixture')
        z.writestr('Example vendor/03 - Empty Company/',b'')
    class Upload:
        name='synthetic-fixture.zip'
        def getvalue(self):return buffer.getvalue()
    def fake_upload(*args,**kwargs):
        return [Upload()] if kwargs.get('key')=='document_uploads' else None
    at=app(tmp_path)
    with patch('streamlit.file_uploader',side_effect=fake_upload):
        at.run()
        at.radio(key='page').set_value('Upload documents').run()
        at.button(key='save_documents').click().run()
        assert not at.exception
        stored=Store(tmp_path)
        assert len(stored.documents())==3 and len(stored.vendors())==3
        assert len(stored.upload_archives())==1
        assert int(stored.documents().needs_review.sum())==1
        at.button(key='save_documents').click().run()
        assert not at.exception and len(stored.documents())==3
        at.radio(key='page').set_value('Companies & documents').run()
        at.text_input(key='company_search').set_value('Beta').run()
        assert at.selectbox(key='company_selection').options==['Beta Devices']
        at.button(key='prepare_company_zip').click().run()
        assert not at.exception
        data=at.session_state['zip_company'][1]
        with zipfile.ZipFile(BytesIO(data)) as z:
            assert all(p.startswith('Beta_Devices/') for p in z.namelist())
            assert any(p.endswith('Beta_Devices_Checklist.xlsx') for p in z.namelist())
        for page in ['Uploaded ZIPs','Review files','Data & backups']:
            at.radio(key='page').set_value(page).run()
            assert not at.exception


def test_reset_requires_confirmation_and_deletes_uploaded_zips(tmp_path):
    seed(tmp_path)
    at=app(tmp_path).run()
    at.radio(key='page').set_value('Data & backups').run()
    button=at.button(key='reset_history_button')
    assert button.disabled
    next(c for c in at.checkbox if c.label.startswith('I understand')).check()
    at.text_input(key='reset_confirmation').set_value('RESET HISTORY').run()
    button=at.button(key='reset_history_button')
    assert not button.disabled
    button.click().run()
    assert not at.exception and at.metric[0].value=='0'
    store=Store(tmp_path)
    assert store.documents().empty and store.vendors().empty
    assert store.history()==[] and store.backup_list()==[]
    assert store.upload_archives().empty
