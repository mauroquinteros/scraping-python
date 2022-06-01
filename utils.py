import os


def get_download_path(path: str):
    if not os.path.isdir(path):
        os.mkdir(path)
    return os.path.abspath(path)


def get_tag_element(xml_element):
    split_tag = xml_element.tag.split("}")
    return split_tag[1]
