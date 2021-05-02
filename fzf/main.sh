#!/usr/bin/env bash

trap 'printf "\x1b[J"' EXIT

PATH_HISTORY="$HOME/.cache/ulauncher-joplin/history"
mkdir -p "$(dirname $PATH_HISTORY)"
LOGFILE=~/log/pyjoplin-fzf/$(date '+%Y_%m_%d-%H_%M_%S')
mkdir -p "$(dirname "$LOGFILE")"

######################
# Battery of actions
path_parent_dir="$(dirname $(realpath "${BASH_SOURCE[0]}"))"
source "$path_parent_dir/actions.sh"

function print_startup_entries ()(
  # NOTE: tac instead of cat to reverse order of history (newest is last in file)
  pyjoplin get $(tac $PATH_HISTORY 2>> "$LOGFILE")
)

function print_query_results ()(
  local query="$1:?"
  pyjoplin search "$query*" 2>> "$LOGFILE"
  # NOTE: Appending * for incomplete word search in query for pyjoplin
  # NOTE2: `*` should not be relevant with space-triggered search?
  # TODO: Debug why not always working?
)

function preview (){
  pyjoplin find-title {1} | highlight -O ansi --syntax md
}
cmd_preview="$(type preview | tail -n +3)"
# NOTE: Removing hacky suffix for passing preview title to search


# Source common utils for fzf-loop UI
source "$HOME/Code/common/fzf/fzf-loop.sh"


##############
# Main logic

# Call UI loop, with any given arguments as initial query
main "$*"

# HACK:
# Wait a bit before closing this window
# This enables keeping the new standalone created above
# in the same container level as this process
sleep 0.2s

exit 0