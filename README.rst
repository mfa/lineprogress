Line progress hook
==================

About
-----

The goal of the line progress hook is visualize the lines I have written for my
phd thesis. Summarize lines added and removed, but only for the .tex files and
without empty lines and comments. 

Addional goals are:

 * playing with python shelve
 * usable as a hook for git


How it works
------------

1) Get list of files changed by current commit.

2) Calculate the lines of tex (without empty lines and comments) for the file.

3) Add filename, timestamp and lines to the shelf. The key is the filename, and
   the datastructure is a list of tuples, with the newest at the end. Every tuple
   is a timestamp and the current line count.


How to install
--------------

Copy (or symlink) the file to .git/hooks/pre-commit and ensure that it is
executable. 
