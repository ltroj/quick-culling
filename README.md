# quick-culling
Flexible script to create a file catalog of a directory and find orphaned files (i.e. with missing sidecar file)

## Usage

Run the dashboard using 
```
>>> streamlit run quick_culling_dash.py
```

or use as a flexible library adapted for the individual use case

```python
from quick_culling import file_catalog, copy_files

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
```
