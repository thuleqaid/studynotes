" Name    : ModifyTag
" Object  : add modify history for c/c++ source
" Author  :
" Date    : 2015/02/17
" Version : v0.4
" ChangeLog
" v0.4 2015/02/17
"   add s:DenyChanges()
" v0.3 2015/02/17
"   add s:ApproveChanges()
" v0.2 2015/02/17
"   add s:SumModifiedLines()
"   add s:GenerateCommand()

" Usage :
" 1. use <Leader>ta/tc/td when coding
" 2. use <Leader>tt to generate script and bash command
" 3. open result.txt after run step2's command, use <Leader>ts to summarize the result
" Manual Command :
" 1. use <Leader>tu to update lines of modified code in the current file
" 2. use <Leader>tm to count selected lines
" CodeReview Command :
" 1. use <Leader>to to approve selected lines
" 2. use <Leader>tn to approve selected lines

" Paramater I
" this part should be unique for every project
let s:tag_key1   = 'abcd' "must
let s:tag_key2   = 'hijk' "optional
let s:tag_key3   = 'wxyz' "optional
let s:tag_reason = 'xxxyyyzzz' "default modify-reason
let s:tag_co     = '' "compile option, valid only if s:tag_mode == 1
let s:tag_allowr = 1 "0: without reason line, 1: with reason line
" Paramater II
" this part should be unique for every people
let s:tag_user   = 'anonymous'
" Paramater III
" this part should be same for every people
let s:tag_start  = '=================start=================='
let s:tag_end    = '==================end==================='
let s:cmt_start  = '/* '
let s:cmt_end    = ' */'
let s:tag_mode   = 0  "0: [#if] for chg and del, 1:[#if] for add, chg and del
let s:tag_timef  = "%Y/%m/%d"
let s:tag_sep    = ','
let s:ptn_escape = '/*[]()'
" define command
command! -n=0 -bar ModifyTagUpdateLines :call s:CalculateModifiedLines()
command! -n=0 -rang=% -bar ModifyTagManualCount :<line1>,<line2>call s:CountLines()
command! -n=0 -rang -bar ModifyTagAddSource :call s:ModifyTag('add',<line1>,<line2>)
command! -n=0 -rang -bar ModifyTagChgSource :call s:ModifyTag('chg',<line1>,<line2>)
command! -n=0 -rang -bar ModifyTagDelSource :call s:ModifyTag('del',<line1>,<line2>)
command! -n=0 -bar ModifyTagSumLines :call s:SumModifiedLines()
command! -n=0 -bar ModifyTagTerminalCmd :call s:GenerateCommand()
command! -n=0 -rang -bar ModifyTagOKChanges :<line1>,<line2>call s:ApproveChanges()
command! -n=0 -rang -bar ModifyTagNGChanges :<line1>,<line2>call s:DenyChanges()
" key-binding
nmap <Leader>ta :ModifyTagAddSource<CR>
vmap <Leader>tc :ModifyTagChgSource<CR>
vmap <Leader>td :ModifyTagDelSource<CR>
nmap <Leader>tu :ModifyTagUpdateLines<CR>
vmap <Leader>tm :ModifyTagManualCount<CR>
nmap <Leader>ts :ModifyTagSumLines<CR>
nmap <Leader>tt :ModifyTagTerminalCmd<CR>
nmap <Leader>to :ModifyTagOKChanges<CR>
vmap <Leader>to :ModifyTagOKChanges<CR>
nmap <Leader>tn :ModifyTagNGChanges<CR>
vmap <Leader>tn :ModifyTagNGChanges<CR>

