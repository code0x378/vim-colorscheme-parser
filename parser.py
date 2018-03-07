import argparse
import glob
import logging
import re
import json
import csv

from os.path import basename
from string import Template

##########################################
# LOGGING
##########################################
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
handler = logging.FileHandler('dist/parser.log')
handler.setLevel(logging.INFO)
logger.addHandler(handler)
logger.info('Starting parser')

##########################################
# COMMAND LINE ARGS
##########################################
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--format", type=str, help="Specify an output format (sass, json, css or all)")
parser.add_argument("-i", "--input", type=str, help="Specify an input directory")
parser.add_argument("-o", "--output", type=str, help="Specify an output directory")
parser.add_argument("-d", "--debug", help="Uses test data")
args = parser.parse_args()
format = args.format if args.format else "all"
debug = args.debug if args.debug else False

##########################################
# VARS
##########################################
REGEX_GROUP = "hi ?\w+"
REGEX_GUIFG = "guifg=(#\w+|\w+)"
REGEX_GUIBG = "guibg=(#\w+|\w+)"
REGEX_CTERMFG = "ctermfg=(#\w+|\w+)"
REGEX_CTERMBG = "ctermbg=(#\w+|\w+)"
REGEX_GUI = "gui=(\w+)"
REGEX_CTERM = "term|cterm=(\w+)"

DEFAULT_FG_COLOR = '#333'
DEFAULT_BG_COLOR = '#fff'
DEFAULT_OPTIONS = ''

parsed_data = {}

with open('templates/sass.tpl', 'r') as f:
    sass_template = Template(f.read())

with open('templates/css.tpl', 'r') as f:
    css_template = Template(f.read())

with open('data/xterm-colors.txt', 'r') as f:
    reader = csv.reader(f, delimiter='\t')
    xterm_colors = list(reader)

with open('data/x11-colors.txt', 'r') as f:
    reader = csv.reader(f, delimiter='\t')
    x11_colors = list(reader)

if debug:
    input_dir = "testing"
    output_dir = "testing"
else:
    input_dir = args.input if args.input else "vim-colorschemes/colors"
    output_dir = args.output if args.output else "dist"


##########################################
# FUNCTIONS
##########################################
def lookup_color(color):
    if color.isdigit():
        return lookup_color_by_num(color)
    else:
        return lookup_color_by_name(color)


def lookup_color_by_name(color):
    for row in xterm_colors:
        if color.lower() == row[1].lower():
            return row[2]
    for row in x11_colors:
        if color.lower() == row[0].lower():
            return row[1]
    return color


def lookup_color_by_num(color):
    for row in xterm_colors:
        if color == row[0]:
            return row[2]
    return color


def get_fg_color(val):
    color = val[0]
    if color:
        return color if color[0] == '#' else lookup_color(color)
    else:
        return ''


def get_bg_color(val):
    color = val[0]
    if color:
        return color if color[0] == '#' else lookup_color(color)
    else:
        return ''


def get_options(val):
    if val:
        return val[0]
    else:
        return DEFAULT_OPTIONS


def generate_sass_output(file_name):  # my own custom sass format
    data = {'name': file_name}

    if 'Normal' in parsed_data[file_name]:
        data['color'] = parsed_data[file_name]['Normal']['guifg']
    else:
        data['color'] = DEFAULT_FG_COLOR

    if 'Normal' in parsed_data[file_name]:
        data['background'] = parsed_data[file_name]['Normal']['guibg']
    else:
        data['background'] = DEFAULT_FG_COLOR

    if 'Title' in parsed_data[file_name]:
        data['title'] = parsed_data[file_name]['Title']['guifg']
    else:
        data['title'] = '#333'

    result = sass_template.safe_substitute(data)
    with open(output_dir + '/' + file_name + ".scss", "w") as fout:
        fout.write(result)


def generate_json_output(file_name):
    with open(output_dir + '/' + file_name + '.json', 'w') as fout:
        json.dump(parsed_data[file_name], fout, indent=4, sort_keys=True)


