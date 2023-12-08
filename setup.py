import os.path
import sys
import glob
import copy
import runpy


root_folder = os.path.abspath(os.path.dirname(__file__))
packages = [f.split(os.sep)[1] for f in glob.glob('src/*/setup.py')]

for package in packages:
    pkg_setup_folder = os.path.join(root_folder, "src", package)
    pkg_setup_path = os.path.join(pkg_setup_folder, "setup.py")
    try:
        saved_dir = os.getcwd()
        saved_syspath = sys.path

        os.chdir(pkg_setup_folder)
        sys.path = [pkg_setup_folder] + copy.copy(saved_syspath)

        print("Start ", pkg_setup_path)
        result = runpy.run_path(pkg_setup_path)
    except Exception as e:
        print(e, file=sys.stderr)
    finally:
        os.chdir(saved_dir)
        sys.path = saved_syspath