function! s:ApproveChanges() range
	let l:pos = s:tellPos(a:firstline, a:lastline)
	let l:i   = len(l:pos) - 5
	while l:i >= 0
		let l:type  = get(l:pos,l:i)
		let l:line1 = get(l:pos,l:i+1)
		let l:line2 = get(l:pos,l:i+2)
		let l:line3 = get(l:pos,l:i+3)
		let l:line4 = get(l:pos,l:i+4)
		let l:i     = l:i - 5
		if l:type == 'add'
			call s:approveAddBlock(l:line1, l:line2, l:line3, l:line4)
		elseif l:type == 'chg'
			call s:approveChgBlock(l:line1, l:line2, l:line3, l:line4)
		elseif l:type == 'del'
			call s:approveDelBlock(l:line1, l:line2, l:line3, l:line4)
		endif
	endwhile
endfunction
function! s:DenyChanges() range
	let l:pos = s:tellPos(a:firstline, a:lastline)
	let l:i   = len(l:pos) - 5
	while l:i >= 0
		let l:type  = get(l:pos,l:i)
		let l:line1 = get(l:pos,l:i+1)
		let l:line2 = get(l:pos,l:i+2)
		let l:line3 = get(l:pos,l:i+3)
		let l:line4 = get(l:pos,l:i+4)
		let l:i     = l:i - 5
		if l:type == 'add'
			call s:denyAddBlock(l:line1, l:line2, l:line3, l:line4)
		elseif l:type == 'chg'
			call s:denyChgBlock(l:line1, l:line2, l:line3, l:line4)
		elseif l:type == 'del'
			call s:denyDelBlock(l:line1, l:line2, l:line3, l:line4)
		endif
	endwhile
endfunction
function! s:GenerateCommand()
	let l:keyword  = escape(s:constructKeyword(), s:ptn_escape)
	let l:command  = ":silent! echo find . -regex '.*\\.\\(c\\|h\\)' | xargs -i sh -c \"vim -s mtupdate.vim {};grep -Hn '" . l:keyword ."' {} >> result.txt\""
	call append(line('$'), ':silent! echo Save this file as "mtupdate.vim"')
	call append(line('$'), ':silent! echo Terminal Command')
	call append(line('$'), l:command)
	call append(line('$'), ':ModifyTagUpdateLines')
	call append(line('$'), ':wq')
endfunction
function! s:SumModifiedLines()
	let l:keyword  = s:constructKeyword()
	let l:lastline = line('$')
	let l:total1   = 0
	let l:total2   = 0
	let l:total3   = 0
	let l:total4   = 0
	let l:total5   = 0
	let l:total6   = 0
	let l:total7   = 0
	let l:total8   = 0
	let l:i        = 1
	call append(line('$'), "File\tLineNo\tADD_Total\tADD_Code\tCHG_Total_Old\tCHG_Code_Old\tCHG_Total_New\tCHG_Code_New\tDEL_Total\tDEL_Code\tAuthor\tDate")
	while l:i <= l:lastline
		let l:text = getline(l:i)
		if stridx(l:text, l:keyword) > 0
			let l:text = substitute(l:text, escape(s:cmt_start, s:ptn_escape), '', '')
			let l:text = substitute(l:text, escape(s:cmt_end, s:ptn_escape), '', '')
			let l:text = substitute(l:text, escape(s:tag_sep . l:keyword . s:tag_sep, s:ptn_escape), ':', '')
			" add ':' between author and date
			let l:text = substitute(l:text, ' ', ':', '')
			let l:text = substitute(l:text, '\CADD\[\(\d*\)\]\[\(\d*\)\]', '\1:\2::::::', '')
			let l:text = substitute(l:text, '\CCHG\[\(\d*\)\]\[\(\d*\)\]_\[\(\d*\)\]\[\(\d*\)\]', '::\1:\2:\3:\4::', '')
			let l:text = substitute(l:text, '\CDEL\[\(\d*\)\]\[\(\d*\)\]', '::::::\1:\2', '')
			" sum lines
			let l:pos1 = match(l:text, ':', 0, 2)
			let l:pos2 = match(l:text, ':', l:pos1+1, 8)
			let l:curlines = split(strpart(l:text, l:pos1+1, l:pos2-l:pos1), ':', 1)
			let l:total1 = l:total1 + str2nr(get(l:curlines, 0))
			let l:total2 = l:total2 + str2nr(get(l:curlines, 1))
			let l:total3 = l:total3 + str2nr(get(l:curlines, 2))
			let l:total4 = l:total4 + str2nr(get(l:curlines, 3))
			let l:total5 = l:total5 + str2nr(get(l:curlines, 4))
			let l:total6 = l:total6 + str2nr(get(l:curlines, 5))
			let l:total7 = l:total7 + str2nr(get(l:curlines, 6))
			let l:total8 = l:total8 + str2nr(get(l:curlines, 7))
			" change ':' to '\t'
			let l:text = substitute(l:text, ':', '\t', 'g')
			call append(line('$'), l:text)
		endif
		let l:i = l:i + 1
	endwhile
	call append(line('$'), "Total\t\t" . l:total1 . "\t" . l:total2 . "\t" . l:total3 . "\t" . l:total4 . "\t" . l:total5 . "\t" . l:total6 . "\t" . l:total7 . "\t" . l:total8)
