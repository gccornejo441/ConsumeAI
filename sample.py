

from utils.config import _file2dict, summarize_zip
from utils.import_utils import import_modules_from_file

if __name__ == "__main__":
    print(_file2dict("assets/agent.yaml"))
    import_modules_from_file("main.py")
    # summary_file = summarize_zip()
    # if summary_file is None:
    #     print("Error")
    # else:
    #     print(summary_file)