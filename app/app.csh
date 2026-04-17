#!/bin/csh

set protected_dir = "/u/trankiet/projects/signara-platform"

if ("$cwd" =~ "*$protected_dir*") then
    echo "Refusing to start from protected directory: $cwd"
    exit 1
endif

setenv PYTHONPYCACHEPREFIX "$HOME/.cache/signara-platform/pycache"
mkdir -p "$PYTHONPYCACHEPREFIX"
	
# Free port 8000 if already in use
set pidlist = `lsof -ti :8000`
if ($#pidlist > 0) then
    echo "Port 8000 in use by PIDs: $pidlist. Killing..."
    foreach pid ($pidlist)
        kill -9 $pid
    end
endif
if ( ! $?prompt ) set prompt = ""
source /u/trankiet/projects/signara-platform/venv/bin/activate.csh

ln -sf /u/trankiet/projects/signara-platform/app .
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000