endfunction
function! s:CountLines() range
	let l:cnt = s:countSourceLines(a:firstline, a:lastline)
	call setpos('.', [0, a:lastline, 1, 0])
	echo l:cnt
endfunction
function! s:CalculateModifiedLines()
	let l:cntlist = s:countList()
	" modify source lines
	let l:i = 0
	while l:i < len(l:cntlist)
		let l:type  = get(l:cntlist,l:i)
		let l:line0 = get(l:cntlist,l:i+1)
		let l:line1 = get(l:cntlist,l:i+2)
		let l:line2 = get(l:cntlist,l:i+3)
		let l:i     = l:i + 4
		if l:type == 'add'
			let l:rep = 'ADD[' . l:line1 . '][' . l:line2 . ']'
			let l:res = substitute(getline(l:line0), '\CADD\[\d*\]\[\d*\]', l:rep, "")
			call setline(l:line0, l:res)
		elseif l:type == 'chg'
			let l:line3 = get(l:cntlist,l:i)
			let l:line4 = get(l:cntlist,l:i+1)
			let l:i     = l:i + 2
			let l:rep   = 'CHG[' . l:line1 . '][' . l:line2 . ']_[' . l:line3 . '][' . l:line4 . ']'
			let l:res = substitute(getline(l:line0), '\CCHG\[\d*\]\[\d*\]_\[\d*\]\[\d*\]', l:rep, "")
			call setline(l:line0, l:res)
		elseif l:type == 'del'
			let l:rep = 'DEL[' . l:line1 . '][' . l:line2 . ']'
			let l:res = substitute(getline(l:line0), '\CDEL\[\d*\]\[\d*\]', l:rep, "")
			call setline(l:line0, l:res)
		endif
	endwhile
endfunction

function! s:countList()
	let l:rangelist = s:modifyList()
	let l:cntlist   = []
	" count source lines
	let l:i = 0
	while l:i < len(l:rangelist)
		let l:type  = get(l:rangelist,l:i)
		let l:line1 = get(l:rangelist,l:i+1)
		let l:line2 = get(l:rangelist,l:i+2)
		if l:type == 'add'
			call add(l:cntlist, 'add')
			call add(l:cntlist, l:line1+1)
			let l:cnt = s:countSourceLines(l:line1+2+s:tag_allowr+s:tag_mode,l:line2-1-s:tag_mode)
			call extend(l:cntlist, l:cnt)
		elseif l:type == 'chg'
			call add(l:cntlist, 'chg')
			call add(l:cntlist, l:line1+1)
			call setpos('.', [0, l:line1+2+s:tag_allowr, 1, 0])
			call searchpair('#if','#else','#endif')
			let l:midline = line('.')
			let l:cnt = s:countSourceLines(l:line1+3+s:tag_allowr,l:midline-1)
			call extend(l:cntlist, l:cnt)
			let l:cnt = s:countSourceLines(l:midline+1,l:line2-2)
			call extend(l:cntlist, l:cnt)
		elseif l:type == 'del'
			call add(l:cntlist, 'del')
			call add(l:cntlist, l:line1+1)
			let l:cnt = s:countSourceLines(l:line1+3+s:tag_allowr,l:line2-2)
			call extend(l:cntlist, l:cnt)
		endif
		let l:i   = l:i + 3
	endwhile
	return l:cntlist
