# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 17:37:24 2015

@author: wengsheng_
"""
"""
Wrangle the data and transform the shape of the data into the correct model. Save the data in a new file so that we can do
mongoimport later on to import the shaped data into MongoDB. Update the street names before saving them into JSON.
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import re
import codecs
import json


problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

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
    

def shape_element(element):
    """transform the shape of the data into the correct format"""
    node = {}
    if element.tag == "node" or element.tag == "way" :
        key_list = element.keys() # http://discussions.udacity.com/t/data-wrangling-lesson-6-preparing-for-database-exercise-lat-key-error/8166/2
        node['type'] = element.tag
        if 'id' in key_list:
            node['id'] = element.attrib['id']
        if 'visible' in key_list:
            node['visible'] = element.attrib['visible']
        created_dict = {}
        if 'version' in key_list:
            created_dict['version'] = element.attrib['version']
        if 'changeset' in key_list: 
            created_dict['changeset'] = element.attrib['changeset']
        if 'user' in key_list: 
            created_dict['user'] = element.attrib['user']
        if 'uid' in key_list: 
            created_dict['uid'] = element.attrib['uid']
        if 'timestamp' in key_list: 
            created_dict['timestamp'] = element.attrib['timestamp']
        if created_dict != {}:
            node['created'] = created_dict
        if 'lat' in key_list and 'lon' in key_list:
            node['pos'] = [float(element.attrib['lat']), float(element.attrib['lon'])]
        address_dict = {}
        ref_set = []
        for tag in element.iter('tag'):
            if problemchars.match(tag.attrib['k']):
                continue
            elif tag.attrib['k'][0:5] == 'addr:' and ':' in tag.attrib['k'][5: len(tag.attrib['k'])]:
                continue
            elif tag.attrib['k'][0:5] == 'addr:':
                address_type = tag.attrib['k'][5: len(tag.attrib['k'])]
                new_name = update_name(tag.attrib['v'], mapping)
                address_dict[address_type] = new_name
            else:
                node[tag.attrib['k']] = tag.attrib['v']
        if address_dict != {}:
            node['address'] = address_dict
        for nd in element.iter('nd'):
            ref_set.append(nd.attrib['ref'])
        if ref_set != []:
            node['node_refs'] = ref_set
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    """Store the data into JSON file"""
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    data = process_map('austin_texas.osm', False)
    print len(data)
    
if __name__ == "__main__":
    test()