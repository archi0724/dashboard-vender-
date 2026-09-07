# V3.12 Fresh Start QA Report

## Distribution state
- No preloaded companies.
- No preloaded document records or document bytes.
- No uploaded ZIP archive.
- No upload history.
- No saved backups.
- No bundled `vendor_data` runtime directory.

## Delete All Data verification
The reset flow was changed to an always-visible callback-based control in **Data & backups**. The user must tick the permanent-delete checkbox and type `RESET HISTORY` exactly before **DELETE ALL DATA NOW** is enabled. The callback executes deletion before the next Streamlit rerun.

The storage reset now:
- deletes companies and classified document records;
- deletes upload history and saved backups;
- deletes uploaded ZIP archive rows and original ZIP bytes;
- deletes local classified document bytes;
- deletes legacy vendor/document rows and runtime migration/reconciliation artifacts;
- compacts the local SQLite database after deletion;
- verifies all user-data counts and stored-file counts are zero before returning success.

An end-to-end storage test seeded 2 companies, 2 documents, 1 uploaded ZIP, history, a backup, and an extra runtime file. After reset, every checked count was zero and `reset_status()['clean']` was true.

## Automated checks
- 59 core/storage/import tests passed.
- Python syntax compilation passed for `app.py` and `storage.py`.
- Full Streamlit UI automation was not run in this build container because Streamlit is not installed there. The callback/reset source path was reviewed and the storage behavior was executed directly.

## Deployment note
For Streamlit Community Cloud, use a private repository and configure `APP_PASSWORD`. Configure `DATABASE_URL` when uploads must survive app restarts/redeploys. Never commit real secrets or vendor documents to GitHub.
