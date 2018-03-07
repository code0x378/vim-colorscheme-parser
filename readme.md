# Vim colorscheme parser

VCP converts vim colorscheme (color/*.vim) files into json, css or sass files.  

##Notes

- gui colors take precedence over cterm
- gui, term and cterm formatting values are not currently handled (i.e. no underline css)
- named colors are looked up first via xterm 256 colors then X11 colors
- int colors are looked up via xterm colors
- if the colors (name or int), are not found they are just returned as is