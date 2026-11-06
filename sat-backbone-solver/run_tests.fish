#!/usr/bin/env fish

set -l instance_dir test_instances
set -l expected_dir test_solutions
set -l solver_script backbone_szyjut_12634056.py

if not test -d "$instance_dir"
    echo "Missing directory: $instance_dir" >&2
    exit 1
end

if not test -d "$expected_dir"
    echo "Missing directory: $expected_dir" >&2
    exit 1
end

if not test -f "$solver_script"
    echo "Missing solver script: $solver_script" >&2
    exit 1
end

set -l tmp_dir (mktemp -d)
if test $status -ne 0
    echo "Failed to create temporary directory" >&2
    exit 1
end

set -l pass_count 0
set -l fail_count 0

for cnf in $instance_dir/*.cnf
    set -l base (string replace -r '\.cnf$' '' (basename "$cnf"))
    set -l expected "$expected_dir/$base.out"
    set -l actual "$tmp_dir/$base.out"

    if not test -f "$expected"
        echo "[FAIL] $base (missing expected output: $expected)"
        set fail_count (math $fail_count + 1)
        continue
    end

    uv run python "$solver_script" "$cnf" > "$actual"
    if test $status -ne 0
        echo "[FAIL] $base (solver execution failed)"
        set fail_count (math $fail_count + 1)
        continue
    end

    diff -u "$expected" "$actual" > /dev/null
    if test $status -eq 0
        echo "[PASS] $base"
        set pass_count (math $pass_count + 1)
    else
        echo "[FAIL] $base"
        diff -u "$expected" "$actual"; or true
        set fail_count (math $fail_count + 1)
    end
end

rm -rf "$tmp_dir"

echo
printf "Summary: %d passed, %d failed\n" $pass_count $fail_count

if test $fail_count -ne 0
    exit 1
end
