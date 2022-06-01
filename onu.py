import csv
import os
import utils
import urllib.request as urllib
import xml.etree.ElementTree as ET


class ScrapingONU:
    def __init__(self, download_dir, download_file, csv_file):
        self.file = download_file
        self.dir = utils.get_download_path(download_dir)
        self.csv_file = csv_file
        self.csv_path = os.path.join(self.dir, csv_file)
        self.headers = ["id", "firstName", "secondName", "type", "documentType", "documentNumber", "nationality"]

    def download_onu_file(self):
        self.onu_list = self.parse_xml()
        self.serialize_onu_list = self.get_serialize_onu_list()
        self.create_csv()

    def parse_xml(self):
        tree = ET.parse(urllib.urlopen(self.file))
        root = tree.getroot()

        onu_list = []
        for node in root:
            for sub_node in node:
                onu_item = self.get_onu_data(sub_node)
                onu_list.append(onu_item)
        return onu_list

    def get_onu_data(self, node):
        data_node = {}
        for sub_node in node:
            tag = sub_node.tag.lower()
            if sub_node.text:
                data_node[tag] = sub_node.text
            if len(sub_node) > 0 and sub_node.tag == "INDIVIDUAL_DOCUMENT":
                for grand_node in sub_node:
                    sub_tag = grand_node.tag.lower()
                    data_node[sub_tag] = grand_node.text
            if len(sub_node) > 0 and sub_node.tag == "INDIVIDUAL_ALIAS":
                if sub_node[0].tag == "QUALITY" and sub_node[0].text == "Good":
                    data_node[tag] = sub_node[1].text
            if len(sub_node) > 0 and sub_node.tag == "NATIONALITY":
                if sub_node[0].text:
                    data_node[tag] = sub_node[0].text
            if len(sub_node) > 0:
                for grand_node in sub_node:
                    if grand_node.text:
                        data_node[tag] = grand_node.text
        return data_node

    def get_serialize_onu_list(self):
        serialize_onu_list = []
        for onu_item in self.onu_list:
            serialize_onu = {
                "id": onu_item.get("dataid", "").upper().strip(),
                "firstName": onu_item.get("first_name", "").upper().strip(),
                "secondName": onu_item.get("second_name", "").upper().strip(),
                "type": onu_item.get("un_list_type", "").upper().strip(),
                "documentType": onu_item.get("type_of_document", "").upper().strip(),
                "documentNumber": onu_item.get("number", "").upper().strip(),
                "nationality": onu_item.get("nationality", "").upper().strip(),
            }
            serialize_onu_list.append(serialize_onu)
        return serialize_onu_list

    def create_csv(self):
        with open(self.csv_path, "w", encoding="UTF8", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.headers)
            writer.writeheader()
            writer.writerows(self.serialize_onu_list)
