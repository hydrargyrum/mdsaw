#!/usr/bin/env pytest

from subprocess import check_call, CalledProcessError
from tempfile import mkdtemp
from textwrap import dedent
from pathlib import Path

import pytest


def literal(text):
	return dedent(text).lstrip()


@pytest.fixture
def indir(tmp_path):
	ret = tmp_path / 'in'
	ret.mkdir()
	return ret


@pytest.fixture
def outdir(tmp_path):
	ret = tmp_path / 'out'
	ret.mkdir()
	return ret


def run_compose(*args):
	check_call([mdpath, '-c', *args])


def run_decompose(*args):
	check_call([mdpath, '-d', *args])


def check_file_contains(path, content):
	assert Path(path).read_text() == content


def create_dir_content(path, datadict):
	for name, content in datadict.items():
		path.joinpath(name).write_text(content)


def check_dir_contains(path, datadict):
	for name, content in datadict.items():
		assert path.joinpath(name).read_text() == content


def test_decompose(indir, outdir):
	create_dir_content(indir, {
		'1.md': literal('''
			# bar
			b 1
			b 2

			# foo
			f 1
			f 2
		'''),
	})

	run_decompose(indir / '1.md', outdir)

	check_dir_contains(outdir, {
		'bar.md': literal('''
			# bar
			b 1
			b 2
		'''),
		'foo.md': literal('''
			# foo
			f 1
			f 2
		'''),
	})


def test_decompose_empty(indir, outdir):
	create_dir_content(indir, {
		'1.md': literal('''
			# bar

			# foo
			f 1
			f 2
			# qux
			# quack
			f 1
			f 2
		'''),
	})

	run_decompose(indir / '1.md', outdir)

	check_dir_contains(outdir, {
		'bar.md': literal('''
			# bar

		'''),
		'qux.md': literal('''
			# qux

		'''),
		'foo.md': literal('''
			# foo
			f 1
			f 2
		'''),
		'quack.md': literal('''
			# quack
			f 1
			f 2
		'''),
	})


def test_decompose_subtitles(indir, outdir):
	create_dir_content(indir, {
		'1.md': literal('''
			# bar
			b 1
			## sub
			b 2

			# foo
			f 1

			### subsub
			f 2
		'''),
	})

	run_decompose(indir / '1.md', outdir)

	check_dir_contains(outdir, {
		'bar.md': literal('''
			# bar
			b 1
			## sub
			b 2
		'''),
		'foo.md': literal('''
			# foo
			f 1

			### subsub
			f 2
		'''),
	})


def test_decompose_error_dirs(indir, outdir):
	with pytest.raises(CalledProcessError):
		run_decompose(indir, outdir)


def test_compose(indir, outdir):
	create_dir_content(indir, {
		'bar.md': literal('''
			# bar
			b 1
			b 2
		'''),
		'foo.md': literal('''
			# foo
			f 1
			f 2
		'''),
	})

	run_compose(indir, outdir / 'test.md')

	check_file_contains(outdir / 'test.md', literal('''
		# bar
		b 1
		b 2

		# foo
		f 1
		f 2
	'''))


def test_compose_selected(indir, outdir):
	create_dir_content(indir, {
		'bar.md': literal('''
			# bar
			b 1
			b 2
		'''),
		'foo.md': literal('''
			# foo
			f 1
			f 2
		'''),
	})

	run_compose(indir / 'foo.md', indir / 'bar.md', outdir / 'test.md')

	check_file_contains(outdir / 'test.md', literal('''
		# foo
		f 1
		f 2

		# bar
		b 1
		b 2
	'''))


def test_compose_error_mixpaths(indir, outdir):
	create_dir_content(indir, {
		'bar.md': '# bar\nb 1\nb 2\n',
	})
	with pytest.raises(CalledProcessError):
		run_compose(indir / 'foo.md', indir, outdir / 'test.md')


mdpath = Path(__file__).parent.with_name('mdsaw')
