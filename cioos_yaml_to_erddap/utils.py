#!/usr/bin/env python3


def get_in_language(val, language):
    """
    Handle optionally bilingual fields that are written without
    specifying language. eg could handle
    comment:"my comment" or comment: { en:"my comment" }
    """

    if isinstance(val, str):
        return val
    if isinstance(val, dict):
        return val[language]

    return None


def get_xml_filename(title, identifier):
    """
    Figure out what the XML filename would be called based on the sanitized title
    and UUID. Eg hakai_institute_juvenile_salmo_50f11.xml
    """
    name = title[0:30] + "_" + identifier[0:5]

    char_list = [
        character if character.isalnum() else "_" for character in name.strip().lower()
    ]
    name = "".join(char_list)

    return name
