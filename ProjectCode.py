import re
import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict
import json


street_type_re=re.compile(r'\b\S+\.?$',re.IGNORECASE) #character nospace . (0/1) end

expected=["Street", "Avenue", "Alley","Boulevard","Broadway" "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons","Path","Plaza","Terrace","Walk","Way","Circle","Crescent","Expressway","Highway","Loop","Terminal"]

def audit_street_type(street_types,street_name):
    m=street_type_re.search(street_name)
    if m:
        street_type=m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    return (elem.attrib['k']=="addr:street")

def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                #print 'qewqe'
                #print tag
                if is_street_name(tag):
                    #print tag.attrib['v'] street name
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    #print "!!!!!!!"
    #print street_types
    return dict(street_types)


# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "Ave":"Avenue",
           "AVENUE":"Avenue",
           "AVenue":"Avenue",
           "Ave.":"Avenue",
           "AVE.":"Avenue",
           "Ave": "Avenue",
           "Ave,": "Avenue",
           "Avenue,": "Avenue",
           "Avene": "Avenue",
           "Aveneu": "Avenue",
           'Avenue,#392':"Avenue",
           "ave":"Avenue",
           "avenue":"Avenue",
           "Blv.":"Boulevard",
           "Blvd":"Boulevard",
           "Blvd.":"Boulevard",
           "Blvd":"Boulevard",
           "boulevard":"Boulevard",
           "Broadwat": "Broadway",
           "Broadway.":"Broadway",
           "CIRCLE":"Circle",
           "Cir": "Circle",
           "Cres":"Crescent",
           "DRIVE":"Drive",
           "drive":"Drive",
           "Dr":"Drive",
           "Dr.":"Drive",
           "Driveway":"Drive",
           "E":"East",
            "EAST":"East",
           'Expy':"Expressway",
           "Hwy":"Highway",
           'LANE':"Lane",
           "lane":"Lane",
            "N":"North",
           "north":"North",
           'PARKWAY':"Parkway",
           'Pkwy': "Parkway",
           'Pky': "Parkway",
           "PLACE":"Place",
           "Pl": "Place",
           "Plz":"Place",
           'PLAZA':"Plaza",
           'ROAD':"Road",
           'Rd':"Road",
           'Rd.':"Road",
           "road": "Road",
           "S":"South",
           "SOUTH":"South",
           'ST':"Street",
           "st":"Street",
           "STREET":"Street",
           'st':"Street",
           'St.':"Street",
           'Steet':"Street",
           "street":"Street",
           'Streeet':"Street",
           'Ter':"Terminal",
          'Tunpike':'Turnpike',
           "Tunrpike": 'Turnpike',
           "Turnlike": 'Turnpike',
           "W":"West",
           "WEST":"West",
           "west":"West",
           "WAY":"Way"
            }

def update_street_name(name, mapping):

    m=street_type_re.search(name)
    better_name=name  # make sure that other name that not in the mapping are in the result
    if m:
        if m.group in mapping.keys():
            #print m.group()
            better_street_type=mapping[m.group()]
            better_name=street_type_re.sub(better_street_type,name)

    return better_name

city_name_re=re.compile(r'\b\S+\.?$',re.IGNORECASE) #character nospace . (0/1) end

def is_city_name(elem):
    return (elem.attrib['k']=="addr:city")

# update the city name

city_mapping={
    "new york": "New York City",
    "New York city": "New York City",
    "york":"New York",
    "CITY": "New York City",
    "CIty": "New York City",
    "brooklyn":"Brooklyn",
    "Brookklyn": "Brooklyn",
    "BrookLyn": "Brooklyn",
    "Bronx, NY": "Bronx",
    "bloomfield":"Bloomfield",
    "caldwell":"West Caldwell",
    "flushing": "Flushing",
    "FARMINGDALE": "Farmingdale",
    "island":"Staten Island",
    'linden':"Linden",
    "northport":"Northport",
    "new rochelle": "New Rochelle",
    "ny":"New York",
    "Lake":"Lakes",
    'plaine':"White Plaine",
    "PISCATAWAY":"Piscataway",
    "Queens)":"Queens",
    "queens":"Queens",
    "ridgewood":"Ridgewood",
    "rochelle":"New Rochelle",
    "stamford":"Stamford",
    "vernon":'Mount Vernon'
}

def update_city_name(name, city_mapping):
    m=city_name_re.search(name)
    update=name
    if m:
        if m.group in city_mapping.keys():
            better_city_name=street_mapping[m.group]
            update=city_name_re.sub(better_city_name,name)
    return update


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
lower_dot = re.compile(r'^([a-z]|_)*\.([a-z]|_)*$')

CREATED = ["version", "changeset", "timestamp", "user", "uid"]


def shape_element(element):
    node = {}
    # go through the node attribute
    if element.tag == 'node' or element.tag == "way":
        for attrib, value in element.attrib.items():
            node["type"] = element.tag
            if attrib in CREATED:
                if "created" not in node.keys():
                    node['created'] = {}
                node['created'][attrib] = value
            elif attrib == 'lat' or attrib == 'lon':
                if "pos" not in node.keys():
                    node['pos'] = {}
                node['pos'][attrib] = float(value)
            else:
                node[attrib] = value

            for tag in element.iter("tag"):
                tag_key = tag.attrib['k']
                tag_value = tag.attrib['v']

                if PROBLEMCHARS.match(tag_key):
                    continue
                elif tag_key.startswith("addr:"):
                    if "address" not in node.keys():
                        node["address"] = {}
                    addr_key = tag_key[len("addr:"):]
                    if lower_colon.match(addr_key):  # if there is more than : in the tag_key
                        continue
                    elif addr_key == 'city':
                        node["address"][addr_key] = update_city_name(tag_value, city_mapping)
                        # node["address"][addr_key]=tag_value
                    elif addr_key == 'street':
                        node["address"][addr_key] = update_street_name(tag_value, mapping)
                    else:
                        node["address"][addr_key] = tag_value
                elif lower_colon.match(tag_key):
                    node[tag_key] = tag_value
                elif lower_dot.match(tag_key):
                    a, b = tag_key.split('.')
                    if a not in node.keys():
                        node[a] = {}
                    node[a][b] = tag_value
                else:
                    node[tag_key] = tag_value

            for nd in element.iter("nd"):
                if "node_refs" not in node.keys():
                    node["node_refs"] = []
                node["node_refs"].append(nd.attrib['ref'])

        return node





def process_map(file_in):
    filename = "{0}-123.json".format(file_in)
    data = []
    with open(filename, 'wb') as outfile:
        for _, element in ET.iterparse(file_in):
            dic = shape_element(element)
            if dic:
                data.append(dic)
        json.dump(data, outfile)
    return data


data=process_map('new-york.osm')

