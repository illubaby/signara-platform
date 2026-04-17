#!/bin/csh -f
source /remote/cad-rep/etc/.cshrc
module load sia
if ( $#argv < 1 ) then
  echo "Usage: $0 <question...>"
  exit 1
endif

set question = "$*"
set script_dir = `dirname "$0"`
set config_file = "$script_dir/../opencode.jsonc"

if ( ! -f "$config_file" ) then
  echo "Error: Cannot find config file at $config_file"
  exit 1
endif

bash -c 'export OPENCODE_CONFIG_CONTENT="$(cat "$1")"; sia run --agent --model snpsazure/gpt-5.4 build "$2."' -- "$config_file" "$question"
