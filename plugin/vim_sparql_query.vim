let s:plugin_root_dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')

if executable('python3')
python3 << EOF
import sys
from os.path import normpath, join
import vim
plugin_root_dir = vim.eval('s:plugin_root_dir')
python_root_dir = normpath(join(plugin_root_dir, '..', 'python'))
sys.path.insert(0, python_root_dir)
import vsq
EOF
endif

function! s:get_visual_selection()
    " Why is this not a built-in Vim script function?!
    let [line_start, column_start] = getpos("'<")[1:2]
    let [line_end, column_end] = getpos("'>")[1:2]
    let lines = getline(line_start, line_end)
    if len(lines) == 0
        return ''
    endif
    let lines[-1] = lines[-1][: column_end - (&selection == 'inclusive' ? 1 : 2)]
    let lines[0] = lines[0][column_start - 1:]
    return join(lines, "\n")
endfunction

function! NewQuery()
    python3 vsq.new_query()
endfunction

function! BufferQuery()
    python3 vsq.buffer_query()
endfunction

command! -nargs=0 BufferQuery call BufferQuery()
command! -nargs=0 NewQuery call NewQuery()
