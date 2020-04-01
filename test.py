#!/usr/bin/env -S python3 -m pytest

from subprocess import check_call, CalledProcessError
from tempfile import mkdtemp
from pathlib import Path

import pytest


@pytest.fixture
def indir():
	return Path(mkdtemp())


@pytest.fixture
def outdir():
	return Path(mkdtemp())


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
		'1.md': '# bar\nb 1\nb 2\n\n# foo\nf 1\nf 2\n',
	})
	run_decompose(indir / '1.md', outdir)
	check_dir_contains(outdir, {
		'bar.md': '# bar\nb 1\nb 2\n',
		'foo.md': '# foo\nf 1\nf 2\n',
	})


def test_decompose_error_dirs(indir, outdir):
	with pytest.raises(CalledProcessError):
		run_decompose(indir, outdir)


def test_compose(indir, outdir):
	create_dir_content(indir, {
		'bar.md': '# bar\nb 1\nb 2\n',
		'foo.md': '# foo\nf 1\nf 2\n',
	})
	run_compose(indir, outdir / 'test.md')
	check_file_contains(outdir / 'test.md', '# bar\nb 1\nb 2\n\n# foo\nf 1\nf 2\n')


def test_compose_selected(indir, outdir):
	create_dir_content(indir, {
		'bar.md': '# bar\nb 1\nb 2\n',
		'foo.md': '# foo\nf 1\nf 2\n',
	})
	run_compose(indir / 'foo.md', indir / 'bar.md', outdir / 'test.md')
	check_file_contains(outdir / 'test.md', '# foo\nf 1\nf 2\n\n# bar\nb 1\nb 2\n')


def test_compose_error_mixpaths(indir, outdir):
	create_dir_content(indir, {
		'bar.md': '# bar\nb 1\nb 2\n',
	})
	with pytest.raises(CalledProcessError):
		run_compose(indir / 'foo.md', indir, outdir / 'test.md')


mdpath = Path(__file__).with_name('mdsaw')
