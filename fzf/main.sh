#!/usr/bin/env bash
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


######################
# Battery of actions

# Define list of potential actions a-priori
# See [bash - case dispatcher](joplin://f202c2133eea4399b27806254d748b52)
# NOTE:
# These functions have potential side effects like:
# - update `query` variable
# - exit script
# Because of these are NOT subshell-functions
declare -A map_key_action

# Just continue search
# NOTE: The space has to be inserted again because the --expect in fzf intercepts it
map_key_action[space]=add_space_to_query
function add_space_to_query (){
  query="$query ";
}

map_key_action[ctrl-alt-n]=create_new_note
function create_new_note (){
  # Create new note and open (w/o closing)

  words=($query)
  # Check nb keyword (first)
  case "$(echo ${words[0]} | tr '[:upper:]' '[:lower:]')" in
    "#fb") query="${words[@]:1}"; nb="fb";;
    *) nb="personal";;
  esac
  # Check nb keyword (last)
  #case "$(echo ${words[-1]} | tr '[:upper:]' '[:lower:]')" in
  #  "#fb") query="${words[@]::${#words[@]}-1}"; nb="fb";;
  #  *) nb="personal";;
  #esac
  nohup pyjoplin new_and_edit --notebook "$nb" "$query" &
  # Add opened file to history
  sleep 0.3s  # some delay to ensure 
  append_to_history $(pyjoplin find-title "$query" | head -n 1)
}

map_key_action[ctrl-n]=create_new_note_and_stop_fzf
function create_new_note_and_stop_fzf (){
  create_new_note
  return 10
}

map_key_action[ctrl-p]=copy_note_name
function copy_note_name (){
  title="${result% @@@*}"  # Cleanup hacky addition in result
  $HOME/.dotfiles/bin/notify-send-and-xclip.sh "$title"
}

map_key_action[ctrl-l]=copy_note_hyperlink
function copy_note_hyperlink (){
  # Copy note hyperlink
  title="${result% @@@*}"  # Cleanup hacky addition in result
  uid="$(pyjoplin find-title "$title" | head -1)"
  hyperlink="[$title](joplin://$uid)"
  $HOME/.dotfiles/bin/notify-send-and-xclip.sh "$hyperlink"
}

map_key_action[ctrl-s]=run_imfeelinglucky
function run_imfeelinglucky (){
  # Run 'Imfeelinglucky' on selection
  title="${result% @@@*}"  # Cleanup hacky addition in result
  uid=$(pyjoplin find-title "$title" | head -n 1)
  pyjoplin imfeelinglucky $uid
}

map_key_action[ctrl-v]=append_xclip_to_query
function append_xclip_to_query (){
  # Append clipboard content to query for search
  # This is a workaround for https://github.com/junegunn/fzf/issues/1803
  query="${query}$(xclip -selection clipboard -o)"
  continue
}

map_key_action[ctrl-t]=copy_note_title
function copy_note_title (){
  # Copy note title
  # Using ctrl-t and not ctrl-0 because ctrl-NR not available
  title="${result% @@@*}"  # Cleanup hacky addition in result
  $HOME/.dotfiles/bin/notify-send-and-xclip.sh "$title"
}

map_key_action[ctrl-y]=refresh_theme
function refresh_theme (){
  theme-refresh-terminal
}

map_key_action[alt-enter]=open_note
function open_note (){
  # Open note
  title="${result% @@@*}"  # Cleanup hacky addition in result
  if [ -z "$title" ]; then
    notify-send "ERROR pyjoplin-fzf" \
      'Tried to open note with empty title'
  else
    nohup pyjoplin edit-by-title "$title" &
    # Add opened file to history
    append_to_history $(pyjoplin find-title $title | head -n 1)
    [[ "$key" == *"alt"* ]] || return 10
  fi
}

map_key_action[enter]=open_note_and_stop_fzf
function open_note_and_stop_fzf (){
  open_note
  return 10
}

map_key_action[ctrl-h]=print_help
function print_help (){
  echo "Available actions:"
  echo
  for key in "${!map_key_action[@]}"; do
    val="${map_key_action[$key]}"
    echo -e "[$key]\t-> $val"
  done
  echo

  read -p 'Press Enter to continue'
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