endfunction
function! s:modifyList()
	silent! exe "normal gg"
	let l:rangelist = []
	let l:startline = escape(s:constructStartLine(), s:ptn_escape)
	let l:keyline   = s:constructKeyword()
	let l:endline   = escape(s:constructEndLine(), s:ptn_escape)
	let l:lineno1   = search(l:startline)
	while l:lineno1 > 0
		let l:keylinetext = getline(l:lineno1 + 1)
		if stridx(l:keylinetext, l:keyline) > 0
			call setpos('.', [0, l:lineno1, 1, 0])
			let l:lineno2 = searchpair(l:startline, '', l:endline)
			if l:lineno2 > l:lineno1
				if stridx(l:keylinetext, 'ADD[') > 0
					call add(l:rangelist, 'add')
				elseif stridx(l:keylinetext, 'CHG[') > 0
					call add(l:rangelist, 'chg')
				elseif stridx(l:keylinetext, 'DEL[') > 0
					call add(l:rangelist, 'del')
				endif
				call add(l:rangelist, l:lineno1)
				call add(l:rangelist, l:lineno2)
			endif
		endif
		let l:lineno2 = search(l:startline)
		if l:lineno2 <= l:lineno1
			let l:lineno1 = -1
		else
			let l:lineno1 = l:lineno2
		endif
	endwhile
	return l:rangelist
endfunction
function! s:rmMultilineComment()
	call setpos('.', [0, 1, 1, 0])
	let v:errmsg = ''
	silent! /\/\*
	while v:errmsg == ''
		silent! exe "normal v/\\*\\//e\<CR>d"
		if v:errmsg != ''
			break
		endif
		silent! /\/\*
	endwhile
endfunction
function! s:countSourceLines(startlineno, endlineno)
	silent! redir => dummy
	" delete lines after range
	if a:endlineno < line('$')
		silent! exe "normal ".(a:endlineno+1)."G"
		silent! exe "normal ".(line("$")-a:endlineno)."dd"
	endif
	" delete lines before range
	if a:startlineno > 1
		silent! exe "normal gg"
		silent! exe "normal ".(a:startlineno-1)."dd"
	endif
	" delete comment /*...*/
	silent! %s+/\*.*\*/++g
	" delete comment //...
	silent! %s+//.*$++g
	call s:rmMultilineComment()
	" remove empty line
	silent! g+^\s*$+d
	let l:count = line("$")
	silent undo
	redir END
	return [a:endlineno-a:startlineno+1, l:count]
endfunction

function! s:constructStartLine()
	let l:output = s:cmt_start . s:tag_start . s:cmt_end
	return l:output
endfunction
function! s:constructEndLine()
	let l:output = s:cmt_start . s:tag_end . s:cmt_end
	return l:output
endfunction
function! s:constructKeyword()
	let l:output = '[' . s:tag_key1 . ']'
	if s:tag_key2 != ''
		let l:output = l:output . '[' . s:tag_key2 . ']'
		if s:tag_key3 != ''
			let l:output = l:output . '[' . s:tag_key3 . ']'
		endif
	endif
	return l:output
endfunction
function! s:constructKeywordLine(type)
	if a:type == 'add'
		let l:addtag = 'ADD[][]'
	elseif a:type == 'chg'
		let l:addtag = 'CHG[][]_[][]'
	elseif a:type == 'del'
		let l:addtag = 'DEL[][]'
	endif
	let l:curtime = strftime(s:tag_timef)
	let l:output = s:cmt_start . l:addtag . s:tag_sep . s:constructKeyword() . s:tag_sep . s:tag_user . ' ' . l:curtime . s:cmt_end
	return l:output
