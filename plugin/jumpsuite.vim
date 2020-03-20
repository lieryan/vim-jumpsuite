let s:plugindir = expand('<sfile>:p:h:h')
let s:jumpsuite_py = shellescape(s:plugindir . '/jumpsuite/jumpsuite.py')

let g:jumpsuite_filename = ''

function! s:jumpsuite(...)
    let filename = a:0 == 0 ? g:jumpsuite_filename : a:1
    if filename
        let filename=shellescape(filename)
    endif
    cexpr system('python '. s:jumpsuite_py . ' ' . filename)
    copen
endfunction

command! -complete=file -nargs=? JumpSuite call s:jumpsuite(<f-args>)
let &makeprg='python ' . s:jumpsuite_py . ' test-reports/test-report.xml'
