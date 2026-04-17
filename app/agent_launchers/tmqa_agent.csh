#!/bin/csh -f
source /remote/cad-rep/etc/.cshrc
module load sia
if ( $#argv != 1 ) then
  echo "Usage: $0 <input_path>"
  exit 1
endif

set input_path = "$1"
set script_dir = `dirname "$0"`
set config_file = "$script_dir/opencode.jsonc"

if ( ! -f "$config_file" ) then
  echo "Error: Cannot find config file at $config_file"
  exit 1
endif

bash -c 'export OPENCODE_CONFIG_CONTENT="$(cat "$1")"; sia run --agent build "Please use timing-qa-analyst to analyse the report $2. Use output folder named timing_qa_analysis_output in the same directory as the input xlsx file. Write Summary_Analysis.csv and Quick_Summary.txt in that folder. Success response must be exactly two lines containing only file paths in this order: line 1 is the final Summary_Analysis.csv path, line 2 is the final Quick_Summary.txt path. No extra text."' -- "$config_file" "$input_path"
