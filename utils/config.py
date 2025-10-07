import os.path as osp
import pathlib
import platform
import shutil
import tempfile
import zipfile

# https://github.com/modelscope/modelscope/blob/master/modelscope/utils/config.py


def _file2dict(filename):
    # points to file
    filename = osp.abspath(osp.expanduser(filename))


    #  checks if file exists
    if not osp.exists(filename):
        raise FileNotFoundError(f'File {filename} does not exist.')

    fileExtName = osp.splitext(filename)[1]
    if not fileExtName in ['.yaml', '.yml']:
        raise ValueError('Only yaml or yml file is supported.')

    with tempfile.TemporaryDirectory() as tmp_cfg_dir:

        tmp_cfg_file = tempfile.NamedTemporaryFile(
            dir=tmp_cfg_dir, suffix=fileExtName)

        if platform.system() == "Windows":
            tmp_cfg_file.close()
        tmp_cfg_name = osp.basename(tmp_cfg_file.name)
        shutil.copyfile(filename, tmp_cfg_file.name)


TEMP_DIR = "./assets/temp"
ZIP_FILE = "./assets/test.zip"

def summarize_zip() -> list[dict]:
    summarizes = []

    with tempfile.TemporaryDirectory(dir=TEMP_DIR) as workdir:
        work = pathlib.Path(workdir)

        with zipfile.ZipFile(ZIP_FILE, 'r') as zf:
            zf.extractall(work)

            file_list = zf.namelist()

            for file in file_list:
                file_ext_names = osp.splitext(file)[1]
                if not file_ext_names in ['.txt']:
                    continue
                
                with open(file, "r", encoding="utf-8") as f:
                    file_content = f.read()

                summarizes.append({
                    "file_name": file,
                    "file_content": file_content
                })

    return summarizes

def dict_zip(file="assets/agent.yaml"):
    
    filename = osp.basename(file)
    file_ext = osp.splitext(filename)[1]

    if not file_ext in ['.yaml', '.yml', 'json']:
        raise ValueError('Only yaml or yml file is supported.')
    
    print(filename)
    