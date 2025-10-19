# contacts/utils_storage.py
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from django.conf import settings

DATA_DIR = Path(settings.BASE_DIR) / 'data'
DATA_DIR.mkdir(exist_ok=True)

JSON_PATH = DATA_DIR / 'contacts.json'
XML_PATH = DATA_DIR / 'contacts.xml'

def read_json_contacts():
    if not JSON_PATH.exists():
        return []
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json_contacts(list_of_dicts):
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(list_of_dicts, f, ensure_ascii=False, indent=2)

def read_xml_contacts():
    if not XML_PATH.exists():
        return []
    tree = ET.parse(XML_PATH)
    root = tree.getroot()
    out = []
    for c in root.findall('contact'):
        d = {
            'name': c.findtext('name', ''),
            'email': c.findtext('email', ''),
            'phone': c.findtext('phone', ''),
            'notes': c.findtext('notes', ''),
        }
        out.append(d)
    return out

def write_xml_contacts(list_of_dicts):
    root = ET.Element('contacts')
    for d in list_of_dicts:
        c = ET.SubElement(root, 'contact')
        for k in ['name', 'email', 'phone', 'notes']:
            el = ET.SubElement(c, k)
            el.text = d.get(k, '')
    tree = ET.ElementTree(root)
    tree.write(XML_PATH, encoding='utf-8', xml_declaration=True)
