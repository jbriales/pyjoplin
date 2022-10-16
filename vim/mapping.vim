"TODO: Do not use `function!`, instead refactor to plugin/ folder
function! GetJoplinTitle()
  return getline(2)
endfunction

function! GetJoplinHyperlink()
  return "[" . GetJoplinTitle() . "](" . "joplin://" . getline(1) . ")"
endfunction

nnoremap fl :let @+ = GetJoplinHyperlink()<CR>

" Same mapping but more conveniently located: yank-title
nnoremap fjt :let @+ = GetJoplinTitle()<CR>


" Check this note's content is synced with database
" Good for checking before closing to avoid losing work
" d is for Database
nnoremap <leader>d :execute "!pyjoplin-checkOpenAndDbSync.sh " . getline(1)<CR>


" Refactor note content for Joplin URLs
nnoremap <localleader>jr :w<CR>:execute "!refactor-joplinUrls.py '" . expand('%:p') . "'"<CR>


" alias for :E to edit code block in separate buffer
nmap <leader>e :E<CR>
