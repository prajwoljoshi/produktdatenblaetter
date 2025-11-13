import sys
from pathlib import Path
import re
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        base_path = Path(__file__).parent
    return base_path / relative_path

def extract_language(url):
    match = re.search(r'/(..)-DE/emico', url)
    return match.group(1) if match else None
