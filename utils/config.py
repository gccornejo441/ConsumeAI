import os.path as osp

def _file2dict(filename):
    filename = osp.abspath(osp.expanduser(filename))
    if not osp.exists(filename):
        raise FileNotFoundError(f"File does not exist: {filename}")
    fileExtname = osp.splitext(filename)[1]

    print(f"fileExtname: {fileExtname}")