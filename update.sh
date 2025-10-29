#!/bin/sh

# Standard location for pacman log
PACMAN_LOG="/var/log/pacman.log"
# Standard locations for commands
CHECKUPDATES_CMD="/usr/bin/checkupdates"
YAY_CMD="/usr/bin/yay"
PACMAN_CMD="/usr/bin/pacman"

# --- Function to check if a command exists ---
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# --- Function to get pending official updates ---
get_pending_pacman() {
    if command_exists "$CHECKUPDATES_CMD"; then
        "$CHECKUPDATES_CMD"
    else
        echo "Error: 'checkupdates' command not found." >&2
        echo "Try installing 'pacman-contrib': sudo pacman -S pacman-contrib" >&2
        exit 1
    fi
}

# --- Function to get pending AUR updates ---
get_pending_aur() {
    if command_exists "$YAY_CMD"; then
        "$YAY_CMD" -Qua
    else
        echo "Error: 'yay' command not found." >&2
        echo "Please install an AUR helper like yay." >&2
        exit 1
    fi
}

# --- Function to get update sizes ---
get_update_sizes() {
    printf "Calculating update sizes...\n"
    # Run pacman sync, but pipe "n" to cancel the actual update
    # Capture the output to parse the size summary
    # Use POSIX redirection: >/dev/null 2>&1
    size_output=$(echo "n" | sudo "$PACMAN_CMD" -Syu >/dev/null 2>&1)

    # Extract the size lines using grep
    download_size=$(echo "$size_output" | grep "Total Download Size:")
    installed_size=$(echo "$size_output" | grep "Total Installed Size:")
    net_size=$(echo "$size_output" | grep "Net Upgrade Size:")

    # Use POSIX test `[ -n ... ]` instead of `[[ -n ... ]]`
    if [ -n "$download_size" ]; then
        echo "$download_size"
        echo "$installed_size"
        echo "$net_size"
    else
        echo "Could not determine update sizes (maybe no updates or an error occurred)."
    fi
}

# --- Function to get updated packages from log ---
# Takes start timestamp (seconds since epoch) as argument
get_updated_packages() {
    start_timestamp=$1
    printf "Packages updated in this run:\n"

    # awk is POSIX compliant, mktime is a common extension (present in gawk/nawk)
    awk -v start="$start_timestamp" '
    BEGIN { FS="[][]"; } # Set field separators to [ or ]
    {
        # Extract the timestamp part (e.g., 2025-10-22T20:30:00+0200)
        log_time_str = $2;
        # Convert it to the format mktime expects: "YYYY MM DD HH MM SS"
        gsub(/[-T:+]/, " ", log_time_str);
        # Get seconds since epoch for the log entry
        log_timestamp = mktime(log_time_str);

        # Check if log entry is after script start and contains upgrade/install
        # Use POSIX compatible check for existence of ALPM and upgraded/installed
        if (log_timestamp > start && ($0 ~ /ALPM]/ && ($0 ~ /upgraded/ || $0 ~ /installed/))) {
            # Extract package name and version info (usually 5th space-separated field in $3)
            split($3, parts, " ");
            package_info = parts[5];
            # Print only package name and version transition if available
            # Check POSIX compatible way
            if (parts[6] = "(" && parts[8] = "->") {
                 # Format: package (old -> new)
                 printf " - %s %s %s %s\n", package_info, parts[6], parts[7], parts[8], parts[9]
            } else if (substr(parts[6], 1, 1) = "(") {
                 # Format: package (version) - check if 6th field starts with (
                 printf " - %s %s\n", package_info, parts[6]
            } else {
                 # Fallback print if format is unexpected
                 printf " - %s (unknown format: %s)\n", package_info, $3
            }
        }
    }' "$PACMAN_LOG"
}

# --- Main Script ---

printf "Checking for updates...\n"

# Check required commands first
if ! command_exists "sudo"; then
    echo "Error: 'sudo' command not found. Please install it." >&2
    exit 1
fi
if ! command_exists "$PACMAN_CMD"; then
    echo "Error: 'pacman' command not found." >&2
    exit 1
fi
# get_pending_* functions will check for checkupdates and yay

# Get and store pending updates
pending_pacman=$(get_pending_pacman)
pending_aur=$(get_pending_aur)

# Display pending updates
# Use POSIX test `[ -n ... ]`
if [ -n "$pending_pacman" ]; then
    printf -- "------------------------------------\n"
    printf "Official Packages to Update:\n"
    echo "$pending_pacman"
    printf -- "------------------------------------\n"
else
    printf "No official package updates pending.\n"
fi

if [ -n "$pending_aur" ]; then
    printf -- "------------------------------------\n"
    printf "AUR Packages to Update:\n"
    echo "$pending_aur"
    printf -- "------------------------------------\n"
else
    printf "No AUR package updates pending.\n"
fi

# If there are any updates, calculate sizes and run update
# Use POSIX test `[ ... -o ... ]` for OR
if [ -n "$pending_pacman" -o -n "$pending_aur" ]; then
    printf "\n"
    get_update_sizes
    printf "\n"

    # Get the timestamp *before* starting the actual update
    start_time_seconds=$(date +%s)

    printf "Starting updates...\n"
    printf -- "------------------------------------\n"

    # Run official updates
    sudo "$PACMAN_CMD" -Syu --noconfirm
    if [ $? -ne 0 ]; then
        echo "Error during pacman update."
        exit 1
    fi

    printf "\n"
    printf -- "------------------------------------\n"
    printf "Updating AUR packages...\n"
    printf -- "--- Please review PKGBUILD changes ---\n"
    # Run AUR updates (safer without --noconfirm)
    "$YAY_CMD" -Sua
    if [ $? -ne 0 ]; then
        echo "Error during yay update."
        exit 1
    fi
    printf -- "------------------------------------\n"

    printf "\nUpdate process finished.\n\n"

    # Get and display the list of updated packages from the log
    get_updated_packages "$start_time_seconds"

else
    printf "System is already up to date. ✅\n"
fi

printf "\nSystem fully updated.\n"

exit 0
