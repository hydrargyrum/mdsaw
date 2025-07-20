Compose/decompose text files with multiple markdown sections

Composition
-----------

Multiple text files from the input directory will be merged into a singe big
output text file, with markdown sections for each of the original separate
files, and titles to split them (`# name of the file`).

	mdsaw -c in_directory out_file.md

Or:

	mdsaw -c in_file1.md in_file2.md in_file3.md out_file.md

Decomposition
-------------

Conversely, if an input text file has markdown titles (for example lines like
`# the title`), it can be decomposed in multiple text files in the output
directory, each corresponding to one of the sections.
For example, one of the files could be `the-title.txt` and contain the text
from that section up to the next title.

	mdsaw -d in_file.md out_directory

Example
-------

A markdown file containing:

	# lorem

	lorem ipsum

	# dolor

	dolor sit amet

can be _decomposed_ in 2 files, `lorem.md` and `dolor.md`, each file
containing only the text from the corresponding section (and the heading).

Then, the 2 files `lorem.md` and `dolor.md` can be _composed_ together
to rebuild the original file.
