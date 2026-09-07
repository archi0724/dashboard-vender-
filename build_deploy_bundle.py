"""Create a code-only ZIP. Uses an explicit allowlist: no private documents."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
FILES = [
    'app.py', 'vendor_core.py', 'storage.py', 'exports.py', 'import_service.py', 'requirements.txt',
    'README.md', 'DEPLOY_TO_STREAMLIT.md', 'CHANGELOG.md', 'QA_REPORT.md',
    '.gitignore', '.streamlit/config.toml', '.streamlit/secrets.toml.example',
    'START_WINDOWS.bat', 'build_deploy_bundle.py', 'tests/test_core.py', 'tests/test_app.py', 'tests/test_updates.py', 'START_HERE.txt',
]


def build(output: Path | None = None) -> Path:
    output = output or ROOT.parent / 'venders_dashboard_streamlit_source.zip'
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in FILES:
            file = ROOT / name
            if file.is_file(): archive.write(file, name)
        archive.writestr('CLOUD_DEPLOYMENT', 'Code-only deployment. APP_PASSWORD must be configured before data access.\n')
    return output


if __name__ == '__main__':
    print(build())
