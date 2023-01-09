# -*- coding: utf-8 -*-
"""
Created on Wed May 25 15:15:25 2022


"""
import json
import streamlit as st
from quick_culling import file_catalog, copy_files

st.title('Quick Culling Tool')

source_dir = st.text_input("Source Dir", r'U:\Python\quick-culling\testroot')
keeper_dir = r'U:\Python\quick-culling\keepers'
rejects_dir = r'U:\Python\quick-culling\rejects'
to_json = st.checkbox('Save file catalog to json file', value=False)
from_json = st.checkbox('Load file catalog from json file', value=False)
copy_inp_files = st.checkbox('Copy input files along', value=True)

input_ext = st.text_input('Input file extension', '.inp')
victim_ext = st.text_input('Target file extension','.vic')

if st.button('Build Catalog'):

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

    keeper_paths
    rejects_paths

    st.write('The following keeper files were found:')
    st.write(catalog_keepers_only)
    
    st.write('The following files are to be culled:')
    st.write(catalog_rejects_only)
    
    if st.button('Copy Files'):
    
        copy_files(keeper_paths, keeper_dir)
        copy_files(rejects_paths, rejects_dir)
        
        if copy_inp_files:
            inp_paths = [d['path'] for d in catalog_input_ext_only]
            copy_files(inp_paths, keeper_dir)