endfunction
function! s:constructReasonLine()
	let l:msg    = input("Reason: ", s:tag_reason)
	let l:output = s:cmt_start . l:msg . s:cmt_end
	return l:output
endfunction
function! s:constructIfLine(type)
	if a:type == 'add'
		if s:tag_mode == 1
			if s:tag_co == ''
				let l:addtag = '#if 1'
			else
				let l:addtag = '#ifndef ' . s:tag_co
			endif
		else
			let l:addtag = ''
		endif
	elseif a:type == 'chg'
		if s:tag_mode == 1
			if s:tag_co == ''
				let l:addtag = '#if 0'
			else
				let l:addtag = '#ifdef ' . s:tag_co
			endif
		else
			let l:addtag = '#if 0'
		endif
	elseif a:type == 'del'
		if s:tag_mode == 1
			if s:tag_co == ''
				let l:addtag = '#if 0'
			else
				let l:addtag = '#ifdef ' . s:tag_co
			endif
		else
			let l:addtag = '#if 0'
		endif
	endif
	return l:addtag
endfunction
function! s:constructElseLine(type)
	if a:type == 'add'
		let l:addtag = ''
	elseif a:type == 'chg'
		if s:tag_mode == 1
			if s:tag_co == ''
				let l:addtag = '#else'
			else
				let l:addtag = '#else /* ' . s:tag_co . ' */'
			endif
		else
			let l:addtag = '#else'
		endif
	elseif a:type == 'del'
		let l:addtag = ''
	endif
	return l:addtag
endfunction
function! s:constructEndifLine(type)
	if a:type == 'add'
		if s:tag_mode == 1
			if s:tag_co == ''
				let l:addtag = '#endif'
			else
				let l:addtag = '#endif /* ' . s:tag_co . ' */'
			endif
		else
			let l:addtag = ''
		endif
	elseif a:type == 'chg'
		if s:tag_mode == 1
			if s:tag_co == ''
				let l:addtag = '#endif'
			else
				let l:addtag = '#endif /* ' . s:tag_co . ' */'
			endif
		else
			let l:addtag = '#endif'
		endif
	elseif a:type == 'del'
		if s:tag_mode == 1
			if s:tag_co == ''
				let l:addtag = '#endif'
			else
				let l:addtag = '#endif /* ' . s:tag_co . ' */'
			endif
		else
			let l:addtag = '#endif'
		endif
	endif
	return l:addtag
endfunction

function! s:ModifyTag(type, startlineno, endlineno)
	" start part
	let l:curlineno = a:startlineno - 1
	call append(l:curlineno, s:constructStartLine())
	let l:curlineno += 1
	call append(l:curlineno, s:constructKeywordLine(a:type))
	let l:curlineno += 1
	if s:tag_allowr > 0
		call append(l:curlineno, s:constructReasonLine())
		let l:curlineno += 1
	endif
	let l:ifelend = s:constructIfLine(a:type)
	if l:ifelend != ''
		call append(l:curlineno, l:ifelend)
		let l:curlineno += 1
	endif
	" middle part
	if a:type == 'add'
		" add an empty line
		call append(l:curlineno, '')
		let l:curlineno += 1
		let l:poslineno = l:curlineno
	elseif a:type == 'chg'
		" skip select lines
		let l:curlineno = l:curlineno + a:endlineno - a:startlineno + 1
		" add #else
		let l:ifelend = s:constructElseLine(a:type)
		if l:ifelend != ''
			call append(l:curlineno, l:ifelend)
			let l:curlineno += 1
		endif
		" add an empty line
		call append(l:curlineno, '')
		let l:curlineno += 1
		let l:poslineno = l:curlineno
	elseif a:type == 'del'
		" skip select lines
		let l:curlineno = l:curlineno + a:endlineno - a:startlineno + 1
		let l:poslineno = l:curlineno
	endif
	" end part
	let l:ifelend = s:constructEndifLine(a:type)
	if l:ifelend != ''
		call append(l:curlineno, l:ifelend)
		let l:curlineno += 1
	endif
	call append(l:curlineno, s:constructEndLine())
	call setpos('.', [0, l:poslineno, 0, 0])
