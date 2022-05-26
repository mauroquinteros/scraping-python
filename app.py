import os
import utils
import values
import xml.etree.ElementTree as ET
from ftplib import FTP
from zipfile import ZipFile


class ScrapingOFAC:
    def __init__(self, download_dir, download_file):
        self.dir = utils.get_download_dir(download_dir)
        self.file = download_file
        self.path = os.path.join(self.dir, download_file)

    def download_zipfile(self):
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

    def parser_xml(self):
        self.download_zipfile()
        self.xml = os.path.join(self.dir, values.OFAC_XMLNAME)
        with open(self.xml, "r") as xml:
            tree = ET.parse(xml)
            root = tree.getroot()


if __name__ == "__main__":
    scraping_ofac = ScrapingOFAC("download", values.OFAC_ZIPNAME)
    scraping_ofac.parser_xml()
