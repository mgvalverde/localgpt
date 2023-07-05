from pathlib import Path
import re
import importlib
import uuid


def generate_uuid():
    return uuid.uuid4().hex


def check_import(module):
    try:
        importlib.import_module(module)
    except ImportError:
        raise ImportError(
            f"""Could not import the `tinydb` Python package. 
            "Please install it with `pip install {module}`."""
        )


def resolve_path(path: str, mkdir: bool = True) -> str:
    """Extract the path from the connection string"""
    path_res = Path(path).expanduser().resolve()
    if mkdir:
        path_res.parent.mkdir(parents=True, exist_ok=True)
    return str(path_res)


def get_meta_path(fpath: str) -> str:
    """Return the path to the metadata file"""
    return re.sub(r"(.[a-zA-Z0-9]{3,4}$)", r"_meta\1", fpath)
