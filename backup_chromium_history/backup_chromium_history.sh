#!/usr/bin/env bash

set -euo pipefail

# Usage: backup_chromium_history [chromium_config_dir]
#
# For each profile, copies History to:
#   <backup_dir>/History-YYMMDD
#
# <backup_dir> is resolved in this order:
#   1. Per-profile entry in the map file (see CHROMIUM_HISTORY_BACKUP_MAP)
#   2. $CHROMIUM_HISTORY_BACKUP_ROOT/<profile_name>  if that env var is set
#   3. <profile_dir>/History-backups                 (default)
#
# Map file format (TAB or " | " separated; blank lines and # comments ok):
#   Profile 1	/mnt/backups/chromium-work
#   Profile 2	/home/me/elsewhere/personal-history

chromium_dpath="${1:-${CHROMIUM_CONFIG_DIR:-$HOME/.config/chromium}}"
backup_subdir="${CHROMIUM_HISTORY_BACKUP_SUBDIR:-History-backups}"
backup_root="${CHROMIUM_HISTORY_BACKUP_ROOT:-}"
backup_map="${CHROMIUM_HISTORY_BACKUP_MAP:-$HOME/.config/chromium_history_backup.map}"
date_suffix="$(date +%y%m%d)"

# Profiles that are ephemeral / not user browsing history
skip_profiles=(
    "Guest Profile"
    "System Profile"
)

is_skipped_profile() {
    local name="$1"
    local skip
    for skip in "${skip_profiles[@]}"; do
        if [ "$name" = "$skip" ]; then
            return 0
        fi
    done
    return 1
}

# Look up profile_name in the map file; print backup dir or nothing.
map_backup_dir() {
    local profile_name="$1"
    local line key val

    if [ ! -f "$backup_map" ]; then
        return 0
    fi

    while IFS= read -r line || [ -n "$line" ]; do
        # strip comments and surrounding whitespace
        line="${line%%#*}"
        line="${line#"${line%%[![:space:]]*}"}"
        line="${line%"${line##*[![:space:]]}"}"
        if [ -z "$line" ]; then
            continue
        fi

        if [[ "$line" == *"|"* ]]; then
            key="${line%%|*}"
            val="${line#*|}"
        else
            # TAB-separated (also accepts runs of whitespace)
            key="${line%%$'\t'*}"
            if [ "$key" = "$line" ]; then
                # fallback: first field / rest
                key="${line%% *}"
                val="${line#* }"
            else
                val="${line#*$'\t'}"
            fi
        fi
        key="${key%"${key##*[![:space:]]}"}"
        key="${key#"${key%%[![:space:]]*}"}"
        val="${val#"${val%%[![:space:]]*}"}"
        val="${val%"${val##*[![:space:]]}"}"

        if [ "$key" = "$profile_name" ] && [ -n "$val" ]; then
            printf '%s\n' "$val"
            return 0
        fi
    done <"$backup_map"
}

backup_dir_for_profile() {
    local profile_name="$1"
    local profile_dir="$2"
    local mapped

    mapped="$(map_backup_dir "$profile_name")"
    if [ -n "$mapped" ]; then
        printf '%s\n' "$mapped"
        return 0
    fi

    if [ -n "$backup_root" ]; then
        printf '%s\n' "$backup_root/$profile_name"
        return 0
    fi

    printf '%s\n' "${profile_dir}${backup_subdir}"
}

# Consistent snapshot of a SQLite DB that may be open (Chromium holds a lock).
copy_history_db() {
    local src="$1"
    local dst="$2"
    mkdir -p "$(dirname "$dst")"
    if command -v sqlite3 >/dev/null 2>&1; then
        if sqlite3 "$src" ".backup '$dst'" 2>/dev/null; then
            return 0
        fi
    fi
    # Fallback if sqlite3 is missing or backup fails
    cp -- "$src" "$dst"
}

if [ ! -d "$chromium_dpath" ]; then
    echo "chromium config dir not found: $chromium_dpath" >&2
    exit 1
fi

copied_any=0
shopt -s nullglob
for profile_dir in "$chromium_dpath"/*/; do
    profile_name="$(basename "$profile_dir")"
    history_src="${profile_dir}History"

    if [ ! -f "$history_src" ]; then
        continue
    fi
    if is_skipped_profile "$profile_name"; then
        continue
    fi

    backup_dir="$(backup_dir_for_profile "$profile_name" "$profile_dir")"
    history_dst="${backup_dir}/History-${date_suffix}"
    copy_history_db "$history_src" "$history_dst"
    echo "$history_dst"
    copied_any=1
done
shopt -u nullglob

if [ "$copied_any" -eq 0 ]; then
    echo "no chromium profile History files found under $chromium_dpath" >&2
    exit 1
fi
