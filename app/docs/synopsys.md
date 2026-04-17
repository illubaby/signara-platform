Install environment
- /depot/Python/Python-3.11.2/bin/python -m venv venv
- source venv/bin/activate.csh
- pip install -r app/requirements.txt
- source app/addition_package.csh

Upload Product Documentation to Synopsys
- bin/python/compare_p4_folders.py app //wwcad/msip/projects/ucie/tb/gr_ucie/design/timing/CloseBeta/bin/python/app -t 12
- bin/python/UploadP4_multi.py -input updated_files.lst -note "v1.2.9"