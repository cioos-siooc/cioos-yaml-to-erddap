#!/usr/bin/env python3

"""

Main function of this module, creates ACDD key/value from the appropriate values in the yaml

"""

from typing import Dict

from .utils import get_in_language, get_xml_filename


def yaml_to_erddap_dict(record: Dict) -> Dict:
    "Builds a dictionary of ACDD key/value pairs"

    language = record["metadata"]["language"]

    if not language:
        raise Exception("'language' cannot be empty")

    # Get all organizations
    organizations = []

    for role in record["contact"]:
        organization = role.get("organization", {}).get("name")
        if organization:
            organizations = list(set(organizations + [organization]))

    # Get all instruments
    instruments = []
    if record.get("platform"):
        if record["platform"]["instruments"]:
            for instrument in record["platform"]["instruments"]:
                if instrument["id"]:
                    instruments = list(set(instruments + [str(instrument["id"])]))

    bbox = record["spatial"].get("bbox")

    # get first publisher, ACDD seems to indicate this should be a single value
    publisher = {}

    creator = {}

    contributor_names = []
    contributor_roles = []
    creator_type = ""
    # publisher will be first 'publisher' or 'custodian' in contacts
    for contact in record["contact"]:
        if "publisher" in contact["roles"] or "custodian" in contact["roles"]:
            publisher = contact
            break

    # contributors will be list of each person or organization
    # with their first roles listed (in our system one person can have many roles)
    # but 'contributor_name' in ACDD doesnt really let you do this
    # 'custodian' is Metadata Contact, 'owner' is Data Contact

    for contact in record["contact"]:
        if not creator and "owner" in contact["roles"]:
            if "individual" in contact:
                creator = contact["individual"]
                # ACDD says to use one of 'person', 'group', 'institution', or 'position'
                creator_type = "person"
            elif "organization" in contact:
                creator = contact["organization"]
                creator_type = "institution"

        contributor_name = contact.get("individual", {}).get("name") or contact.get(
            "organization", {}
        ).get("name")

        contributor_names.append(contributor_name)

        # just getting the first role
        contributor_roles.append(contact["roles"][0])

    title = get_in_language(record["identification"]["title"], language)

    erddap_globals = {
        #    "infoUrl": "",  # from erddap
        #    "sourceUrl": "",  # from erddap
        #    "Conventions": "",
        #    "acknowledgement": "",
        #    "cdm_data_type": "",
        "comment": get_in_language(record["metadata"].get("comment"), language),
        "contributor_name": ",".join(contributor_names or []),
        "contributor_role": ",".join(contributor_roles or []),
        #    "coverage_content_type": "",
        "creator_email": creator.get("email"),
        "creator_institution": creator.get("organization", {}).get("name"),
        "creator_name": creator.get("name"),
        "creator_type": creator_type,
        "creator_url": creator.get("url"),
        "date_created": record["identification"].get("dates", {}).get("creation"),
        #    "date_issued": "",
        #    "date_metadata_modified": "",
        #    "date_modified": "",
        "geospatial_bounds": record["spatial"]["polygon"] if not bbox else None,
        #    "geospatial_bounds_crs": "",
        #    "geospatial_bounds_vertical_crs": "",
        "geospatial_lat_max": bbox[3] if bbox else None,
        "geospatial_lat_min": bbox[1] if bbox else None,
        "geospatial_lon_max": bbox[0] if bbox else None,
        "geospatial_lon_min": bbox[2] if bbox else None,
        "geospatial_vertical_max": record["spatial"]["vertical"][1],
        "geospatial_vertical_min": record["spatial"]["vertical"][0],
        #    "geospatial_vertical_positive": "",
        #    "geospatial_vertical_resolution": "",
        #    "geospatial_vertical_units": "",
        #    "history": "",
        #    "id": ""
        "institution": ",".join(organizations or []),
        "instrument": ",".join(instruments or []),
        #    "instrument_vocabulary": "",
        "keywords": ",".join(
            list(
                set(
                    record["identification"]["keywords"]["default"][language]
                    + record["identification"]["keywords"]["eov"][language]
                )
            )
        ),
        #    "keywords_vocabulary": "",
        "license": record.get("use_constraints", {}).get("licence", {}).get("title"),
        #    "metadata_link": "",
        #    "naming_authority": "",
        "platform": record.get("platform", {}).get("name"),
        #    "platform_vocabulary": "",
        #    "processing_level": "",
        #    "product_version": "",
        #    "program": "",
        #    "project": "",
        "publisher_email": publisher.get("organization", {}).get("email")
        or publisher.get("individual", {}).get("email"),
        "publisher_institution": publisher.get("organization", {}).get("name"),
        "publisher_name": publisher.get("individual", {}).get("name")
        or publisher.get("organization", {}).get("name"),
        #    "publisher_type": "",
        "publisher_url": publisher.get("organization", {}).get("url"),
        #    "references": "",
        #    "source": "",
        #    "standard_name_vocabulary": "",
        "summary": get_in_language(record["identification"]["abstract"], language),
        #    "time_coverage_duration": "",
        #    "time_coverage_end": "",
        #    "time_coverage_resolution": "",
        #    "time_coverage_start": "",
        "title": title,
        #    "Metadata_Convention": ""
    }
    return erddap_globals


def create_xml_snippet(record: Dict) -> str:
    """
    Converts a dictionary with ACDD key/value pairs into an XML string
    """

    xml_snippet = "<addAttributes>\n"

    erddap_globals = yaml_to_erddap_dict(record)

    uuid = record["metadata"]["identifier"]
    iso_xml_filename = f"{get_xml_filename(erddap_globals['title'],uuid)}.xml"
    xml_snippet += f"<iso19115File>/your/waf/{iso_xml_filename}</iso19115File>\n"

    for key, value in erddap_globals.items():
        if value:
            xml_snippet += f'\t<att name="{key}">{value}</att>' + "\n"

    xml_snippet += "</addAttributes>"

    return xml_snippet
