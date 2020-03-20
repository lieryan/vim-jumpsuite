let s:plugindir = expand('<sfile>:p:h:h')

command! -complete=file -nargs=? JumpSuite :cexpr system('python '. s:plugindir . '/jumpsuite/jumpsuite.py <args>')\|copen<Enter>