endfunction

function! s:splitChgBlock(startline, endline)
	call setpos('.', [0, a:startline + 2 + s:tag_allowr, 1, 0])
	call searchpair('#if','#else','#endif')
	let l:endtext = getline(a:endline)
	let l:midline = line('.')
	" change part after #else into an ADD block
	" #endif for ADD block
	let l:ifelend = s:constructEndifLine('add')
	if l:ifelend != ''
		call setline(a:endline-1, l:ifelend)
	else
		silent! exe "normal ".(a:endline - 1)."Gdd"
	endif
	let l:curlineno = l:midline
	" copy start line
	let l:linetext  = getline(a:startline)
	call append(l:curlineno, l:linetext)
	let l:curlineno = l:curlineno + 1
	" copy keyword line
	let l:linetext  = getline(a:startline + 1)
	let l:linetext  = substitute(l:linetext, '\CCHG\[\d*\]\[\d*\]_\[\d*\]\[\d*\]', 'ADD[][]', '')
	call append(l:curlineno, l:linetext)
	let l:curlineno = l:curlineno + 1
	" copy reason line
	if s:tag_allowr > 0
		let l:linetext  = getline(a:startline + 2)
		call append(l:curlineno, l:linetext)
		let l:curlineno = l:curlineno + 1
	endif
	" add #if according to s:tag_mode
	let l:ifelend = s:constructIfLine('add')
	if l:ifelend != ''
		call append(l:curlineno, l:ifelend)
		let l:curlineno += 1
	endif
	" change part before #else into an DEL block
	" #endif for DEL block
	let l:ifelend = s:constructEndifLine('del')
	call setline(l:midline, l:ifelend)
	" copy end line
	call append(l:midline, l:endtext)
	" modify keyword line
	let l:linetext  = getline(a:startline + 1)
	let l:linetext  = substitute(l:linetext, '\CCHG\[\d*\]\[\d*\]_\[\d*\]\[\d*\]', 'DEL[][]', '')
	call setline(a:startline+1, l:linetext)
	return l:midline
endfunction
function! s:tellPos(startlineno, endlineno)
	let l:oldpos    = getpos('.')
	let l:rangelist = s:modifyList()
	let l:startline = a:startlineno
	let l:endline   = a:endlineno
	let l:grouplist = []
	let l:i         = 0
	while l:i < len(l:rangelist)
		let l:type  = get(l:rangelist,l:i)
		let l:line1 = get(l:rangelist,l:i+1)
		let l:line2 = get(l:rangelist,l:i+2)
		let l:i = l:i + 3
		if l:startline < l:line1
			let l:startline = l:line1
			if l:startline > l:endline
				break
			endif
		endif
		if l:startline <= l:line2
			call add(l:grouplist, l:type)
			call add(l:grouplist, l:line1)
			call add(l:grouplist, l:line2)
			call add(l:grouplist, l:startline)
			if l:endline <= l:line2
				call add(l:grouplist, l:endline)
				let l:startline = l:endline + 1
				break
			else
				call add(l:grouplist, l:line2)
				let l:startline = l:line2 + 1
			endif
		endif
	endwhile
	call setpos('.', l:oldpos)
	return l:grouplist
