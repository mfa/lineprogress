""" pre-commit hook for counting lines in .tex files to measure writing progress.

    :copyright: (c) 2012 by Andreas Madsack.
    :license: BSD, see LICENSE for more details.
"""

import shelve
import subprocess
import os
import re
import datetime
import argparse

def git_get_toplevel():
    """ returns the toplevel of the current repository
    """
    return subprocess.check_output("git rev-parse --show-toplevel", 
                                   shell=True).strip()

def git_get_changed_files():
    """ returns a list of files changed in this commit
    """
    return subprocess.check_output(
        "git diff --cached --name-only --diff-filter=ACM", shell=True)

def check_line(line):
    """ check if the line is nonempty and no comment
    """
    if len(line.strip()) == 0:
        return False
    if re.findall(r'^\s*$', line):
        return False
    if re.findall(r'^\s*%', line):
        return False
    return True


class LineProgress:
    
    def __init__(self, opts):
        self.toplevel = git_get_toplevel()
        self.shelfname = os.path.join(self.toplevel, '.git',
                                      'lineprogress')

        if opts.init:
            self.initialize()
        elif opts.list:
            self.list(opts.listtype)
        else:
            files = git_get_changed_files().split('\n')
            checked_files = self.check(files)
            if checked_files:
                self.update(checked_files)

    def check(self, file_list):
        """ Check if file is a texfile
        TODO: add option for blacklisting specific files
        """
        fn_checked = []
        for fn in file_list:
            if fn.endswith('.tex'):
                fn_checked.append(fn)
        return fn_checked

    def update(self, file_list):
        """ update the shelf for a given filelist
        """
        d = shelve.open(self.shelfname, flag='c')
        now = datetime.datetime.now()
        for fn in file_list:
            linesum = self.get_lines(fn)
            if fn not in d:
                d[fn] = []

            xx = d[fn]
            data = (now, linesum, )
            xx.append(data)
            d[fn] = xx
        d.close()

    def list(self, listtype):
        """ list all keys in shelf in long or short format

        short format doesn't show datetime ob the changes
        """
        d = shelve.open(self.shelfname, flag='c')
        print listtype
        for key in d.keys():
            if listtype=='l':
                print("%s: %s" % (key, str(d[key])))
            else:
                values = ', '.join(map(lambda x:str(x[1]), d[key]))
                print("%s: %s" % (key, values))

        d.close()

    def get_lines(self, filename):
        """ runs check_line on every line and returns the sum of desired lines
        """
        fn = os.path.join(self.toplevel, filename)
        f = open(fn, 'r')
        linesum = sum(map(lambda x:check_line(x), f.readlines()))
        f.close()
        return linesum

    def initialize(self):
        """ init shelf with all files self.check returns True
        """
        file_list = []
        for root, dirs, files in os.walk(self.toplevel):
            # relpath removes repository path from filename
            file_list.extend(self.check(
                    [os.path.relpath(os.path.join(root, i), self.toplevel)
                     for i in files]))
        self.update(file_list)


def options():
    parser = argparse.ArgumentParser(description=
                                     'saves the progress in lines on tex files')

    parser.add_argument('--list', dest='list', default=False, action='store_true',
                        help='list all elements in the shelf')
    parser.add_argument('--list-type', dest='listtype', default='s',
                        help='list type: (s)hort or (l)ong')
    parser.add_argument('--init', dest='init', default=False, action='store_true',
                        help='init the shelf with all .tex files in the repository')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    opts = options()
    lp = LineProgress(opts)
