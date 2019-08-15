#!/usr/bin/env python3

import argparse
import pathlib
import re
import sys


def to_filename(name):
	name = name.replace('.txt', '')
	name = name.lower()
	name = re.sub(r'[\W.]+', '-', name)
	name += '.txt'
	return name


def decompose(filepath, dirpath):
	text = filepath.read_text()
	matches = re.findall(
		r'(?:----|#) ([^\n]+)\n'
		r'(.+?)'
		r'(?:(?=^----|^#)|\Z)',
		text, flags=re.UNICODE | re.DOTALL | re.MULTILINE
	)

	for title, subtext in matches:
		subtext = subtext.strip()
		subtext = f'# {title}\n\n{subtext}\n'

		fn = to_filename(title)
		print('writing', fn, file=sys.stderr)
		subfilepath = dirpath.joinpath(fn)
		subfilepath.write_text(subtext)


def compose(filepath, dirpath):
	buf = []
	for subfilepath in sorted(dirpath.glob('*.txt')):
		print('reading', subfilepath, file=sys.stderr)
		subtext = subfilepath.read_text()
		if subtext.startswith('# '):
			title, _, subtext = subtext.partition('\n')
			title = title[1:].strip()  # remove "#"
		else:
			title = subfilepath.name
		subtext = subtext.strip()

		buf.append(f'# {title}\n\n')
		buf.append(subtext)
		buf.append('\n\n')

	if buf:  # don't empty the file
		text = ''.join(buf)
		if filepath == pathlib.Path('-'):
			print(text)
		else:
			filepath.write_text(text)


def build_parser():
	parser = argparse.ArgumentParser(
		description='''
Compose/decompose text files with multiple markdown sections

Composition
-----------

Multiple text files from the input directory will be merged into a singe big
output text file, with markdown sections for each of the original separate
files, and titles to split them ("# name of the file").

Decomposition
-------------

Conversely, if an input text file has markdown titles (for example lines like
"# the title"), it can be decomposed in multiple text files in the output
directory, each corresponding to one of the sections.
For example, one of the files could be "the-title.txt" and contain the text
from that section up to the next title.
'''.strip(),
		formatter_class=argparse.RawDescriptionHelpFormatter,
	)

	cmp = parser.add_mutually_exclusive_group(required=True)
	cmp.add_argument(
		'-c', '--compose', '--merge', action='store_true',
		help='Compose multiple text files into a single file',
	)
	cmp.add_argument(
		'-d', '--decompose', '--split', action='store_true',
		help='Decompose a text file with separators into multiple files',
	)

	parser.add_argument(
		'inpath', type=pathlib.Path,
		help='Input path, must be an existing directory path to the '
		'files to merge if in composing mode or an existing file path'
		' in decomposing mode',
	)
	parser.add_argument(
		'outpath', type=pathlib.Path,
		help='Output path, must be a file path where to write the '
		'merged file when composing or an existing directory path '
		'where the resulting files will be written when decomposing',
	)
	return parser


def main():
	parser = build_parser()
	args = parser.parse_args()

	if args.compose:
		if not args.inpath.is_dir():
			parser.error(f'{str(args.inpath)!r} is not a directory')

		if args.outpath.exists() and not args.outpath.is_file():
			parser.error(f'{str(args.outpath)!r} is not a file')

		compose(args.outpath, args.inpath)
	elif args.decompose:
		if not args.inpath.is_file():
			parser.error('{str(args.inpath)!r} is not a file')

		if not args.outpath.is_dir():
			parser.error(f'{str(args.outpath)!r} is not a directory')

		decompose(args.inpath, args.outpath)
	else:
		assert False


if __name__ == '__main__':
	main()
