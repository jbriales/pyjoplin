#!/usr/bin/env bash

######################
# Battery of actions
path_parent_dir="$(dirname $(realpath "${BASH_SOURCE[0]}"))"
source "$path_parent_dir/actions.sh"


PATH_HISTORY="$HOME/.cache/ulauncher-joplin/history"
mkdir -p "$(dirname $PATH_HISTORY)"
LOGFILE=~/log/pyjoplin-fzf/$(date '+%Y_%m_%d-%H_%M_%S')
mkdir -p "$(dirname "$LOGFILE")"

# Print to stdout the search results
# based on current query (given as input)
function search () {
  local query
  if [ -z "$1" ] || [ "$1" = " " ]; then
    # NOTE: tac instead of cat to reverse order of history (newest is last in file)
    pyjoplin get $(tac $PATH_HISTORY 2>> "$LOGFILE")
  else
    query="$1"
    pyjoplin search "$query*" 2>> "$LOGFILE"
    # NOTE: Appending * for incomplete word search in query for pyjoplin
    # TODO: Debug why not always working?
  fi
}

# TODO: Refactor out common logic for fzf-based interface from here?
function filter() {
  local query="$1"
  # NOTE:
  # Use full path to avoid issues in i3
  # with this being in a non-standard bin path
  fzf_expected_keys="$(echo "${!map_key_action[@]}" | xargs printf "%s,")"
  fzf_expected_keys="${fzf_expected_keys::-1}"  # remove trailing ','
  $HOME/.fzf/bin/fzf --layout=reverse --ansi \
    --expect="$fzf_expected_keys" \
    --tiebreak=begin \
    --query="$query" --print-query \
    --height 100% \
    --preview 'pyjoplin find-title $(echo {} | sed -e "s| @@@.*||") | highlight -O ansi --syntax md'
  # NOTE: Removing hacky suffix for passing preview title to search
}

# Similar logic to that in Code/python/ulauncher-joplin/history.py (append)
append_to_history() {
  local MAX_NUM_ENTRIES_MINUS_ONE=29
  # NOTE: Currently if opened via ulauncher (15) will crop a longer list?
  local uid=$1
  if [[ -e "$PATH_HISTORY" ]]; then
    # Remove uid if it already exists
    sed -i "/$uid/c\\" $PATH_HISTORY
    # Update history file with newest MAX_NUM_ENTRIES_MINUS_ONE elems and new one
    # NOTE: It seems tail has to be redirected to a different file or result is empty (pipe behavior?)
    tail -n $MAX_NUM_ENTRIES_MINUS_ONE $PATH_HISTORY > $PATH_HISTORY.temp
  fi
  # Add latest id
  echo $uid >> $PATH_HISTORY.temp
  mv $PATH_HISTORY.temp $PATH_HISTORY
}

##############
# Main logic
trap 'printf "\x1b[J"' EXIT

query="$*"
while true; do
  output=$(search "$query" | xargs --no-run-if-empty -d '\n' printf  "%s @@@ $query\n" | filter "$query")
  status=$?
  [ $status -eq 130 ] || [ $status -eq 2 ] && exit $status

  mapfile -t lines <<< "$output"
  query="${lines[0]}"
  key="${lines[1]}"
  result="${lines[2]}"

  if ! [ ${map_key_action[$key]} ]; then
    notify-send 'pyjoplin-fzf ERROR' "Unexpected key $key"
  else
    # Run corresponding action
    ${map_key_action[$key]}
    # Check return code and exit loop if special code 10
    case $? in
      10) break;;  # controlled exit
    esac
  fi
done

# Wait a bit before closing this window
# This enables keeping the new standalone created above
# in the same container level as this process
sleep 0.2s
exit 0
