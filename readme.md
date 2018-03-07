# Vim colorscheme parser

VCP converts vim colorscheme (color/*.vim) files into json, css or sass files.  

## Requirements

- python 3

## Running

```less

python parser.py

```

By default VCP uses "vim-colorschemes/colors" for input and "dist" for output.

Options

```

usage: parser.py [-h] [-f FORMAT] [-i INPUT] [-o OUTPUT] [-t TESTING]

optional arguments:

-h, --help  show this help message and exit
-f FORMAT, --format FORMAT Specify an output format (sass, json, css or all)
-i INPUT, --input INPUT Specify an input directory
-o OUTPUT, --output OUTPUT Specify an output directory
-t BOOL, --testing BOOL Uses test data from testing folder

```

## Notes

- gui colors take precedence over cterm
- gui, term and cterm formatting values are not currently handled (i.e. no underline css)
- named colors are looked up first via xterm 256 colors then X11 colors
- int colors are looked up via xterm colors
- if the colors (name or int), are not found they are just returned as is