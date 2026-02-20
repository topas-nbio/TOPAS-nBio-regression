#!/usr/bin/env bash
#
# =============================================================================
# Script to perform TOPAS-nBio regression tests in batches
# =============================================================================
#
# In principle the ONLY file you need to edit is batch_config.json.
#
# What this script does:
#   1. Reads the settings you supply to batch_config.json for each test
#   2. Modifies the the topas/python command strings and run folder name in
#      in submitLocally.sh/runMain.py accordingly, then runs the tests.
#   3. Restores the original submitLocally.sh/runMain.py files after the test 
#      are done.
#
# By using this script you never have to edit submitLocally.sh by hand
#
# You need: jq (to read the JSON config) and tcsh (to run the tests).
#
# Usage:
#   ./run_batch.sh              # run all tests listed in batch_config.json
#   ./run_batch.sh --dry-run    # only show what would be run, don't run it
#
# =============================================================================

set -e

# -----------------------------------------------------------------------------
# Step 1: Find the script directory and the config file
# -----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
CONFIG_FILE="${SCRIPT_DIR}/batch_config.json"

# Check if the user asked for a dry run (show plan only, do not run or patch)
DRY_RUN="no"
for arg in "$@"; do
  if [[ "$arg" == "--dry-run" || "$arg" == "-n" ]]; then
    DRY_RUN="yes"
    break
  fi
done

# -----------------------------------------------------------------------------
# Step 2: Check that we have the tools and config we need
# -----------------------------------------------------------------------------
if ! command -v jq &>/dev/null; then
  echo "Error: This script needs 'jq' to read the JSON config file." >&2
  echo "Install jq (e.g. from https://stedolan.github.io/jq/) and try again." >&2
  exit 1
fi

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Error: Config file not found: $CONFIG_FILE" >&2
  exit 1
fi

# -----------------------------------------------------------------------------
# Step 3: Read the config file
# -----------------------------------------------------------------------------
# We read each value from the JSON. If a value is missing we use a default
# or leave it empty and check later.

RUN_FOLDER_NAME=$(jq -r '.run_folder_name // empty' "$CONFIG_FILE")
TOPAS_EXECUTABLE=$(jq -r '.topas_executable // empty' "$CONFIG_FILE")
PYTHON_CMD=$(jq -r '.python_cmd // empty' "$CONFIG_FILE")
DEFAULT_RUNS=$(jq -r '.default_runs // 5' "$CONFIG_FILE")
MAX_PARALLEL_JOBS=$(jq -r '.max_parallel_jobs // 1' "$CONFIG_FILE")

# These three must be set in the config
if [[ -z "$RUN_FOLDER_NAME" || -z "$TOPAS_EXECUTABLE" || -z "$PYTHON_CMD" ]]; then
  echo "Error: In batch_config.json you must set: run_folder_name, topas_executable, and python_cmd." >&2
  exit 1
fi

# Read the list of test names (the "tests" array in the JSON)
TESTS_RAW=$(jq -r '.tests[]?' "$CONFIG_FILE")
TESTS=()
while IFS= read -r line; do
  if [[ -n "$line" ]]; then
    TESTS+=("$line")
  fi
done <<< "$TESTS_RAW"

