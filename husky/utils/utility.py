import os
def wise_mk_dir(path):
    if path == "":
        return
    if os.path.exists(path):
        return
    p, c = os.path.split(path)
    if not os.path.exists(p):
        wise_mk_dir(p)
    os.mkdir(path)

def wise_mk_dir_for_file(filepath):
    p = os.path.dirname(filepath)
    wise_mk_dir(p)