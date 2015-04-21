#!/usr/bin/env python

# callblocker - blocking unwanted calls from your home phone
# Copyright (C) 2015-2015 Patrick Ammann <pammann@gmx.net>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#

from __future__ import print_function
import os, sys, argparse
import urllib, urllib2
import demjson


def error(*objs):
  print("ERROR: ", *objs, file=sys.stderr)
  sys.exit(-1)

def debug(*objs):
  #print("DEBUG: ", *objs, file=sys.stdout)
  return

def fetch_url(url, values):
  debug("fetch_url: '" + str(url)+"'")
  post_data = urllib.urlencode(values)
  req = urllib2.Request(url, post_data)
  response = urllib2.urlopen(req)
  return response.read()

def extract_callerName(name):
  matchObj = re.match(r"<a.*>(.*)</a>", name)
  if matchObj: name = matchObj.group(1)
  matchObj = re.match(r"(.*)<span.*>(.*)</span>", name)
  if matchObj: name = matchObj.group(1) + matchObj.group(2)
  return name

def lookup_number(number):
  # convert international number into local one
  number = "0"+number[3:]

  url = "http://www.dasschnelle.at/result/index/"
  values = {
    "bezirk" : 0,
    "boundsE" : 0,
    "boundsN" : 0,
    "boundsS" : 0,
    "boundsW" : 0,
    "mapsearch" : False,
    "orderBy" : "Standard",
    "pageNum" : 1,
    "resultsPerPage" : 20,
    "rubrik" : 0,
    "what" : number,
    "where" : ""
  }
  content = fetch_url(url, values)
  #debug(content)

  callerName = ""
  json = demjson.decode(content)
  for entry in json["entries"]:
    name = entry["name"]
    if len(callerName) == 0:
      callerName = name
    else:
      callerName += "; " + name
  return callerName

#
# main
#
def main(argv):
  parser = argparse.ArgumentParser(description="Online lookup via tel.search.ch")
  parser.add_argument("--number", help="number to be checked", required=True)
  args = parser.parse_args()

  # map number to correct URL
  if not args.number.startswith("+43"):
    error("Not a valid Austria number: " + args.number)

  callerName = lookup_number(args.number)

  # result in json format, if not found empty field
  print('{"name": "%s"}' % (callerName))

if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)
