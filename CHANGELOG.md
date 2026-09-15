# Current update

- Added Price and Catalogue as company-wise Yes / No checklist categories.
- Price and Catalogue files are recognized across supported file formats from filenames and document-type folders.
- Separate ZIP uploads merge into existing normalized company records, and company Excel/ZIP downloads include the newly classified files.

# Version 3.11 - Fresh company start

- Removed all bundled vendor/company/document data, uploaded ZIP archives, history, backups and migration reports from the distribution.
- Removed named sample upload references from test fixtures and replaced them with generic synthetic names.
- Dashboard starts at 0 / 0 / 0 / 0 on first launch.
- Existing ZIP upload/download, reset, export and optional PostgreSQL persistence features are unchanged.

# Version 3.10 - True Delete All Data reset

- **Reset all history** is now a true full wipe of dashboard user data.
- Deletes companies, classified documents/files, upload history, saved backups, legacy dashboard rows, original uploaded ZIP archive records, and the physical ZIP files in `vendor_data/uploaded_zips`.
- Reset remains available even when the main dashboard is already empty but ZIP archives still exist.
- After reset, all dashboard counters are 0 and **Uploaded ZIP Files** is empty.
- Uploaded ZIPs are still downloadable exactly as uploaded before a reset is performed.

# Version 3.9 - Reset + exact ZIP downloads

- Fixed Reset all history so it actually clears active companies, documents, classified file bytes, upload history, legacy rows and saved backups.
- Reset now preserves only original uploaded ZIP archives and their minimal index metadata.
- Added All uploaded ZIPs head-count view plus per-ZIP head count selection.
- Added a separate Download uploaded ZIP files section with one exact-original download button per saved ZIP filename.
- Original uploaded ZIP bytes are read directly from the archive store; downloads are not reconstructed.
- Updated confirmation phrase to RESET HISTORY and removed the form-based reset execution path.

# Version 3.4 - 7 Sep 2026

- Vendor head count now updates automatically after every document upload using cumulative unique company names. Existing vendors are counted once; new vendor names from later ZIPs are added automatically.
- Upload summary now shows the total vendor head count after the upload.
- Added an **Uploaded ZIPs** section that stores each original ZIP, shows its vendor names/count, files read and upload count, and allows the original ZIP to be downloaded again.
- Re-uploading identical ZIP bytes does not duplicate archive storage; its upload count increments.
- Uploaded ZIP archives are included in dashboard backups and reset/restore.
- No other dashboard workflow or classification rules were changed.

# Version 3.3 - 6 Sep 2026

- Fixed Upload documents navigation crash (`StreamlitWidgetAlreadyInstantiatedError`).
- Navigation now uses a pending-page handoff before the sidebar radio is instantiated.
- Clear search now clears the current dashboard view and intentionally shows 0 for all four summary counters without deleting stored data.
- Added Show saved data action to restore the saved view immediately.
- Reset all data remains the separate protected action that actually removes active records after backup.
- Upload page copy is clearer and remains accessible from the top action bar and sidebar.

# Version 3.1 - 6 Sep 2026

- Renamed the top filter reset to **Clear search** so it is not confused with deleting saved data.
- Added a visible **Reset saved data** action that opens the protected backup-and-reset section.
- Moved the company-wise **Yes / No document checklist** to the top of the Companies screen with Excel and CSV downloads.
- Added a one-click **Yes / No checklist** shortcut from every page.
- Changed local stored filenames to short content-hash names to prevent Windows long-path extraction failures.
- Reconciled the bundled data to 64 companies, 357 available document records, and 9 review items.

# Version 3 - 6 September 2026

Updated the supplied existing project, not a separate replacement dashboard.

- Removed the requested hero slogan and replaced the crowded layout with four clear navigation sections.
- Added visible Reset search with no saved-data deletion.
- Added confirmed data reset with transactional backup, downloadable backups and merge restore.
- Separated global totals from filtered results and per-upload counts.
- Reconciled the supplied arranged archive to 64 companies and 357 company-document records, preserving all 281 earlier records.
- Raised the per-document limit from 32 MB to 128 MB; the source's large PDF now imports. Other path, nesting, entry-count and expanded-size safeguards remain.
- Added durable upload history and explicit duplicate/skipped-file reporting.
- Company downloads now include the company name in ZIP, XLSX and filtered CSV filenames.
- A company ZIP enforces company isolation and contains its own Excel checklist.
- Company Excel sheets now also include non-checklist supporting documents.
- Added generic section-folder handling, extra label variants and supporting-document names. No personal handover names are hard-coded.
- Kept SQLite/local files and PostgreSQL support. Cloud storage still needs configuration; no live cloud deployment is claimed.

Earlier code snapshots are in _backups and are not the app entrypoint.

## Version 3.2 - 6 Sep 2026
- Added a prominent Upload documents button in the dashboard header.
- Clarified Clear search versus Reset all data.
- Full reset now states that all four dashboard summary counts become zero and returns to the checklist page after success.
- Kept automatic backup creation before full reset.


## V3.12 Reset Fix - 7 Sep 2026
- Replaced the rerun-sensitive reset expander flow with an always-visible callback-based Delete All Data panel.
- Reset now verifies database rows, uploaded ZIP archive rows, stored document bytes, ZIP bytes, history, backups and runtime artifacts are empty before reporting success.
- Local SQLite is compacted after reset so deleted user rows are removed from unused database pages.
- Reset remains idempotent and can be run even when the visible dashboard is already empty.
