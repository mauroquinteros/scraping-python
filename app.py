import values
from ofac import ScrapingOFAC
from onu import ScrapingONU

if __name__ == "__main__":
    scraping_ofac = ScrapingOFAC("download", values.OFAC_ZIPNAME, "ofac.csv")
    scraping_ofac.download_ofac_file()

    scraping_onu = ScrapingONU("download", values.ONU_URL, "onu.csv")
    scraping_onu.download_onu_file()