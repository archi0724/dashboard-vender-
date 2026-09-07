from io import BytesIO
from pathlib import Path
import hashlib
import json
import sqlite3
import zipfile

import pandas as pd
import pytest
from openpyxl import load_workbook

from vendor_core import *
from storage import Store
from exports import workbook_bytes, csv_bytes


class Upload:
    def __init__(self,name,data):self.name,self.data=name,data
    def getvalue(self):return self.data


def make_zip(entries):
    buffer=BytesIO()
    with zipfile.ZipFile(buffer,'w') as z:
        for name,data in entries.items():z.writestr(name,data)
    return buffer.getvalue()


@pytest.mark.parametrize('wrapper',['Example Vendor Batch','Example vendor','Sample vendor','Test vendors','Generic Vendor Documents','Vendor Documents','Handover 2026','Team files'])
def test_handover_is_not_company(wrapper):
    result=classify(wrapper+'/01 - Alpha Medical LLP/Documents/GST - Personal Name.pdf')
    assert result.company_name=='Alpha Medical LLP'
    assert result.document_types==('GST',)


@pytest.mark.parametrize('filename,expected',[
    ('cancel chq.jpeg',['Cancelled Cheque']),('cancelled_cheque.jpg',['Cancelled Cheque']),
    ('GSTIN certificate.PDF',['GST']),('PAN Card.pdf',['PAN Card']),('DeepakIndustrypancard.pdf',['PAN Card']),
    ('spandan pro cdsco.pdf',[]),('company brochure.pdf',[]),('CERTIFICATEOFINCORPORATION.pdf',[]),
    ('company_registration_certificate.pdf',[]),('startup certificate.pdf',[]),('GST INVOICE.pdf',[]),('GST-CHALLAN.pdf',[]),
    ('UDHYAM.pdf',['Udyam']),('MSME.jpg',['Udyam']),('Udyog Aadhar Registration Certificate.pdf',['Udyam']),
    ('udyam aadhaar msme.pdf',['Udyam']),('Aadhaar.pdf',['Aadhar']),('deepakindustrysadharcard.jpeg',['Aadhar']),
    ('MD5.pdf',['MD']),('MD-42.pdf',['MD']),('FORM MD-9.pdf',['MD']),('TestLicenseMD13.pdf',['MD']),
    ('ISO13485.pdf',['ASF ISO']),('9001 certificate.pdf',['ASF ISO']),('ISO 13485 MD-205023082615.pdf',['ASF ISO']),
    ('isolator.pdf',[]),('Form_16.pdf',['Form 16']),('Form 16A.pdf',[]),('GST and PAN.pdf',['GST','PAN Card']),
])
def test_types(filename,expected):assert types_from_name(filename)==expected


def test_company_folder_over_person_filename():
    result=classify('Example vendor/Annai Latex/PAN CARD - SHYAM PILLAI.jpg.jpeg',['SHYAM PILLAI'])
    assert result.company_name=='Annai Latex'


def test_subfolder_category_and_windows_path():
    result=classify('Sample vendor\\Company B\\Certificates\\PAN Card\\scan001.pdf')
    assert result.company_name=='Company B'
    assert result.document_types==('PAN Card',)


def test_hyphenated_company_and_numbering():
    assert classify('03. TRI-X/GST.pdf').company_name=='TRI-X'
    assert classify('TRI-X - GST.pdf').company_name=='TRI-X'
    assert clean_company('3M India')=='3M India'


def test_flat_ambiguous_is_retained_for_review():
    assert classify('GST - Mr Smith.pdf').company_name is None
    assert classify('scan001.pdf').needs_review


def test_company_keyword_is_not_category():
    assert classify('PAN Industries/GST.pdf').document_types==('GST',)


def test_archive_unsafe_paths_and_unsupported():
    z=make_zip({'../escape.pdf':b'x','/root.pdf':b'x','Example vendor/Alpha/GST.pdf':b'ok','Alpha/run.exe':b'x','__MACOSX/._foo.pdf':b'x'})
    limits=ArchiveLimits()
    records=list(iter_uploads([Upload('a.zip',z)],limits))
    assert len(records)==1 and records[0][0]=='Example vendor/Alpha/GST.pdf'
    assert len(limits.skipped)==3


def test_nested_zip_and_empty_folder():
    inner=make_zip({'Company A/PAN.pdf':b'pan'})
    outer=make_zip({'Example vendor/batch.zip':inner,'Example vendor/Company B/':b''})
    upload=Upload('outer.zip',outer)
    records=list(iter_uploads([upload]))
    assert classify(records[0][0]).company_name=='Company A'
    assert 'Company B' in discover_folder_companies([upload])


def test_archive_limits():
    limits=ArchiveLimits(max_file_bytes=2)
    records=list(iter_uploads([Upload('a.zip',make_zip({'A/GST.pdf':b'123'}))],limits))
    assert not records and limits.skipped


