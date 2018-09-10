import os
import unittest
import tempfile
import shutil
import subprocess
import pickle

from visualequation import dirs

class DependenciesTest(unittest.TestCase):

    def test_latex(self):
        temp_dirpath = tempfile.mkdtemp()
        latex_fpath = os.path.join(temp_dirpath, 'latex.tex')
        latex_code = r"\int_0^1 f(x)\, dx = \sum_{n=0}^\infty a_n"
        with open(dirs.LATEX_TEMPLATE, "r") as ftempl:
            with open(latex_fpath, "w") as flatex:
                for line in ftempl:
                    flatex.write(line.replace('%EQ%', latex_code))
        try:
            subprocess.check_output(["latex", "-halt-on-error",
                                     "-output-directory=" + temp_dirpath,
                                     latex_fpath])
        except subprocess.CalledProcessError:
            raise SystemExit("Suggestion: Do you have the AMS LaTeX packages?")
        except OSError:
            raise SystemExit("Suggestion: Do you have command latex?")
        shutil.rmtree(temp_dirpath)

    def test_dvipng(self):
        temp_dirpath = tempfile.mkdtemp()
        dvi_fpath = os.path.join(os.path.dirname(__file__), 'im.dvi')
        png_fpath = os.path.join(temp_dirpath, 'im.png')
        try:
            subprocess.check_output(["dvipng", "-T", "tight", "-D", "600",
                                     "-bg", "Transparent",
                                     "-o", png_fpath, dvi_fpath])
        except subprocess.CalledProcessError:
            raise SystemExit("Was DVI image not found in the directory?")
        except OSError:
            raise SystemExit("Suggestion: Do you have command dvipng?")
        shutil.rmtree(temp_dirpath)

    def test_dvips(self):
        temp_dirpath = tempfile.mkdtemp()
        dvi_fpath = os.path.join(os.path.dirname(__file__), 'im.dvi')
        eps_fpath = os.path.join(temp_dirpath, 'im.ps')
        try:
            subprocess.check_output(["dvips", "-E", "-D", "600", "-Ppdf", 
                                     "-o", eps_fpath, dvi_fpath])
        except subprocess.CalledProcessError:
            raise SystemExit("DVI image not found in the directory?")
        except OSError:
            raise SystemExit("Suggestion: Do you have command dvips?")

        shutil.rmtree(temp_dirpath)

    def test_epstopdf(self):
        temp_dirpath = tempfile.mkdtemp()
        eps_fpath = os.path.join(os.path.dirname(__file__), 'im.ps')
        pdf_fpath = os.path.join(temp_dirpath, 'im.pdf')
        try:
            subprocess.check_output(["epstopdf", "--outfile", pdf_fpath,
                                     eps_fpath])
        except subprocess.CalledProcessError:
            raise SystemExit("EPS image not found in the directory?")
        except OSError:
            raise SystemExit("Suggestion: Do you have command epstopdf?")

        shutil.rmtree(temp_dirpath)

    def test_dvisvgm(self):
        temp_dirpath = tempfile.mkdtemp()
        dvi_fpath = os.path.join(os.path.dirname(__file__), 'im.dvi')
        svg_fpath = os.path.join(temp_dirpath, 'im.svg')
        # dvisgvm does not return error code when file is not found
        try:
            subprocess.call(["dvisvgm", "--no-fonts", "--scale=5,5", 
                             "-o", svg_fpath, dvi_fpath])
        except OSError:
            raise SystemExit("Suggestion: Do you have command dvisvgm?")

        shutil.rmtree(temp_dirpath)

    def test_exiftool_read(self):
        png_fpath = os.path.join(os.path.dirname(__file__), 'im.png')
        pdf_fpath = os.path.join(os.path.dirname(__file__), 'im.pdf')

        def fun(fpath):
            try:
                eq_str = subprocess.check_output(["exiftool", "-b", "-s3",
                                                  "-description", fpath])
                if not eq_str:
                    raise SystemExit("No equation inside file %s!" % fpath)
                pickle.loads(eq_str)
            except subprocess.CalledProcessError:
                raise SystemExit("Error by exiftool when trying to extract"
                                 + "equation from file.")
            except (KeyError, EOFError, IndexError):
                raise SystemExit("Error while translating read equation "
                           + "from file. Was metadata changed?")
            except OSError:
                raise SystemExit("Suggestion: Do you have command exiftool?")
        fun(png_fpath)
        fun(pdf_fpath)

            
    def test_exiftool_write(self):
        temp_dirpath = tempfile.mkdtemp()
        png_fpath = os.path.join(os.path.dirname(__file__), 'im.png')
        pdf_fpath = os.path.join(os.path.dirname(__file__), 'im.pdf')
        def fun(fpath):
            try:
                subprocess.check_output(["exiftool", "-out", temp_dirpath,
                                         "-description=Hi", fpath])
            except subprocess.CalledProcessError:
                raise SystemExit("Exiftool error.")
            except OSError:
                raise SystemExit("Suggestion: Do you have command exiftool?")
        fun(png_fpath)
        fun(pdf_fpath)
        shutil.rmtree(temp_dirpath)

    def test_tkinter(self):
        try:
            import Tkinter, tkFileDialog
        except ImportError:
            raise SystemExit("You must have Tk installed for python.")

    def test_pygame(self):
        try:
            import pygame
        except ImportError:
            raise SystemExit("You must have pygame installed.")

if __name__ == "__main__":
    unittest.main()