if [[ ${#TESTS[@]} -eq 0 ]]; then
  echo "Error: In batch_config.json you must set 'tests' to a non-empty list of test folder names." >&2
  exit 1
fi

# -----------------------------------------------------------------------------
# This function gets the number of runs to do for a given test
# -----------------------------------------------------------------------------
# If runs_per_test has an entry for this test, use that; otherwise use default_runs.
get_runs_for_test() {
  local test_name="$1"
  local runs
  runs=$(jq -r --arg t "$test_name" '.runs_per_test[$t] // .default_runs // 5' "$CONFIG_FILE")
  echo "$runs"
}

# -----------------------------------------------------------------------------
# This function makes a string safe to use inside a sed replacement. sed uses 
# special characters in replacements; we escape backslash and ampersand
# so that the config value is used literally.
# -----------------------------------------------------------------------------
escape_for_sed() {
  printf '%s' "$1" | sed 's/[\\&]/\\&/g'
}

# -----------------------------------------------------------------------------
# This function saves copies ofsubmittedLocally.sh and runMain.py so we can 
# restore them later. It saves the original file to a temporary backup, remembers 
# the path of the original file and the backup path so we can copy the backup back 
# when the test is done.
# -----------------------------------------------------------------------------
SAVED_FILE_PATHS=()
SAVED_BACKUP_PATHS=()

save_original_file() {
  local file_path="$1"
  if [[ ! -f "$file_path" ]]; then
    echo "Warning: File not found, skipping backup: $file_path" >&2
    return
  fi
  local backup_file
  backup_file=$(mktemp)
  cp "$file_path" "$backup_file"
  SAVED_FILE_PATHS+=("$file_path")
  SAVED_BACKUP_PATHS+=("$backup_file")
}

# -----------------------------------------------------------------------------
# This function restores all files we backed up.
# -----------------------------------------------------------------------------
restore_all_saved_files() {
  local i
  for (( i=0; i < ${#SAVED_FILE_PATHS[@]}; i++ )); do
    local original_path="${SAVED_FILE_PATHS[$i]}"
    local backup_path="${SAVED_BACKUP_PATHS[$i]}"
    if [[ -f "$backup_path" ]]; then
      cp "$backup_path" "$original_path"
      rm -f "$backup_path"
    fi
  done
  SAVED_FILE_PATHS=()
  SAVED_BACKUP_PATHS=()
}

# -----------------------------------------------------------------------------
# This function does everything for one test: backup, patch, run, restore.
# -----------------------------------------------------------------------------
run_single_test() {
  local test_name="$1"
  local test_dir="$SCRIPT_DIR/$test_name"
  local num_runs
  num_runs=$(get_runs_for_test "$test_name")

  # Check that the test directory and script exist
  if [[ ! -d "$test_dir" ]]; then
    echo "Error: Test directory not found: $test_dir" >&2
    return 1
  fi
  if [[ ! -f "$test_dir/submitLocally.sh" ]]; then
    echo "Error: submitLocally.sh not found in $test_dir" >&2
    return 1
  fi

  local submit_script="$test_dir/submitLocally.sh"
  local runmain_script="$test_dir/ParameterFiles/runMain.py"

  # -------- Dry run: only print what we would do --------
  if [[ "$DRY_RUN" == "yes" ]]; then
    echo "[dry-run] Test: $test_name (runs=$num_runs)"
    echo "          Would patch: $submit_script"
    if [[ "$test_name" == "Gvalue_LET-IRT" || "$test_name" == "Gvalue_LET-SBS" ]]; then
      if [[ -f "$runmain_script" ]]; then
        echo "          Would patch: $runmain_script"
      fi
    fi
    return 0
  fi

  # -------- Step A: Back up the files we are about to change --------
  save_original_file "$submit_script"
  if [[ "$test_name" == "Gvalue_LET-IRT" || "$test_name" == "Gvalue_LET-SBS" ]]; then
    if [[ -f "$runmain_script" ]]; then
      save_original_file "$runmain_script"
    fi
  fi

  # -------- Step B: Prepare escaped strings for sed --------
  # (so that characters in the config don't break sed)
  local run_folder_escaped
  local topas_escaped
  local python_escaped
  run_folder_escaped=$(escape_for_sed "$RUN_FOLDER_NAME")
  topas_escaped=$(escape_for_sed "$TOPAS_EXECUTABLE")
  python_escaped=$(escape_for_sed "$PYTHON_CMD")

  # -------- Step C: Patch submitLocally.sh --------
  # Replace whatever is between run/ and _"$DATE with the config run folder name
  sed -i.bak -e "s|/run/[^_]*_|/run/${run_folder_escaped}_|g" "$submit_script"
  # Replace the literal "topas" with the config executable:
  # - On the "time ..." line (e.g. "time topas $INFILE.txt" or "time python3 $INFILE.py topas")
  sed -i.bak -e "/time / s/topas/${topas_escaped}/g" "$submit_script"
  # - On the Python script line when there is no "time " (e.g. GvalueIRT_H: "python3 $INFILE.py topas")
  sed -i.bak -e "/\.py / s/topas/${topas_escaped}/g" "$submit_script"
  # Replace the Python command (any form: python, python2, python3, python3.10, etc.)
  sed -i.bak -e "s/python[0-9.]*/${python_escaped}/g" "$submit_script"
  rm -f "$submit_script.bak"

  # -------- Step D: Patch runMain.py for the two tests that use it --------
  # Replace the literal "topas" in os.system("topas RUN.txt") with the config executable
  if [[ "$test_name" == "Gvalue_LET-IRT" || "$test_name" == "Gvalue_LET-SBS" ]]; then
    if [[ -f "$runmain_script" ]]; then
      sed -i.bak -e "s/\"topas RUN\.txt\"/\"${topas_escaped} RUN.txt\"/g" "$runmain_script"
      rm -f "$runmain_script.bak"
    fi
  fi

  # -------- Step E: Run the test --------
  echo "Running test: $test_name (${num_runs} runs)"
  (cd "$test_dir" && tcsh submitLocally.sh "$num_runs") || true

  # -------- Step F: Put the original files back --------
  restore_all_saved_files
}

# -----------------------------------------------------------------------------
# Cleanup when the script exits or is interrupted (e.g. Ctrl+C).
# First we stop any background test jobs (so TOPAS and other child processes
# are not left running). Then we restore any patched files.
# -----------------------------------------------------------------------------
cleanup_on_exit() {
  # Stop any background jobs this script started (and their children, e.g. topas)
  for pid in $(jobs -p 2>/dev/null); do
    kill -TERM -"$pid" 2>/dev/null || true
  done
  wait 2>/dev/null || true
  restore_all_saved_files
}
trap cleanup_on_exit EXIT INT TERM

# =============================================================================
# Main: run the tests
# =============================================================================

if [[ "$DRY_RUN" == "yes" ]]; then
  echo "Dry run: config read successfully. Tests that would be run:"
  for t in "${TESTS[@]}"; do
    runs=$(get_runs_for_test "$t")
    echo "  - $t (runs=$runs)"
  done
  echo "max_parallel_jobs = $MAX_PARALLEL_JOBS"
  echo ""
  for t in "${TESTS[@]}"; do
    run_single_test "$t"
  done
  trap - EXIT INT TERM
  echo "Dry run finished (no files were changed, no tests were run)."
  exit 0
fi

# -----------------------------------------------------------------------------
# Before running real tests, check that the commands in the config exist.
# If they don't, we exit here so you don't start many tests that all fail
# with "command not found".
# -----------------------------------------------------------------------------
if ! command -v "$TOPAS_EXECUTABLE" &>/dev/null; then
  echo "Error: The command for topas_executable was not found: $TOPAS_EXECUTABLE" >&2
  echo "Install TOPAS or fix the name in batch_config.json, then try again." >&2
  exit 1
fi
if ! command -v "$PYTHON_CMD" &>/dev/null; then
  echo "Error: The command for python_cmd was not found: $PYTHON_CMD" >&2
  echo "Install that Python version or fix the name in batch_config.json, then try again." >&2
  exit 1
fi

# Run tests either one after another or several in parallel
if [[ "$MAX_PARALLEL_JOBS" -le 1 ]]; then
  # Run each test in order
  for t in "${TESTS[@]}"; do
    run_single_test "$t"
  done
else
  # Waves: run up to MAX_PARALLEL_JOBS tests at a time; when the whole batch finishes, start the next batch
  # Enable job control so that if you press Ctrl+C we can stop these background jobs (and their topas processes)
  set -m
  next_index=0
  while (( next_index < ${#TESTS[@]} )); do
    batch=()
    for (( i = 0; i < MAX_PARALLEL_JOBS && next_index < ${#TESTS[@]}; i++ )); do
      (run_single_test "${TESTS[next_index]}") &
      batch+=($!)
      ((next_index++))
    done
    wait ${batch[@]}
  done
fi

trap - EXIT INT TERM
echo "Batch run finished."
