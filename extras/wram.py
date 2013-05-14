# coding: utf-8

# RGBDS BSS section and constant parsing.

def read_bss_sections(bss):
	sections = []
	section = {}
	address = None
	if type(bss) is not list: bss = bss.split('\n')
	for line in bss:
		if 'SECTION' in line:
			if section: sections.append(section) # last section
			
			address = int(line.split('[')[1].split(']')[0].replace('$',''), 16)
			section = {
				'name': line.split('"')[1],
				#'type': line.split(',')[1].split('[')[0].strip(),
				'start': address,
				'labels': [],
			}
		elif ':' in line:
			# the only labels that don't use :s so far are enders,
			# which we typically don't want to end up in the output
			label = line.lstrip().split(':')[0]
			if ';' not in label:
				section['labels'] += [{'label': label, 'address': address, 'length': 0}]
		elif line.lstrip()[:3] == 'ds ':
			length = eval(line.lstrip()[3:].split(';')[0].replace('$','0x'))
			address += length
			if section['labels']:
				section['labels'][-1]['length'] += length
	sections.append(section)
	return sections

wram_sections = read_bss_sections(open('../wram.asm', 'r').readlines())


def make_wram_labels():
	wram_labels = {}
	for section in wram_sections:
		for label in section['labels']:
			if label['address'] not in wram_labels.keys():
				wram_labels[label['address']] = []
			wram_labels[label['address']] += [label['label']]
	return wram_labels

wram_labels = make_wram_labels()


def constants_to_dict(constants):
	return dict((eval(constant.split(';')[0].split('EQU')[1].replace('$','0x')), constant.split('EQU')[0].strip()) for constant in constants)

def scrape_constants(text):
	if type(text) is not list:
		text = text.split('\n')
	return constants_to_dict([line for line in text if 'EQU' in line and ';' not in line.split('EQU')[0]])

hram_constants = scrape_constants(open('../hram.asm','r').readlines())
gbhw_constants = scrape_constants(open('../gbhw.asm','r').readlines())