def generate_css_output(file_name):
    data = {'name': file_name, 'css': ''}

    data['css'] += ' body {\n'
    if 'Normal' in parsed_data[file_name]:
        if parsed_data[file_name]['Normal']['guifg'] != '':
            data['css'] += '  color: ' + parsed_data[file_name]['Normal']['guifg'] + ';\n'
        elif parsed_data[file_name]['Normal']['ctermfg'] != '':
            data['css'] += '  color: ' + parsed_data[file_name]['Normal']['ctermfg'] + ';\n'
    else:
        data['css'] += '  color: ' + DEFAULT_FG_COLOR + ';\n'

    if 'Normal' in parsed_data[file_name]:
        if parsed_data[file_name]['Normal']['guibg'] != '':
            data['css'] += '  background: ' + parsed_data[file_name]['Normal']['guibg'] + ';\n'
        elif parsed_data[file_name]['Normal']['ctermbg'] != '':
            data['css'] += '  background: ' + parsed_data[file_name]['Normal']['ctermbg'] + ';\n'
    else:
        data['css'] += '  background: ' + DEFAULT_BG_COLOR + ';\n'
    data['css'] += '}\n\n'

    for group in parsed_data[file_name]:
        data['css'] += '.' + group + ' {\n'
        if parsed_data[file_name][group]['guifg'] != '' and parsed_data[file_name][group]['guifg'] != 'NONE':
            data['css'] += '  color: ' + parsed_data[file_name][group]['guifg'] + ';\n'
        elif parsed_data[file_name][group]['ctermfg'] != '' and parsed_data[file_name][group]['ctermfg'] != 'NONE':
            data['css'] += '  color: ' + parsed_data[file_name][group]['ctermfg'] + ';\n'

        if parsed_data[file_name][group]['guibg'] != '' and parsed_data[file_name][group]['guibg'] != 'NONE':
            data['css'] += '  background: ' + parsed_data[file_name][group]['guibg'] + ';\n'
        if parsed_data[file_name][group]['ctermbg'] != '' and parsed_data[file_name][group]['ctermbg'] != 'NONE':
            data['css'] += '  background: ' + parsed_data[file_name][group]['ctermbg'] + ';\n'
        data['css'] += '}\n\n'

    result = css_template.safe_substitute(data)
    with open(output_dir + '/' + file_name + ".css", "w") as fout:
        fout.write(result)


##########################################
# MAIN
##########################################
def main():
    files = glob.glob(input_dir + "/*.vim")
    files.sort()
    ctr = 1
    total_files = len(files)

    for file in files:
        with open(file, "r", encoding="utf8", errors='ignore') as f:

            file_name = basename(file)
            logger.info('Processing: %s (%s of %s)' % (file_name, ctr, total_files))
            parsed_data[file_name] = {}

            for line in f:

                if line[0] == '"':
                    continue

                grp = re.findall(REGEX_GROUP, line)
                guifg = re.findall(REGEX_GUIFG, line)
                guibg = re.findall(REGEX_GUIBG, line)
                ctermfg = re.findall(REGEX_CTERMFG, line)
                ctermbg = re.findall(REGEX_CTERMBG, line)
                gui = re.findall(REGEX_GUI, line)
                term = re.findall(REGEX_CTERM, line)

                try:
                    group = grp[0].split(" ")[1]

                    if group not in parsed_data[file_name]:
                        parsed_data[file_name][group] = {'guifg': '', 'guibg': '', 'ctermbg': '', 'ctermfg': '',
                                                         'gui': '', 'term': ''}
                    if guifg:
                        parsed_data[file_name][group]['guifg'] = get_fg_color(guifg)
                    if guibg:
                        parsed_data[file_name][group]['guibg'] = get_bg_color(guibg)
                    if ctermfg:
                        parsed_data[file_name][group]['ctermfg'] = get_fg_color(ctermfg)
                    if ctermbg:
                        parsed_data[file_name][group]['ctermbg'] = get_bg_color(ctermbg)
                    if gui:
                        parsed_data[file_name][group]['gui'] = get_options(gui)
                    if term:
                        parsed_data[file_name][group]['term'] = get_options(term)
                except:
                    pass  # just fail for lines that cant split "hi SomeGroup"

            if format == 'sass' or format == 'all':
                generate_sass_output(file_name)
            if format == 'json' or format == 'all':
                generate_json_output(file_name)
            if format == 'css' or format == 'all':
                generate_css_output(file_name)

            ctr += 1


if __name__ == "__main__":
    main()
