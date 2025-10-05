import os.path as osp
import tempfile
# https://github.com/modelscope/modelscope/blob/master/modelscope/utils/config.py


def _file2dict(filename):
    # points to file
    filename = osp.abspath(filename)

    #  checks if file exists
    if not osp.exists(filename):
        raise FileNotFoundError(f'File {filename} does not exist.')

    fileExtName = osp.splitext(filename)[1]
    if not fileExtName in ['.yaml', '.yml']:
        raise ValueError('Only yaml or yml file is supported.')

    with tempfile.TemporaryDirectory() as tmp_cfg_dir:

        tmp_cfg_file = tempfile.NamedTemporaryFile(
            dir=tmp_cfg_dir,
            suffix=fileExtName
        )
