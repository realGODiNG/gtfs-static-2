import os
import requests
import string
import sys

# pip install lxml
from lxml import etree

def create_txt():
	xml = etree.parse(os.path.dirname(__file__) + '\\gtfs-static.xml')
	txt = ''
	for line in etree.tostring(xml, pretty_print=True, xml_declaration=True, encoding='utf8').decode('utf8').split('\n'):
		txt += line.lstrip()
	txt = txt.replace('"', '\\"')
	file = open(os.path.dirname(__file__) + '\\gtfs-static.txt', 'w')
	file.write(txt)
	file.close()
create_txt()
