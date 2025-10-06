import ast
import os.path as osp
from pathlib import Path
import sys


def import_modules_from_file(py_file: str):
    """ Import module from a certain file

    Args:
        py_file (str): path to .py file

    """

    dirname, basefile = osp.split(py_file)
    if dirname == "":
        dirname = Path.cwd()
    module_name = osp.splitext(basefile)[0]
    sys.path.insert(0, dirname)
    validate_py_syntax(py_file)

def validate_py_syntax(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    try:
        ast.parse(content)
    except SyntaxError as e:
        raise SyntaxError('There are syntax errors in config '
                          f'file {filename}: {e}')