" --------------------------------
" 项目级 Vim 配置文件

if exists("pylon_prj_loaded")
    finish
endif

let pylon_prj_loaded = 1

" --------------------------------

" 获取项目根目录
let s:prjroot=fnamemodify('',':p')

" 解除默认的单元测试映射
unmap <F2>

" 定义单元测试的映射
noremap <F2> <Esc> :call MapPrjUnitTest() <CR>

" 定义单元测试函数
" function MapPrjUnitTest()
"     if filereadable(s:prjroot.'test/unittest.sh')
"         exec '!'. s:prjroot .'test/unittest.sh'
"     else
"         exec '! /home/q/tools/pylon_rigger/rigger start -s test'
"     endif
" endfunction
function MapPrjUnitTest()
    if filereadable(s:prjroot.'test/gotest.sh')
        exec '!'. s:prjroot .'test/gotest.sh'
    else
        exec '! /home/q/tools/pylon_rigger/rigger start -s test'
    endif
endfunction

