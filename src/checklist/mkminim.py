# !/usr/bin/env python

"""
mkminim.py - create Minim description from tabular checklist description
"""

__author__ = "Graham Klyne (GK@ACM.ORG)"
__copyright__ = "Copyright 2011-2013, University of Oxford"
__license__ = "MIT (http://opensource.org/licenses/MIT)"

import json
import requests
import sys
import os
import os.path
import re
import argparse
import logging
import csv

log = logging.getLogger(__name__)

# Make sure MiscUtils can be found on path
if __name__ == "__main__":
    sys.path.append(os.path.join(sys.path[0], ".."))

from rocommand import ro_utils

from iaeval.ro_minim import MINIM

from checklist.grid import GridCSV, GridExcel
from checklist import gridmatch
from checklist import checklist_template
from checklist.minim_graph import Minim_graph

VERSION = "0.2"


def mkminim(grid, baseuri=None):
    """
    Generate minim graph from supplied grid

    Returns (status,mgr) where mgr is RDF graph containing minim description,
    or None.
    """
    # Decode the grid
    try:
        (d, (r, c)) = checklist_template.checklist.match(grid, 0, 0)
    except Exception, e:
        print "Failed to parse minim table %s" % (e)
        return 2, None
    # Create RDF graph and initialize Minim graph creation
    mgr = Minim_graph(base=baseuri)
    # Add checklists to graph
    for cl in d["checklists"]:
        mgr.checklist(purpose=cl["purpose"], model=cl["model"], target='{+targetro}')
    # Add models to graph
    for cm in d["models"]:
        mgr.model(cm["modelid"],
                  [mgr.item(seq=mi["seq"], level=mi["level"], ruleid=mi["reqid"]) for mi in cm["items"]])
    # Open file with values for translation
    with open('checklist/values_mapping.json') as mapping:
        mapping = json.load(mapping)
    # Add requirement rules to graph
    for rq in d["requirements"]:
        if "foreach" in rq:
            if not (rq.get("exists") or rq.get("aggregates") or rq.get("islive") or
                    rq.get("min") or rq.get("max")):
                print "Missing 'exists', 'aggregates', 'islive', 'min' or 'max' in 'foreach' rule:"
                print "- " + repr(rq)
                return 2, None

            if rq['foreach'] in mapping['foreach']:
                rq['foreach'] = mapping['foreach'][rq['foreach']]
            elif (rq['foreach'] not in mapping['foreach']) and (rq['foreach'][0] != '?'):
                print 'The value in foreach field is not supported'
                return 2, None

            if rq['exists'] in mapping['exists']:
                rq['exists'] = mapping['exists'][rq['exists']]
            elif (rq['exists'] not in mapping['exists']) and (rq['exists'][0] != '?'):
                if 'aggregates_' in rq['exists']:
                    if not rq['exists'][11].isupper():
                        print "Type name should start with uppercase"
                        return 2, None
                    if requests.get('https://schema.org/%s' % rq['exists'][11:]).status_code is not 200:
                        print "Value in exists field cannot be found on schema"
                        return 2, None
                    query = '?ro ore:aggregates [ rdf:type sch:' + rq['exists'] + '|sch1:' + rq["exists"] + ']'
                    rq['exists'] = query
                else:
                    if not rq['exists'][0].islower() and rq['exists'][0] != '?':
                        print "Property name should start with lowercase"
                        return 2, None
                    if requests.get('https://schema.org/%s' % rq['exists']).status_code is not 200:
                        print "Value in exists field cannot be found on schema"
                        return 2, None
                    query = '?ro sch:' + rq["exists"] + '|sch1:' + rq["exists"] + ' ?ro' + rq["exists"]
                    rq['exists'] = query

            rule = mgr.rule(rq["reqid"],
                            ForEach=rq["foreach"],
                            ResultMod=rq.get("result_mod"),
                            Exists=rq.get("exists"),
                            Min=rq.get("min"),
                            Max=rq.get("max"),
                            Aggregates=rq.get("aggregates"),
                            IsLive=rq.get("islive"),
                            Show=rq.get("show"),
                            Pass=rq.get("pass"),
                            Fail=rq.get("fail"),
                            NoMatch=rq.get("miss"))
            mgr.collectlist(rule, MINIM.list, rq.get("collectall", []))
            mgr.collectlist(rule, MINIM.listpass, rq.get("collectpass", []))
            mgr.collectlist(rule, MINIM.listfail, rq.get("collectfail", []))
        elif "exists" in rq:
            if rq['exists'] in mapping['exists']:
                rq['exists'] = mapping['exists'][rq['exists']]
            elif (rq['exists'] not in mapping['exists']) and (rq['exists'][0] != '?'):
                if 'aggregates_' in rq['exists']:
                    if not rq['exists'][11].isupper():
                        print "Type name should start with uppercase"
                        return 2, None
                    if requests.get('https://schema.org/%s' % rq['exists'][11:]).status_code is not 200:
                        print "Value in exists field cannot be found on schema"
                        return 2, None
                    query = '?ro ore:aggregates [ rdf:type sch:' + rq['exists'] + '|sch1:' + rq["exists"] + ']'
                    rq['exists'] = query
                else:
                    if not rq['exists'][0].islower() and rq['exists'][0] != '?':
                        print "Property name should start with lowercase"
                        return 2, None
                    if requests.get('https://schema.org/%s' % rq['exists']).status_code is not 200:
                        print "Value in exists field cannot be found on schema"
                        return 2, None
                    query = '?ro sch:' + rq["exists"] + '|sch1:' + rq["exists"] + ' ?ro' + rq["exists"]
                    rq['exists'] = query

            mgr.rule(rq["reqid"],
                     Exists=rq["exists"],
                     Show=rq.get("show"),
                     Pass=rq.get("pass"),
                     Fail=rq.get("fail"),
                     NoMatch=rq.get("miss"))
        elif "command" in rq:
            mgr.rule(rq["reqid"],
                     Command=rq["command"],
                     Response=rq["response"],
                     Show=rq.get("show"),
                     Pass=rq.get("pass"),
                     Fail=rq.get("fail"),
                     NoMatch=rq.get("miss"))
    return 0, mgr


