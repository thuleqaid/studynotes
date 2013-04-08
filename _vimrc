set nocompatible
set enc=utf-8
set fileencodings=ucs-bom,utf-8,sjis
set fileformat=unix
set number
set iminsert=0
set imsearch=0
" => temporary dir
" backup
set bk
set bdir=$HOME/.vimtemp
" swap
set dir=$HOME/.vimtemp
" undo-tree
set undofile
set undodir=$HOME/.vimtemp
" => temporary dir

" => General view
"WinPos
"winpos 0 0
set lines=40 columns=110
set guioptions-=T
set list
set listchars=tab:>-,trail:-
set number
" hightlight trailing spaces
highlight WhitespaceEOL ctermbg=red guibg=red
match WhitespaceEOL /\s\+$/
set ignorecase
set magic
set hls
set is

"convert tab to spaces
"set expandtab
set shiftwidth=4
set tabstop=4
set smarttab
set lbr
set tw=500
set ai
set si
set nowrap

" => General view

" => Window Layout

"NERDTree
let g:NERDTreeMapJumpPrevSibling='<C-[>'
let g:NERDTreeMapJumpNextSibling='<C-]>'
"noremap <silent> <F10> :NERDTree D:\<CR>

" MiniBufExplorer
" copy minibufexpl.vim into ~/.vim/plugin
" In MiniBufExplorer window
"   <Tab> <S-Tab> : jumps among buffer names
"   <Enter>       : open current buffer
"   <d>           : remove current buffer
" use <C-h,j,k,l> to switch sub windows
let g:miniBufExplMapWindowNavVim = 1
" use <C-arrow> to switch sub windows
"let g:miniBufExplMapWindowNavArrow = 1
set hidden

"TagList
"set tags=w:/tags
let Tlist_Show_One_File=1
let Tlist_Exit_OnlyWindow=1
"let Tlist_File_Fold_Auto_Close=1
let Tlist_Show_Menu=1
let Tlist_Use_Right_Window=1

nmap <Leader>wl :NERDTreeToggle<CR>
nmap <Leader>wr :TlistToggle<CR>
nmap <Leader>wa :NERDTree<CR>:TlistOpen<CR>
nmap <Leader>wc :NERDTreeClose<CR>:TlistClose<CR>

"snipMate's Trigger Completion
let g:acp_behaviorSnipmateLength=1

" vimwiki
let g:vimwiki_use_mouse = 1

let wiki_1 = {}
let wiki_1.path = '~/public_html/vimwiki/'
let wiki_1.path_html = '~/public_html/vimwiki/html/'
let wiki_1.html_template = '~/public_html/vimwiki/template/header.tpl'
let wiki_1.auto_export = 1
let wiki_1.index = 'main'

let g:vimwiki_list = [wiki_1]

"let g:vimwiki_list = [{'path': '~/vimwiki/',
"\ 'path_html': '~/vimwiki/html/',
"\ 'html_header': '~/vimwiki/template/header.tpl',
"\ 'auto_export': 1}]

"CScope
"nmap <C-\>a :cs add w:\cscope.out w:\<CR>
nmap <C-\>z :STag 
nmap <C-\>Z :GTag 
nmap <C-\>s mZ:cs find s <C-R>=expand("<cword>")<CR><CR>	
nmap <C-\>g mZ:cs find g <C-R>=expand("<cword>")<CR><CR>	
nmap <C-\>c mZ:cs find c <C-R>=expand("<cword>")<CR><CR>	
nmap <C-\>t mZ:cs find t <C-R>=expand("<cword>")<CR><CR>	
nmap <C-\>e mZ:cs find e <C-R>=expand("<cword>")<CR><CR>	
nmap <C-\>f mZ:cs find f <C-R>=expand("<cfile>")<CR><CR>	
nmap <C-\>i mZ:cs find i ^<C-R>=expand("<cfile>")<CR>$<CR>
nmap <C-\>d mZ:cs find d <C-R>=expand("<cword>")<CR><CR>	
nmap <C-\>S mY:cs find s 
nmap <C-\>G mY:cs find g 
nmap <C-\>C mY:cs find c 
nmap <C-\>T mY:cs find t 
nmap <C-\>E mY:cs find e 
nmap <C-\>F mY:cs find f 
nmap <C-\>I mY:cs find i 
nmap <C-\>D mY:cs find d 
set cscopequickfix=s-,g-,f-,c-,d-,i-,t-,e-
set timeoutlen=4000
set ttimeout 
set ttimeoutlen=100

