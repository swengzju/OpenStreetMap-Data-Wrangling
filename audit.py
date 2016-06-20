# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 16:48:40 2015

@author: wengsheng_
"""
"""
audit the OSMFILE and find the possible data-formating problems in that file. Use the variable 'mapping' to reflect the changes needed 
to fix the unexpected street types to the appropriate ones in the expected list. Print out the original street names and the new street
names after updating.
"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "austin_texas.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 'Building', 'Suite','South','U.S.', 'Texas',
            "Trail", "Parkway", "Commons", "Cove", "Circle", "Expressway", "Highway", "West", "North", 'East']

mapping = { "St": "Street", "st": "Street",
            "St.": "Street",
            'Ave': 'Avenue',
            'Ave.': 'Avenue',
            'Rd.': 'Road',
            'Rd': 'Road',
            'RD': 'Road',
            'Blvd': 'Boulevard', 'Blvd.,': 'Boulevard,',
            'Blvd.': 'Boulevard','Blvd,': 'Boulevard,',
            'Dr.': 'Drive',
            'Dr': 'Drive',
            'Pkwy': 'Parkway', 'Pkwy,': 'Parkway,',
            'PKWY': 'Parkway',
            'Cir': 'Circle',
            'CR': 'Circle',
            'Cv': 'Cove',
            'Ct': 'Court',
            'Ln': 'Lane',
            'Expwy': 'Expressway',
            'Hwy': 'Highway','HWY': 'Highway',
            'W': 'West', 'W,': 'West,',
            'W.': 'West',
            'N': 'North', 'IH35': 'IH 35', 'IH-35': 'IH 35', 'I-35': 'IH 35', 'IH35,': 'IH 35', 'I': 'IH', 'H': '',
            'N.': 'North', 'lane': 'Lane', 'brigadoon': 'Brigadoon',
            'E': 'East','RM': 'Ranch-to-Market Road', 'Ranch to Market Road': 'Ranch-to-Market Road',
            'E.': 'East', 'S': 'South', 'S.': 'South',
            'FM': 'Farm-to-Market Road','Farm to Market Road': 'Farm-to-Market Road', 'F.M.': 'Farm-to-Market Road', 'TX': 'Texas',
            'Ste.': 'Suite', 'Ste': 'Suite', 'Ste,': 'Suite,', 'STE': 'Suite', 'US': 'U.S.',
            'Bldg': 'Building', 'Bldg.': 'Building'}


def audit_street_type(street_types, street_name):
    """find all the streets that need to be changed"""
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    """audit the file and find the street elements"""
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    return street_types


def update_name(name, mapping):
    """fix the street names"""
    name_split = name.split(' ')
    name_new = ''
    for item in name_split:
        if item in mapping:
            item_new = mapping[item]
            name_new = name_new + item_new + ' '
        else:
            name_new = name_new + item + ' '
    name = name_new.strip(' ')
    return name


def test():
    st_types = audit(OSMFILE)
    #pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name

if __name__ == '__main__':
    test()