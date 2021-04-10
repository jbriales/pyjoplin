#!/bin/bash

set -e

# Ensure we are at the right level to open a new window
# if we come from a nested split container
if i3-cycle check_preview_split; then
  i3-msg focus parent
fi

urxvt256c -title "pyjoplin-fzf" -e pyjoplin-fzf.sh "$@"
