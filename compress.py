#!/usr/bin/python

import sys
import os
import os.path
import zipfile
dirpath=sys.argv[1]
zippath=sys.argv[2]
fzip = zipfile.ZipFile(zippath, 'w', zipfile.ZIP_DEFLATED)
basedir = os.path.dirname(dirpath) + '/' 
for root, dirs, files in os.walk(dirpath):
    if os.path.basename(root)[0] == '.':
        continue #skip hidden directories        
    dirname = root.replace(basedir, '')
    for f in files:
        if f[-1] == '~' or (f[0] == '.' and f != '.htaccess'):
            #skip backup files and all hidden files except .htaccess
            continue
        fzip.write(root + '/' + f, dirname + '/' + f)
fzip.close()

