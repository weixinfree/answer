alias chrome="/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome"
chrome --headless --disable-gpu --dump-dom $1 1> _baidu.html 2> _err.log