endfunction
function! s:approveAddBlock(blockline1, blockline2, appline1, appline2)
	if a:appline1 <= a:blockline1 + 2 + s:tag_allowr + s:tag_mode
		"approve region begins at the beginning of the block
		if a:appline2 >= a:blockline2 - 1 - s:tag_mode
			"approve region ends at the ending of the block
			silent! exe "normal ".(a:blockline2 - s:tag_mode)."G".(s:tag_mode + 1)."dd"
			silent! exe "normal ".a:blockline1."G".(s:tag_allowr + s:tag_mode + 2)."dd"
		else
			let l:applines = a:appline2 - (a:blockline1 + 2 + s:tag_allowr + s:tag_mode)
			if l:applines > 0
				silent! exe "normal ".a:blockline1."G".(s:tag_allowr + s:tag_mode + 2)."dd".l:applines."jp"
			elseif l:applines == 0
				silent! exe "normal ".a:blockline1."G".(s:tag_allowr + s:tag_mode + 2)."ddp"
			endif
		endif
	else
		if a:appline2 >= a:blockline2 - 1 - s:tag_mode
			"approve region ends at the ending of the block
			let l:applines = a:blockline2 - 1 - s:tag_mode - a:appline1
			if l:applines >= 0
				silent! exe "normal ".(a:blockline2-s:tag_mode)."G".(s:tag_mode + 1)."dd".(l:applines+1)."kP"
			endif
		else
			silent! exe "normal ".a:blockline1."G".(s:tag_allowr + s:tag_mode + 2)."Y".a:appline2."Gp"
			silent! exe "normal ".(a:blockline2 + s:tag_allowr + 2)."G".(s:tag_mode + 1)."Y".a:appline1."GP"
		endif
	endif
endfunction
function! s:approveDelBlock(blockline1, blockline2, appline1, appline2)
	if a:appline1 <= a:blockline1 + 3 + s:tag_allowr
		"approve region begins at the beginning of the block
		if a:appline2 >= a:blockline2 - 2
			"approve region ends at the ending of the block
			silent! exe "normal ".a:blockline1."G".(a:blockline2 - a:blockline1 + 1)."dd"
		else
			let l:applines = a:appline2 - (a:blockline1 + 3 + s:tag_allowr)
			if l:applines >= 0
				silent! exe "normal ".(a:blockline1 + 3 + s:tag_allowr)."G".(l:applines + 1)."dd"
			endif
		endif
	else
		if a:appline2 >= a:blockline2 - 2
			"approve region ends at the ending of the block
			let l:applines = a:blockline2 - 2 - a:appline1
			if l:applines >= 0
				silent! exe "normal ".a:appline1."G".(l:applines + 1)."dd"
			endif
		else
			silent! exe "normal ".a:appline1."G".(a:appline2 - a:appline1 + 1)."dd"
		endif
	endif
endfunction
function! s:approveChgBlock(blockline1, blockline2, appline1, appline2)
	let l:midline = s:splitChgBlock(a:blockline1, a:blockline2)
	if l:midline <= a:appline1
		"approve region locates after #else
		let l:newappline1   = a:appline1 + 3 + s:tag_allowr + s:tag_mode
		let l:newappline2   = a:appline2 + 3 + s:tag_allowr + s:tag_mode
		let l:newblockline2 = a:blockline2 + 2 + s:tag_allowr + s:tag_mode
		if l:newappline1 > l:newblockline2
			let l:newappline1 = l:newblockline2
		endif
		if l:newappline2 > l:newblockline2
			let l:newappline2 = l:newblockline2
		endif
		call s:approveAddBlock(l:midline + 2, l:newblockline2, l:newappline1, l:newappline2)
	elseif l:midline < a:appline2
		let l:newappline2   = a:appline2 + 3 + s:tag_allowr + s:tag_mode
		let l:newblockline2 = a:blockline2 + 2 + s:tag_allowr + s:tag_mode
		if l:newappline2 > l:newblockline2
			let l:newappline2 = l:newblockline2
		endif
		call s:approveAddBlock(l:midline + 2, l:newblockline2, l:midline + 2, l:newappline2)
		call s:approveDelBlock(a:blockline1, l:midline + 1, a:appline1, l:midline + 1)
	else
		"approve region locates before #else
		call s:approveDelBlock(a:blockline1, l:midline + 1, a:appline1, a:appline2)
	endif
