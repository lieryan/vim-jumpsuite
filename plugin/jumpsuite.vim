let s:plugindir = expand('<sfile>:p:h:h')

let g:jumpsuite_filename = ''

function! s:jumpsuite(...)
    let filename = a:0 == 0 ? g:jumpsuite_filename : a:1
    if filename
        let filename=shellescape(filename)
    endif
    cexpr system('python '. shellescape(s:plugindir . '/jumpsuite/jumpsuite.py') . ' ' . filename)
    copen
endfunction

command! -complete=file -nargs=? JumpSuite call s:jumpsuite(<f-args>)
