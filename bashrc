# To be sourced

path_parent_dir="$(realpath $(dirname "${BASH_SOURCE[0]}"))"

append_to_PATH_if_not_there "$path_parent_dir/bin"

# Install to user bin folder as centralized/stable location for binaries in PATH
ln -sf "$path_parent_dir/bin/"* "$HOME/.local/bin/"
