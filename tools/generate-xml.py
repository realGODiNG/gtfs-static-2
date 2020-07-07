import os
import requests
import string
import sys

# pip install beautifulsoup4
from bs4 import BeautifulSoup, NavigableString
# pip install lxml
from lxml import etree

def format(str):
	return ' '.join(str.split()).replace('( ', '(').replace(' )', ')').replace(' .', '.').replace(' ,', ',').replace(' ;', ';').replace(' :', ':')
def format_name(str):
	return ' '.join(word.capitalize() for word in format(str).replace('_', ' ').split(' '))
def format_structure(str):
	return ''.join(word.capitalize() for word in format(str).replace('-', ' ').split(' '))
def format_tag(str):
	return format(str).replace(' ', '_').lower()
def remove_extension(str):
	return ''.join(str.split('.')[:-1])

def construct_structures(soup):
	structures = etree.Element('structures')
	list = soup.find(attrs={'data-text':'Field types'}).findNext('ul')
	raw_structures = []
	for value in list.find_all('li', recursive=False):
		texts = value.get_text(separator=' ').split(' - ')
		raw_structures.append(format_structure(texts[0]))
		structure = etree.SubElement(structures, 'structure')
		attribute = etree.SubElement(structure, 'identifier')
		attribute.text = raw_structures[-1]
		attribute = etree.SubElement(structure, 'name')
		attribute.text = format_name(texts[0])
		attribute = etree.SubElement(structure, 'description')
		attribute.text = format(''.join(texts[1:]))
	# add trivial structures
	for raw_structure in ['Positive Integer', 'Non-null Integer', 'Positive Float', 'Float', 'Translation']:
		if raw_structure not in raw_structures:
			raw_structures.append(format_structure(raw_structure))
			structure = etree.SubElement(structures, 'structure')
			attribute = etree.SubElement(structure, 'identifier')
			attribute.text = raw_structures[-1]
			attribute = etree.SubElement(structure, 'name')
			attribute.text = format_name(raw_structure)
			attribute = etree.SubElement(structure, 'description')
	return raw_structures, structures
def construct_files(soup):
	files = etree.Element('files')
	table = soup.find(attrs={'data-text':'Dataset files'}).findNext('table')
	tags = [format_tag(tag.text) for tag in table.find('thead').find('tr').find_all('th', recursive=False)]
	tags[tags.index('defines')] = 'description'
	for row in table.find('tbody').find_all('tr', recursive=False):
		file = etree.SubElement(files, 'file')
		for tag, value in zip(tags, row.find_all('td', recursive=False)):
			attribute = etree.SubElement(file, tag)
			attribute.text = format(value.get_text(separator=' '))
	# add names to each file
	for file in files:
		attribute = etree.Element('name')
		attribute.text = format_name(remove_extension(file[0].text))
		file.insert(1, attribute)
	return files
def construct_fields_for_each_file(files, soup):
	for file in files:
		fields = etree.SubElement(file, 'fields')
		table = soup.find(attrs={'data-text':file[0].text}).findNext('table')
		tags = [format_tag(tag.text) for tag in table.find('thead').find('tr').find_all('th', recursive=False)]
		for row in table.find('tbody').find_all('tr', recursive=False):
			field = etree.SubElement(fields, 'field')
			for tag, value in zip(tags, row.find_all('td', recursive=False)):
				# rename field_name
				if tag == 'field_name':
					attribute = etree.SubElement(field, 'identifier')
				else:
					attribute = etree.SubElement(field, tag)
				for unwanted_table in value.find_all('table'):
					unwanted_div = soup.new_tag('div')
					unwanted_div.append(' (table has been removed) ')
					unwanted_table.insert_after(unwanted_div)
					unwanted_table.decompose()
				for li in value.find_all('li'):
					li.insert(0, NavigableString(' • '))
				attribute.text = format(value.get_text(separator=' '))
		# add names to each field
		for field in fields:
			attribute = etree.Element('name')
			attribute.text = format_name(field[0].text)
			field.insert(1, attribute)
	return files

def clean_structures_part_for_each_field(files, raw_structures):
	for element in files.iterfind('.//type'):
		structures = etree.Element('structures')
		data = []
		for value in element.text.replace(',or', ',').replace(', or', ',').replace(' or', ',').split(','):
			value = format(value)
			if len(value) != 0:
				data.append(value)
		for i in range(len(data)):
			data[i] = data[i].split('referencing')
			for j in range(len(data[i])):
				data[i][j] = format(data[i][j])
			if len(data[i]) == 1:
				if '.' in data[i][0]:
					data[i].insert(0, data[i-1][0])
				else:
					data[i].append('')
			data[i][0] = format_structure(data[i][0])
		for entry in data:
			if entry[0] not in raw_structures:
				raise Exception('found unknown structure: ' + element.text)
			structure = etree.SubElement(structures, 'structure')
			attribute = etree.SubElement(structure, 'identifier')
			attribute.text = entry[0]
			attribute = etree.SubElement(structure, 'reference')
			if len(entry[1]) != 0:
				attribute.text = entry[1]
		element.getparent().replace(element, structures)
	return files
def clean_required(files):
	for element in files.iterfind('.//required'):
		element.text = element.text.split(' ')[0].lower()
	return files
def clean_description(xml):
	for element in xml.iterfind('.//description'):
		if element.text:
			element.text = element.text.replace('•', '*')
	return xml
def construct_enumerations(path):
	enums = etree.Element('enumerations')
	for e in etree.parse(path).find('.//enumerations').iter('*'):
		if (e.tag != 'enumeration'):
			continue
		enum = etree.SubElement(enums, 'enumeration')
		skip = True
		for x in e.iter('*'):
			if (skip):
				skip = False
				continue
			attribute = etree.SubElement(enum, x.tag)
			attribute.text = x.text
	return enums

def create_xml():
	path = os.path.dirname(__file__) + '\\gtfs-static.xml'
	soup = BeautifulSoup(requests.get('https://developers.google.com/transit/gtfs/reference').content, 'html.parser')
	raw_structures, structures = construct_structures(soup)
	files = construct_files(soup)
	files = construct_fields_for_each_file(files, soup)
	files = clean_required(files)
	files = clean_structures_part_for_each_field(files, raw_structures)
	xml = etree.Element('gtfs_static')
	xml.insert(0, structures)
	xml.insert(1, construct_enumerations(os.path.dirname(__file__) + '\\gtfs-enumerations.xml'))
	xml.insert(2, files)
	xml = clean_description(xml)
	etree.ElementTree(xml).write(path, pretty_print=True, xml_declaration=True, encoding='utf-8')
create_xml()
