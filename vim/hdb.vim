
" Setup for completion in hdb notes
" TODO: Enable only for relevant hdb notes
" Enable YCM for markdown files
let g:ycm_filetype_blacklist = {}
" Add hdb.tags to tags file to consider in vim editor
set tags+=~/.cronsync/vim-tags/hdb.tags

" Edition bindings
execute "inoremap " . C_period . " <space>-><space>"
execute "inoremap " . K_period . " <space>-><space>"
