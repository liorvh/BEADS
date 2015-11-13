#!/bin/env python
# Samuel Jero <sjero@purdue.edu>
# Results viewer
import sys
import strategies
import os
from os import listdir
from os.path import isfile, join
import re
from types import NoneType

prior_choice = None
prior_log_choice = "yes"
prior_raw_choice = "yes"
term_type = ""

#https://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

#https://stackoverflow.com/questions/3041986/python-command-line-yes-no-input
def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

def query_next():
	global prior_choice
	valid = {"next":'n', "n": 'n', "ne":'n', "nex":'n',
			}
	while True:
		sys.stdout.write("Option: [n/p/j/g/q] ")
		choice = raw_input().lower()
		if prior_choice is not None and choice == '':
			return prior_choice
		elif choice == "next" or choice == "n":
			prior_choice = ("n",0)
			return ("n",0)
		elif choice == "previous" or choice == "p":
			prior_choice = ("p",0)
			return ("p", 0)
		elif choice.find("jump") >= 0:
			mo = re.search("jump ([0-9]+)", choice)
			if type(mo) is not NoneType:
				prior_choice = ("j", int(mo.group(1)))
				return ("j", int(mo.group(1)))
		elif choice.find("j") >= 0:
			mo = re.search("j ([0-9]+)", choice)
			if type(mo) is not NoneType:
				prior_choice = ("j", int(mo.group(1)))
				return ("j", int(mo.group(1)))
		elif choice.find("goto") >= 0:
			mo = re.search("goto ([0-9]+)", choice)
			if type(mo) is not NoneType:
				prior_choice = ("g", int(mo.group(1)))
				return ("g", int(mo.group(1)))
		elif choice.find("g") >= 0:
			mo = re.search("g ([0-9]+)", choice)
			if type(mo) is not NoneType:
				prior_choice = ("g", int(mo.group(1)))
				return ("g", int(mo.group(1)))
		elif choice == "quit" or choice == "q":
			return ("q",0)
		else:
			sys.stdout.write("Invalid Response. Try Again.\n")

def handle_strat(line, ln_no, instfiles):
	global prior_log_choice, prior_raw_choice, term_type
	res = line[0]
	time = line[1]
	test = line[2]
	try:
		strat = eval(line[3])
	except exception as e:
		print e
		return
	reason = line[4]
	print "\n\n\n\n"
	print "Num: " + str(ln_no)
	for s in strat:
		print "Strategy: " + strategies.StrategyGenerator.pretty_print_strat(s)
	print "Time: " + time
	print "Result: " + res
	print "Reason: " + reason

	if query_yes_no("View Log?", prior_log_choice):
		prior_log_choice = "yes"
		found = 0
		for fname in instfiles:
			lnum = 0
			thresln = 0
			with open(fname, "r") as f:
				for line in f:
					lnum += 1
					if line.find("Thresholds") > 0:
							thresln = lnum
					if line.find(str(strat)) > 0:
						os.system(term_type + " -e 'vim +{0} -R {1}'".format(str(lnum), fname))
						if thresln > 0:
							os.system(term_type + " -e 'vim +{0} -R {1}'".format(str(thresln), fname))
							thresln = 0
						found += 1
					if found >= 2:
						break
	else:
		prior_log_choice = "no"
	
	if query_yes_no("View Raw?", prior_raw_choice):
		prior_raw_choice = "yes"
		print strat
	else:
		prior_raw_choice = "no"
	return

def main(args):
	global term_type
	if len(args) != 2:
		print "usage: viewer.py <directory>"
		sys.exit(1)

	if which("gnome-terminal") is not None:
		term_type = "gnome-terminal"
	elif which("mate-terminal") is not None:
		term_type = "mate-terminal"
	elif which("xterm") is not None:
		term_type = "xterm"
	else:
		print "No Supported Terminal Available"
		term_type = ""
	
	onlyfiles = [ f for f in listdir(args[1]) if isfile(join(args[1],f)) ]

	resfile = None
	try:	
		resfile = open(join(args[1],"results.log"), "r")
	except Exception as e:
		print "Error: could not open results.log. Not a log directory."
		sys.exit(1)

	instfiles = []
	for f in onlyfiles:
		mo = re.search("inst[0-9]+\.log", f)
		if type(mo) is not NoneType:
			instfiles.append(join(args[1],f))

	flines = resfile.readlines()
	resfile.close()
	i = 0
	fmt = ""
	while i < len(flines):
		if flines[i] == "#":
			i += 1
			continue
		try:
			fmt = eval(flines[i])
		except Exception as e:
			print e
			i += 1
			continue

		handle_strat(fmt, i, instfiles)

		r = query_next()
		if r[0] == "n":
			i+=1
		elif r[0] == "p":
			i-=1
		elif r[0] == "j":
			i = i + r[1]
		elif r[0] == "g":
			i = r[1]
		elif r[0] == "q":
			break
	return 0


if __name__ == "__main__":
	main(sys.argv)