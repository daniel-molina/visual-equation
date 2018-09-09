# visualequation

Visualequation creates equations visually, in a WYSIWYG (What You See Is What You Get) style. By the moment, equations can be exported to PNG, EPS, PDF and SVG. PNG and SVG are transparent. If you want a background you can put a white (or whatever color) colorbox to the whole equation in the editor before exporting.

## Requirements
By the moment it has only been tested on GNU/Linux. But it would be interesting to have installation instructions for the dependencies on other operative systems.

To run the program successfully, you need:

* python2
* pygame
* Tkinter
* LaTeX
* Some specific LaTeX packages (you can find them in the preamble of the equation template).
* Some command-line programs to manipulate LaTeX output:
  * dvipng
  * dvips
  * dvisvgm
  * epstopdf
* exiftool

### Microsoft Windows and MacOS

Volunteers needed!
  
### Debian/Ubuntu or derivatives

The following packages should be enough:

* python-pygame
* python-tk
* texlive-latex-recommended
* dvipng
* texlive-font-utils
* texlive-math-extra (or textlive-science in newer versions)
* libimage-exiftool-perl

LaTeX will require a lot of MB, but the quality of the equations is incredible too.

To see if everything is installed properly you can run:

$ python2 setup.py test

## Building

If you have the sources and you want build the program, generate the LaTeX symbols used by the program:

$ python2 populate_symbols.py

It will late a bit. After that, if you simply want to run the program you can do

$ python2 visualequation/__main__.py

## Installation

To install the program you can use pip. To download it and install it from PYPI (not uploaded yet), just

$ python2 -m pip install --user --upgrade visualequation

If you have the sources, after running the Building instructions you can generate a package if you have setuptools installed

$ python setup.py sdist

To install it, you can do

$ python2 -m pip install --user dist/visualequation-<version>.tar.gz

where you substitute <version> by the version number of the file generated in dist/.

By default, the program should be installed in ~/.local/bin . If you do not have it in your path you can extend it by

$ PATH=${PATH}:${HOME}/.local/bin

To have this available always that you open a terminal, you can add the previous command to your .bashrc by hand.

To execute the program, just run

$ visualequation 

in whatever current directory.

## Usage/Instructions

This program is expected to be user-friendly and intuitive, so it should not be difficult to use.

Instead of a cursor, you navigate with a box that surrounds blocks of the equation, from a single symbol to the entire equation. Insert characters at the right of the box by pressing keys on the keyboard or clicking symbols in the above panel. If the box surrounds a square, as when you open the program, you overwrite the square.

The following key combinations work: (They can be changed or extended in the future)

* LEFT and RIGHT (or TAB or clicking the equation):
Change the selection box.

* UP and DOWN (or clicking in the menu items of the panel below):
Change the symbols and operators showed in the panel above.

* DELETE or BACKSPACE:
Remove current selection. If it was the entire argument of an operator, a square will remain so you can select it and add something in the future. There is no way to remove those squares without deleting the entire operator.

* ^ and _:
Put a superindex or subindex.

* CTRL+z:
Recover the equation as it was before last change. You can use it all the times that you need.

* CTRL+y:
The opposite of CTR+z. If you change the equation after using CTRL+z, the future history from that point will not be accessible by Ctrl+y anymore.

* CTRL+c:
Copy the current selection.

* CTRL+x:
Cut the current selection.

* CTRL+v:
Paste the last copied or cut selection.

* CTRL+s:
Save the equation to PNG, PDF, EPS or SVG format. If format is either PNG or PDF, you will be able to recover the equation (see CTR+o).

* CTR+o:
Open an equation from a PNG or PDF previously created with this program (see CTR+s). The current equation being edited will be lost.

* CTR+p:
Create a square at the left of the selection box, ready to be overwritten. It is useful if you forgot to write something at the left of a block and you do not want to delete the first symbol/operator until you write the missing part.

* SHIFT+click on an element of the panel above:
If the element is a symbol, the selection is replaced by the symbol. If it is an operator, the selection is replaced by the operator and the first argument of it is set to the selection. (The first argument is the one represented by one dot or three dots instead of a square)

## Known Issues

* Conversion to SVG fails when the equation contains a Text. The application will wait forever while converting, so the user has to force the exit of the execution.
  * Affected environments: Ubuntu Xenial (16.04) (dvisvgm 1.9.2)
  * It is known to work in Ubuntu 14.04 and 18.04 (dvisvgm 1.2.2 and 2.1.3, respectively)
  * Solutions: There are not so many programs that transform images into a nice SVG, most of them have issues. pdf2svg does normally a good work, but it does an ugly output in the affected system for the so-called Text block. Maybe that shows that the problem is caused by something related with the associated font.

## License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

## Acknowledgements

* I have been inspired by Ekee (http://rlehy.free.fr/) features. It is a pity that the program is not mantained (2018).