def run(configbase, filebase, options, progname):
    """
    Access input file as grid, and generate Minim
    """
    status = 0
    # open spreadsheet file as grid
    log.debug("%s: open grid %s" % (progname, options.checklist))
    gridfilename = os.path.join(filebase, options.checklist)
    log.debug("CSV file: %s" % gridfilename)
    base = ""
    if gridfilename.endswith(".csv"):
        try:
            with open(gridfilename, "rU") as csvfile:
                grid = GridCSV(csvfile, baseuri="", dialect=csv.excel)
        except IOError, e:
            print "Failed to open grid CSV file %s" % (e)
            return 2
    elif gridfilename.endswith(".xls"):
        try:
            grid = GridExcel(gridfilename, baseuri="")
        except IOError, e:
            print "Failed to open grid XLS file %s" % (e)
            return 2
    else:
        print "Unrecognized grid file type %s; must be CSV or XLS." % (gridfilename)
        return 2
    # Make minim file
    log.debug("mkminim %s" % (repr(options)))
    (status, mgr) = mkminim(grid, baseuri=grid.resolveUri(""))
    # Serialize graph to output stream
    if status == 0:
        mgr.serialize(sys.stdout, format=options.outformat)
    # Exit
    return status


def parseCommandArgs(argv):
    """
    Parse command line arguments

    prog -- program name from command line
    argv -- argument list from command line

    Returns a pair consisting of options specified as returned by
    OptionParser, and any remaining unparsed arguments.
    """
    # create a parser for the command line options
    parser = argparse.ArgumentParser(
        description="Generate Minim RDF file from tabular checklist description in xsl or csv format.",
        epilog="The RDF Graph generated is written to standard output.")
    # parser.add_argument("-a", "--all",
    #                     action="store_true",
    #                     dest="all",
    #                     default=False,
    #                     help="All, list all files, depends on the context")
    parser.add_argument("checklist", help="File containing checklist description in tabular format")
    parser.add_argument('--version', action='version', version='%(prog)s ' + VERSION)
    parser.add_argument("-o", "--output",
                        dest="outformat",
                        default="turtle",
                        help="Output format to generate: xml, turtle, n3, etc.  Default: 'turtle'.")
    parser.add_argument("--debug",
                        action="store_true",
                        dest="debug",
                        default=False,
                        help="Run with full debug output enabled")
    # parse command line now
    options = parser.parse_args(argv)
    log.debug("Options: %s" % (repr(options)))
    return options


def runCommand(configbase, filebase, argv):
    """
    Run program with supplied configuration base directory, Base directory
    from which to start looking for research objects, and arguments.

    This is called by main function (below), and also by test suite routines.

    Returns exit status.
    """
    options = parseCommandArgs(argv[1:])
    if not options or options.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    log.debug("runCommand: configbase %s, filebase %s, argv %s" % (configbase, filebase, repr(argv)))
    status = 1
    if options:
        progname = ro_utils.progname(argv)
        status = run(configbase, filebase, options, progname)
    return status


def runMain():
    """
    Main program transfer function for setup.py console script
    """
    userhome = os.path.expanduser("~")
    filebase = os.getcwd()
    return runCommand(userhome, filebase, sys.argv)


if __name__ == "__main__":
    """
    Program invoked from the command line.
    """
    status = runMain()
    sys.exit(status)
