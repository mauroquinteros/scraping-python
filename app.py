import csv
import os
import utils
import values
import xml.etree.ElementTree as ET
from ftplib import FTP
from zipfile import ZipFile


class ScrapingOFAC:
    def __init__(self, download_dir, download_file, csv_file):
        self.dir = utils.get_download_dir(download_dir)
        self.file = download_file
        self.csv_file = csv_file
        self.path = os.path.join(self.dir, download_file)
        self.csv_path = os.path.join(self.dir, csv_file)
        self.headers = ["id", "firstName", "lastName", "title", "type", "remarks", "program"]

    def download_ofac_file(self):
        self.download_ftp_zipfile()
        self.xml = os.path.join(self.dir, values.OFAC_XMLNAME)
        self.ofac_list = self.parse_xml()
        self.serialize_ofac_list = self.get_serialize_ofac_data()
        self.create_csv()

    def download_ftp_zipfile(self):
        ftp = FTP(values.OFAC_FTP_URL)
        ftp.login()
        ftp.cwd(values.OFAC_FTP_DIR)

        with open(self.path, "wb") as fp:
            ftp.retrbinary(f"RETR {self.file}", fp.write)

        with ZipFile(self.path, "r") as zipfile:
            file_list = zipfile.namelist()
            for fl in file_list:
                if fl == values.OFAC_XMLNAME:
                    zipfile.extract(fl, self.dir)

    def parse_xml(self):
        ofac_list = []
        with open(self.xml, "r") as xml:
            tree = ET.parse(xml)
            root = tree.getroot()
            for index, child in enumerate(root):
                if index != 0:
                    ofact_item = self.get_ofac_data(child)
                    ofac_list.append(ofact_item)
        return ofac_list

    def get_ofac_data(self, node):
        data_node = {}
        for sub_node in node:
            tag_name = utils.get_tag_element(sub_node)
            if len(sub_node) == 0:
                data_node[tag_name] = sub_node.text
            elif len(sub_node) > 0 and tag_name == "programList":
                data_node[tag_name] = [grand_node.text for grand_node in sub_node]
            elif len(sub_node) > 0 and tag_name in ["idList", "akaList", "addressList"]:
                grand_node_list = []
                for grand_node in sub_node:
                    desc_node_data = {}
                    for desc_node in grand_node:
                        desc_tag_name = utils.get_tag_element(desc_node)
                        desc_node_data[desc_tag_name] = desc_node.text
                    grand_node_list.append(desc_node_data)
                    data_node[tag_name] = grand_node_list
        return data_node

    def get_serialize_ofac_data(self):
        serialize_ofac_list = []
        for ofac_item in self.ofac_list:
            serialize_ofac = {
                "id": ofac_item.get("uid", "").upper(),
                "firstName": ofac_item.get("firstName", "").upper(),
                "lastName": ofac_item.get("lastName", "").upper(),
                "title": ofac_item.get("title", "").upper(),
                "type": ofac_item.get("sdnType", "").upper(),
                "remarks": ofac_item.get("remarks", "").upper(),
            }

            if ofac_item.get("programList", False):
                program_list = [program.upper() for program in ofac_item.get("programList", [])]
                program_list = " - ".join(program_list)
                serialize_ofac["program"] = program_list
            serialize_ofac_list.append(serialize_ofac)
        return serialize_ofac_list

    def create_csv(self):
        with open(self.csv_path, "w", encoding="UTF8", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.headers)
            writer.writeheader()
            writer.writerows(self.serialize_ofac_list)


if __name__ == "__main__":
    scraping_ofac = ScrapingOFAC("download", values.OFAC_ZIPNAME, "ofac.csv")
    scraping_ofac.download_ofac_file()
