
## V3.12 Fresh Start - Reset Fix

This distribution contains application code only. It ships with no vendor companies, no document records, no uploaded ZIP archives, no upload history, no backups, and no migration reports. On first launch the dashboard starts at 0 companies / 0 documents / 0 complete / 0 review. Runtime data is created in `vendor_data/` and is excluded from Git by `.gitignore`.

# Vendor Document Dashboard - version 3.12 Fresh Start

Use the same Streamlit project to upload company folders, save documents, search companies and download company-named files.

## Start on Windows

1. Extract the complete ZIP. Do not run inside the ZIP viewer.
2. Open the `venders dashboard` folder containing `app.py`.
3. Double-click `START_WINDOWS.bat`. Keep the terminal open while using the app.

Python 3.12 or 3.13 and an internet connection for the initial dependency install are required. Alternatively, run from that folder in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.headless false
```

Open the Local URL printed by Streamlit (normally http://127.0.0.1:8501). This is local testing, not a public deployment.

## Use the dashboard

- **Upload documents**: select your document ZIP and click Save documents. Leave "Company for loose files only" blank for company-folder ZIPs. Existing records remain saved. The vendor head count updates automatically from unique company names across all saved batches.

ZIP uploads are supported up to 5 GB per upload. The application still limits expanded archive data to 1 GB total, individual documents to 128 MB, and archive entries to 5,000 for safety.
- **Companies & documents**: search a name, select the company, view the fixed-order categories, and download its Excel. Prepare all company documents, then download the company-named ZIP.
- **Uploaded ZIPs**: view every unique original ZIP saved by the dashboard, its vendor count, vendor names, file count and upload count, and download the original ZIP again.
- **Review files**: correct unclear company/type mappings. Use Show all documents for correction to change any classification.
- **Data & backups**: download a full backup, restore an app backup, view upload history, or reset saved data.

The old "Company folders in..." slogan has been removed.

## Counts and classification

One company = one normalised company-folder/master name. Names are not matched fuzzily. Distinct legal entities are not merged based on similar wording. Generic handover, document-type and section folders are not counted as companies.

Top cards always show all saved data, even while searching. The result caption separately shows filtered counts. Files and document types are different: several versions of a GST certificate are several files but only one available GST category.

A file with identical SHA-256 bytes uploaded again for the same company is not a new document. Identical bytes in different companies stay separate company records.

**Yes means an available file is classified to that category. No means no matching classified file was found. Neither means authenticity, validity, expiry or completeness has been verified.** Classification uses filenames and document-type folders. Optional PDF-heading extraction is available; no OCR or external API is used. Review unclear files and Other documents before concluding a required document was never provided.

The checklist categories are Cancelled Cheque, GST, MD, Udyam, ASF ISO, PAN Card, Form 16, Aadhar, Price and Catalogue. Price files are recognized from labels such as price list, pricelist, pricing, rate list and rate card. Catalogue files are recognized from catalogue, catalog and product catalog labels. These classifications work for supported PDF, image, Excel, Word, CSV and text files; the filename or document-type folder supplies the label. Supporting records have descriptive labels in the Excel register and company sheets rather than being forced into a wrong category.

Price and Catalogue files uploaded in separate ZIPs are merged by normalized company name. Each company Excel checklist shows Yes or No for both categories, and each company's downloadable ZIP includes all available files grouped under the company and category folders.

Future uploads use a canonical company key across ZIPs, PDFs, folders, spreadsheets, CSVs and supported document files. Matching ignores capitalization, punctuation, spacing and common legal suffixes such as Pvt, Ltd, LLC, Inc and Corp. A unique shared initial/core name is matched to the existing company; ambiguous matches are retained for review instead of being silently merged. Exact duplicate file bytes for one company are skipped.

## Reset is safe and explicit

**Reset search** clears only the screen search, filters, selected company and prepared exports. It does not touch the database.

**Data & backups > Reset saved dashboard data** requires both the checkbox and the exact phrase `RESET DATA`. It creates a restorable ZIP backup in the database in the same transaction before emptying active records. If backup validation fails, reset is refused. Saved reset backups can be restored after restarting the app. Reset is not a permanent secure erase: backup copies and original local file bytes are retained. Legacy migration is not re-run after a reset.

Restore merges into existing data. Repeated files are skipped; existing records are not silently discarded. A storage failure during restore can leave a partially merged restore; retrying is safe.

## Storage

Local data is under `vendor_data` next to app.py, unless VENDOR_DATA_DIR is explicitly configured. Original uploaded ZIPs are stored under `vendor_data/uploaded_zips` locally and in PostgreSQL when cloud storage is configured. Keep the data directory when updating. Closing the browser or terminal does not reset records. Store the full ZIP privately.

For an existing installation with newer uploads than this supplied package, back up first and replace source files only; do not overwrite your newer vendor_data folder. Then upload the arranged document ZIP through the dashboard to reconcile it.

Streamlit Community Cloud does not guarantee local-disk persistence. Configure `DATABASE_URL` for PostgreSQL storage of metadata, files and reset backups. The cloud provider controls quota, retention and backups. Local records are not silently copied to a remote database; upload documents there or restore an app backup.

## Included source-data reconciliation (full package only)

The full package preserves the 281 document records in the supplied project and adds 76 documents from the supplied arranged archive. It contains 64 companies and 357 available company-document records. The original archive contains 360 file entries; three within-company identical-file repeats are deduplicated. Nine filenames remain unclear and are flagged for review. No file was skipped in the final import. Details are in `vendor_data/reconciliation_v3.json`.

The small GitHub package contains code only. It starts with no vendor data; it is not a copy of the populated dashboard.

## Deployment

Do not push the full private package to GitHub. Run:

```powershell
.\.venv\Scripts\python.exe build_deploy_bundle.py
```

This produces a source-only ZIP beside the project folder. Extract its contents to your GitHub repository root. Use app.py as the Streamlit entrypoint. Set APP_PASSWORD in Streamlit Secrets and restrict viewers. See DEPLOY_TO_STREAMLIT.md. No live cloud deployment was made as part of this update.

## Verification

Run `python -m pytest tests -q` after installing pytest for development. See QA_REPORT.md for the actual verification and environment limits.

References:
- https://docs.streamlit.io/develop/concepts/architecture/run-your-app
- https://docs.streamlit.io/develop/concepts/connections/connecting-to-data
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy


## V3.10 reset and ZIP archive behavior

Reset All History is now a true **Delete All Data** action. It permanently clears active dashboard/classification data, upload history, legacy rows, saved backups, classified document bytes, **all original uploaded ZIP archive records, and the physical uploaded ZIP files**. After reset, the four main dashboard counters are 0 and Uploaded ZIP Files is empty. Before reset, each archived ZIP can still be downloaded with its original filename and exact original bytes.


### Delete All Data (V3.12)
Open **Data & backups**, tick the permanent-delete confirmation, type `RESET HISTORY`, and click **DELETE ALL DATA NOW**. Success is shown only after companies, documents, history, backups, uploaded ZIP records and stored file bytes are verified empty.
