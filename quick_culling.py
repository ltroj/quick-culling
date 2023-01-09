# -*- coding: utf-8 -*-
import os
import os.path
from shutil import copyfile
import errno
import json

def walklevel(path, depth = -1):
    """
    It works just like os.walk, but you can pass it a level parameter
    that indicates how deep the recursion will go.
    If depth is 0, the current directory is listed.
    If depth is >0, the given depth is walked.
    If depth is -1 (or less than 0), the full depth is walked.
    https://gist.github.com/TheMatt2/faf5ca760c61a267412c46bb977718fa
    """
    # If depth is negative, just walk
    # Not using yield from for python2 compat
    # and copy dirs to keep consistant behavior for depth = -1 and depth = inf
    if depth < 0:
        for root, dirs, files in os.walk(path):
            yield root, dirs[:], files
        return
    #elif depth == 0:
    #    return

    # path.count(os.path.sep) is safe because
    # - On Windows "\\" is never allowed in the name of a file or directory
    # - On UNIX "/" is never allowed in the name of a file or directory
    # - On MacOS a literal "/" is quitely translated to a ":" so it is still
    #   safe to count "/".
    base_depth = path.rstrip(os.path.sep).count(os.path.sep)
    for root, dirs, files in os.walk(path):
        yield root, dirs[:], files
        cur_depth = root.count(os.path.sep)
        if base_depth + depth <= cur_depth:
            del dirs[:]
            
def file_catalog(root, depth=-1, ext=None, to_json=False):
    """
    Generate a list of all files within a directory (including subdirs). Return
    s a list of dicts with the following keys:
        'name' : file name without extension
        'ext' : file extension
        'path' : full file path
        'dir path': full path of parent dir of file
    If parameter 'ext' is provided, only files with the given extension will be
    added to the list.

    Parameters
    ----------
    root : str
        Root path
    depth : int, optional
        Indicates how deep the recursion will go. The default is -1.
    ext . str
        Only files with provided file extension will be added to the list.
        Example: '.pdf', '.txt'. Currently only a single string is supported.

    Returns
    -------
    l : list
        List of dicts.

    """
    l = []
    for dirpath, dirnames, filenames in walklevel(root, depth):
        for full_filename in filenames:
            filename, file_extension = os.path.splitext(full_filename)
            index = filename.split("_")[-1].upper()  # 89734A-001_1_a --> ['89734A-001', '1', 'a'] --> 'a' --> 'A'
            if not index.isalpha():  # If index is not a letter
                index = '.'
            name_stripped = filename.split("_")[0]
            if not ext or ext == file_extension:
                l.append({'name': filename,
                          'name_stripped': name_stripped,
                          'ext': file_extension,
                          'path': os.path.join(dirpath, full_filename),
                          'dir_path': dirpath,
                          'index': index})
    if to_json:
        # Writing a JSON file
        with open('file_catalog.json', 'w') as f:
            json.dump(l, f, indent=4)

    return l
            
def copy_files(fpaths, target_dir):
    """
    Copies files provided in list fpaths to target_dir (without creating subdir
    s).

    Parameters
    ----------
    fpaths : list
        List of source files (full file paths).
    target_dir : str
        Path for target directory.

    Returns
    -------
    None.

    """
    print('No of files to copy: '+str(len(fpaths)))
    i = 1
    for fp in fpaths:
        print(str(i)+': '+fp)
        _, file = os.path.split(fp)
        dst = os.path.join(target_dir, file)
        if not os.path.exists(os.path.dirname(dst)):
            try:
                os.makedirs(os.path.dirname(dst))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        copyfile(fp, dst)
        i+=1
        

if __name__ == "__main__":

    source_dir = r'U:\Python\quick-culling\testroot'
    keeper_dir = r'U:\Python\quick-culling\keepers'
    rejects_dir = r'U:\Python\quick-culling\rejects'
    to_json = False
    from_json = False
    copy_inp_files = True
    
    input_ext = '.inp'
    victim_ext = '.vic'
    
    if from_json:
        with open('file_catalog.json', 'r') as f:
            catalog = json.load(f)
            
        if to_json:  # If from_json AND to_json
            print('Parameters to_json and from_json both TRUE. Did not write json file.')   
    
    else:
        catalog = file_catalog(source_dir, depth=-1, ext=None, to_json=to_json)
    
    catalog_input_ext_only = [d for d in catalog if d['ext']==input_ext]
    input_names = [d['name'] for d in catalog_input_ext_only]
    catalog_keepers_only = [d for d in catalog if d['name'] in input_names and d['ext']==victim_ext]
    catalog_rejects_only = [d for d in catalog if d['name'] not in input_names and d['ext']==victim_ext]
    
    keeper_paths = [d['path'] for d in catalog_keepers_only]
    rejects_paths = [d['path'] for d in catalog_rejects_only]
    
    copy_files(keeper_paths, keeper_dir)
    copy_files(rejects_paths, rejects_dir)
    
    if copy_inp_files:
        inp_paths = [d['path'] for d in catalog_input_ext_only]
        copy_files(inp_paths, keeper_dir)
    