endfunction
function! s:denyAddBlock(blockline1, blockline2, appline1, appline2)
	if a:appline1 <= a:blockline1 + 2 + s:tag_allowr + s:tag_mode
		"deny region begins at the beginning of the block
		if a:appline2 >= a:blockline2 - 1 - s:tag_mode
			"deny region ends at the ending of the block
			silent! exe "normal ".a:blockline1."G".(a:blockline2 - a:blockline1 + 1)."dd"
		else
			let l:applines = a:appline2 - (a:blockline1 + 2 + s:tag_allowr + s:tag_mode)
			if l:applines >= 0
				silent! exe "normal ".(a:blockline1 + 2 + s:tag_allowr + s:tag_mode)."G".(l:applines + 1)."dd"
			endif
		endif
	else
		if a:appline2 >= a:blockline2 - 1 - s:tag_mode
			"deny region ends at the ending of the block
			let l:applines = a:blockline2 - 1 - s:tag_mode - a:appline1
			if l:applines >= 0
				silent! exe "normal ".a:appline1."G".(l:applines + 1)."dd"
			endif
		else
			silent! exe "normal ".a:appline1."G".(a:appline2 - a:appline1 + 1)."dd"
		endif
	endif
endfunction
function! s:denyDelBlock(blockline1, blockline2, appline1, appline2)
	if a:appline1 <= a:blockline1 + 3 + s:tag_allowr
		"deny region begins at the beginning of the block
		if a:appline2 >= a:blockline2 - 2
			"deny region ends at the ending of the block
			silent! exe "normal ".(a:blockline2 - 1)."G2dd"
			silent! exe "normal ".a:blockline1."G".(s:tag_allowr + 3)."dd"
		else
			let l:applines = a:appline2 - (a:blockline1 + 3 + s:tag_allowr)
			if l:applines > 0
				silent! exe "normal ".a:blockline1."G".(s:tag_allowr + 3)."dd".l:applines."jp"
			elseif l:applines == 0
				silent! exe "normal ".a:blockline1."G".(s:tag_allowr + 3)."ddp"
			endif
		endif
	else
		if a:appline2 >= a:blockline2 - 2
			"deny region ends at the ending of the block
			let l:applines = a:blockline2 - 2 - a:appline1
			if l:applines >= 0
				silent! exe "normal ".(a:blockline2-1)."G2dd".(l:applines+1)."kP"
			endif
		else
			silent! exe "normal ".a:blockline1."G".(s:tag_allowr + 3)."Y".a:appline2."Gp"
			silent! exe "normal ".(a:blockline2 + 3)."G2Y".a:appline1."GP"
		endif
	endif
endfunction
function! s:denyChgBlock(blockline1, blockline2, appline1, appline2)
	let l:midline = s:splitChgBlock(a:blockline1, a:blockline2)
	if l:midline <= a:appline1
		"deny region locates after #else
		let l:newappline1   = a:appline1 + 3 + s:tag_allowr + s:tag_mode
		let l:newappline2   = a:appline2 + 3 + s:tag_allowr + s:tag_mode
		let l:newblockline2 = a:blockline2 + 2 + s:tag_allowr + s:tag_mode
		if l:newappline1 > l:newblockline2
			let l:newappline1 = l:newblockline2
		endif
		if l:newappline2 > l:newblockline2
			let l:newappline2 = l:newblockline2
		endif
		call s:denyAddBlock(l:midline + 2, l:newblockline2, l:newappline1, l:newappline2)
	elseif l:midline < a:appline2
		let l:newappline2   = a:appline2 + 3 + s:tag_allowr + s:tag_mode
		let l:newblockline2 = a:blockline2 + 2 + s:tag_allowr + s:tag_mode
		if l:newappline2 > l:newblockline2
			let l:newappline2 = l:newblockline2
		endif
		call s:denyAddBlock(l:midline + 2, l:newblockline2, l:midline + 2, l:newappline2)
		call s:denyDelBlock(a:blockline1, l:midline + 1, a:appline1, l:midline + 1)
	else
		"deny region locates before #else
		call s:denyDelBlock(a:blockline1, l:midline + 1, a:appline1, a:appline2)
	endif
endfunction
