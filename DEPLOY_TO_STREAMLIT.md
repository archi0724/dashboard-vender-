# Version 3 note

This update includes import_service.py; it must be uploaded with the other source files. Use the new code-only package, not an earlier archive. Reset/backup controls are under Data & backups.

# Streamlit deployment - exact handoff

**Live publication has not been performed.** A connected GitHub account/repository,
your Streamlit login, and the chosen cloud-storage connection are still required.
Do not paste passwords or database credentials into a chat message.

## 1. Upload ONLY the clean source to GitHub

Extract `venders_dashboard_streamlit_source.zip`. Put all its contents in a new
private GitHub repository. `app.py` should be at the repository root. Include the
`.streamlit` folder and `CLOUD_DEPLOYMENT` file. The code-only archive contains no
vendor documents, old database, personal data, `.venv`, real secrets or backups.

Do NOT upload `venders_dashboard_updated.zip`, `vendor_data/`, `_backups/`, any real
vendor ZIP, or `.streamlit/secrets.toml` to a repository, even a private one.

## 2. Prepare durable storage and access

Use an organization-approved PostgreSQL database. Obtain the connection URL and
make sure the Streamlit app can reach it over TLS. The application role must be
allowed to create/use the `vdd_*` tables in its database/schema. Prefer a dedicated
database and role for this application, with suitable backups and storage quotas.
The app stores the file bytes as PostgreSQL BYTEA as well as storing metadata.
For large-scale document repositories, plan separate object storage/retention capacity.

In Streamlit Cloud **Advanced settings > Secrets**, enter real values:

```toml
APP_PASSWORD = "YOUR-LONG-UNIQUE-TEAM-PASSWORD"
DATABASE_URL = "postgresql://USER:URL_ENCODED_PASSWORD@HOST:5432/DATABASE?sslmode=require"
```

The database password in a URL must be percent-encoded when it contains characters
such as `@`, `/`, `:` or `#`. Use the provider's supplied connection string, not an
example copied without replacing the values. The code uses TLS in cloud mode.

For a temporary demonstration, DATABASE_URL can be omitted. The app prominently
warns that local storage on Community Cloud is not durable. That mode is NOT suitable
for the requirement that future uploads remain permanently recorded.

Restrict the app to authorized viewers in Streamlit's sharing settings. A shared
password alone is not a replacement for organization-approved authentication, access
management and audit controls for PAN/Aadhaar/banking data.

## 3. Deploy

Open https://share.streamlit.io and sign in. Choose **Create app > Yup, I have an app**.
Select your GitHub repository and branch, with:

```text
Branch: main (or your actual default branch)
Main file path: app.py
Python: 3.12
```

Set Secrets through **Advanced settings**, then deploy. A public `*.streamlit.app`
address exists only after Streamlit finishes a successful deployment. This package
does not fabricate or pre-allocate an app URL.

## 4. First use

Open the deployed app, enter the team password and upload your ORIGINAL vendor
handover ZIP from the sidebar. Click **Classify & save documents**. There is no need
to put a vendor ZIP in GitHub, and no need to load the sample handover before deployment.
The original local records are kept in the private updated project, not published.

After uploading, confirm counts and the review queue. Test with a new browser session
and an app reboot while DATABASE_URL remains configured. Verify provider-side backups.

## Troubleshooting

- Missing app.py: upload extracted contents, not the ZIP itself or a nested folder.
- `ModuleNotFoundError`: keep all four `.py` modules and requirements.txt together.
- Password setup screen: add APP_PASSWORD in Streamlit Settings > Secrets.
- Storage could not be opened: check URL, TLS/network access and CREATE/table permissions.
  The app does not expose the database password in a user-facing error message.
- Data disappeared in Cloud local mode: configure external storage before real use;
  a local filesystem is not guaranteed to survive app lifecycle events.
- Unnamed scanned documents: keep company folders and meaningful filenames, or classify
  those particular files through Review queue. No OCR accuracy is promised.

## Official references

- Deployment: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- Secrets: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
- Local-storage warning: https://docs.streamlit.io/develop/concepts/connections/connecting-to-data
- Private sharing: https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app
- PostgreSQL driver: https://www.psycopg.org/psycopg3/docs/basic/usage.html