function! s:inputDir(name)
    let dir = a:name ==# '' ? getcwd() : a:name
    "hack to get an absolute path if a relative path is given
    if has("win16") || has("win32") || has("win64")
        let sep = '\'
    else
        let sep = '/'
    endif
    if dir =~ '^\.'
        let dir = getcwd() . sep . dir
    endif
    let dir = resolve(dir)
    if strlen(dir)>strridx(dir,sep)+1
        let dir=dir . sep
    endif
    exec ':chdir '. dir
    return dir
endfunction
function! s:genTag(name)
    let dir=s:inputDir(a:name)
    "exec ':chdir '. dir
    exec '!ctags -R'
    "exec '!cscope -Rbkq'
    exec '!cscope -Rbc'
    ""set tags
    exec ':set tags=' . dir  . 'tags'
    exec ':cs add ' . dir . 'cscope.out'
endfunction
function! s:setTag(name)
    let dir=s:inputDir(a:name)
    "exec ':chdir '. dir
    if filereadable(dir.'tags')
        exec ':set tags=' . dir  . 'tags'
    else
        echo 'Not found: '. dir . 'tags'
    endif
    if filereadable(dir.'cscope.out')
        exec ':cs add ' . dir . 'cscope.out'
    else
        echo 'Not found: '. dir . 'cscope.out'
    endif
endfunction

command! -n=? -complete=dir -bar GTag :call s:genTag('<args>')
command! -n=? -complete=dir -bar STag :call s:setTag('<args>')

map <F5> "+y
map <F6> "+p

exe 'menu VimIDE.Generate\ Tags\.\.\.<tab><C-\>Z		<C-\>Z'
exe 'menu VimIDE.Set\ Tags\.\.\.<tab><C-\>Z		<C-\>z'
exe 'menu VimIDE.-SEP1-		<Nop>'
exe 'menu VimIDE.WindowManager<tab>\\wm		<Leader>wm'
exe 'menu VimIDE.-SEP2-		<Nop>'
exe 'menu VimIDE.Symbol.Current<tab><C-\>s		<C-\>s'
exe 'menu VimIDE.Symbol.Specified\.\.\.<tab><C-\>S		<C-\>S'
exe 'menu VimIDE.Definition.Current<tab><C-\>g		<C-\>g'
exe 'menu VimIDE.Definition.Specified\.\.\.<tab><C-\>G		<C-\>G'
exe 'menu VimIDE.CalledBy.Current<tab><C-\>d		<C-\>d'
exe 'menu VimIDE.CalledBy.Specified\.\.\.<tab><C-\>D		<C-\>D'
exe 'menu VimIDE.Calling.Current<tab><C-\>c		<C-\>c'
exe 'menu VimIDE.Calling.Specified\.\.\.<tab><C-\>C		<C-\>C'
exe 'menu VimIDE.Text.Current<tab><C-\>t		<C-\>t'
exe 'menu VimIDE.Text.Specified\.\.\.<tab><C-\>T		<C-\>T'
exe 'menu VimIDE.Egrep.Current<tab><C-\>e		<C-\>e'
exe 'menu VimIDE.Egrep.Specified\.\.\.<tab><C-\>E		<C-\>E'
exe 'menu VimIDE.File.Current<tab><C-\>f		<C-\>f'
exe 'menu VimIDE.File.Specified\.\.\.<tab><C-\>F		<C-\>F'
exe 'menu VimIDE.Including.Current<tab><C-\>i		<C-\>i'
exe 'menu VimIDE.Including.Specified\.\.\.<tab><C-\>I		<C-\>I'
exe 'menu VimIDE.-SEP3-		<Nop>'
exe 'menu VimIDE.Result.Open<tab>:cw		:cw<CR>'
exe 'menu VimIDE.Result.Close<tab>:ccl		:ccl<CR>'