def test_store_dedup_and_company_isolation(tmp_path):
    store=Store(tmp_path)
    for name in ['Alpha','Beta']:
        assert store.save_document(f'{name}/GST.pdf',b'same-bytes',classify(f'{name}/GST.pdf'))
    assert not store.save_document('Alpha/GST.pdf',b'same-bytes',classify('Alpha/GST.pdf'))
    assert len(store.documents())==2
    checklist=build_checklist(store.vendors(),store.documents())
    assert checklist.GST.tolist()==['Yes','Yes']
    assert set(checklist['PAN Card'])=={'No'}
    docs=store.documents(); assert len(docs[docs.company_key=='alpha'])==1
    zipdata=store.company_zip('Alpha',docs[docs.company_key=='alpha'])
    with zipfile.ZipFile(BytesIO(zipdata)) as z:assert all(p.startswith('Alpha/') for p in z.namelist())


def test_unknown_save_review_and_presence(tmp_path):
    store=Store(tmp_path)
    store.save_document('scan001.png',b'opaque',classify('scan001.png'))
    docs=store.documents();assert len(docs)==1 and bool(docs.iloc[0].needs_review)
    store.correct_document(int(docs.iloc[0].id),'Alpha',['PAN Card'])
    checklist=build_checklist(store.vendors(),store.documents())
    assert checklist.iloc[0]['PAN Card']=='Yes'
    store2=Store(tmp_path)
    assert store2.documents().iloc[0].method=='Reviewed'
    store2.correct_document(int(docs.iloc[0].id),'Alpha',[])
    assert not bool(store2.documents().iloc[0].needs_review)


def test_missing_file_not_yes_reupload_repairs(tmp_path):
    store=Store(tmp_path)
    decision=classify('Alpha/GST.pdf')
    store.save_document('Alpha/GST.pdf',b'gst',decision)
    path=store.safe_path(store.documents().iloc[0].stored_path);path.unlink()
    assert build_checklist(store.vendors(),store.documents()).iloc[0].GST=='No'
    assert not store.save_document('Alpha/GST.pdf',b'gst',decision)
    assert build_checklist(store.vendors(),store.documents()).iloc[0].GST=='Yes'


def test_legacy_windows_migration(tmp_path):
    content=b'original-file';digest=hashlib.sha256(content).hexdigest()
    (tmp_path/'files').mkdir();(tmp_path/'files'/'original.pdf').write_bytes(content)
    with sqlite3.connect(tmp_path/'vendor_documents.db') as db:
        db.execute('CREATE TABLE vendors(company_key TEXT,company_name TEXT,created_at TEXT,updated_at TEXT)')
        db.execute('CREATE TABLE documents(id INTEGER,company_key TEXT,company_name TEXT,document_type TEXT,filename TEXT,stored_path TEXT,uploaded_at TEXT,file_hash TEXT)')
        db.execute("INSERT INTO vendors VALUES('person','Someone Personal','','')")
        db.execute('INSERT INTO documents VALUES(?,?,?,?,?,?,?,?)',(1,'person','Someone Personal','PAN Card','Example vendor/Real Company/GST - Someone Personal.pdf','vendor_data\\files\\original.pdf','2026-09-01',digest))
    store=Store(tmp_path);assert store.vendors().company_name.tolist()==['Real Company']
    assert store.read_bytes(1)==content
    assert store.documents().iloc[0].types==['GST']
    assert (tmp_path/'backups'/'vendor_documents_before_update.db').exists()
    assert len(Store(tmp_path).documents())==1


def test_filter_literal_no_stale_match(tmp_path):
    store=Store(tmp_path)
    for name in ['Alpha (A+B)','Beta']:
        store.save_document(f'{name}/GST.pdf',name.encode(),classify(f'{name}/GST.pdf'))
    checklist=build_checklist(store.vendors(),store.documents())
    assert len(filter_checklist(checklist,'(A+B)'))==1
    assert filter_checklist(checklist,'not-present').empty


def test_excel_headers_formulas_and_injection(tmp_path):
    store=Store(tmp_path)
    store.save_document('Alpha/GST.pdf',b'one',classify('Alpha/GST.pdf'))
    store.save_document('=MALICIOUS()/PAN.pdf',b'two',classify('=MALICIOUS()/PAN.pdf'))
    checklist=build_checklist(store.vendors(),store.documents())
    data=workbook_bytes(checklist,store.documents(),True)
    book=load_workbook(BytesIO(data),data_only=False)
    assert book['Document Checklist']['B4'].value=='Cancelled Cheque'
    assert book['Document Checklist']['J5'].value=='=COUNTIF(B5:I5,"Yes")'
    assert book['Document Checklist']['A5'].data_type=='s'
    for sheet in book:
        if sheet.title not in {'Document Checklist','Document Register','Read me'}:
            assert sheet['A1'].data_type=='s'
    csv=csv_bytes(pd.DataFrame({'Company Name':['=HYPERLINK("x")']})).decode()
    assert "'=HYPERLINK" in csv
