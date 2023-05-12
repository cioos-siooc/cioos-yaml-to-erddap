#!/usr/bin/env python3

"""

Main function of this module, creates ACDD key/value from the appropriate values in the yaml

"""

from typing import Dict

from cioos_yaml_to_erddap.licenses import license_urls
from cioos_yaml_to_erddap.utils import get_in_language, get_xml_filename


def yaml_to_erddap_dict(record: Dict) -> Dict:
    "Builds a dictionary of ACDD key/value pairs"

    def _get_contact(contact, info):
        """Priotorize individual contacts over organization"""
        return contact.get("individual", {}).get(info) or contact.get(
            "organization", {}
        ).get(info)

    def _get_contributors_name(contact):
        if "individual" in contact and "organization" in contact:
            return (
                f"{contact['individual']['name']} [{contact['organization']['name']}]"
            )

        return contact.get("individual", {}).get("name") or contact.get(
            "organization", {}
        ).get("name")

    # Sort language
    language = record["metadata"]["language"]
    language_alt = "fr" if language == "fr" else "en"
    if not language:
        raise Exception("'language' cannot be empty")

    # TODO: reference the original cioos level? Not just national?
    doi = record["identification"].get("identifier")
    doi_url = doi if not doi or "doi.org" in doi else f"http://doi.org/{doi}"
    metadata_link = (
        "https://catalogue.cioos.ca/en/dataset/ca-cioos_"
        + record["metadata"]["identifier"],
    )

    # Contacts
    # creator
    creator_contact = [
        contact for contact in record["contact"] if "owner" in contact["roles"]
    ]
    if not creator_contact:
        raise Exception("No contact is associated with the role: owner")
    # Consider the first publisher listed
    creator_contact = creator_contact[0]
    institution = creator_contact["organization"]["name"]
    creator = {
        "creator_name": _get_contact(creator_contact, "name"),
        "creator_email": _get_contact(creator_contact, "email"),
        "creator_url": _get_contact(creator_contact, "url"),
        "creator_address": _get_contact(creator_contact, "address"),
        "creator_city": _get_contact(creator_contact, "city"),
        "creator_country": _get_contact(creator_contact, "country"),
        "creator_ror": _get_contact(creator_contact, "ror"),
        "creator_type": "person" if "individual" in creator_contact else "institution",
        "creator_institution": creator_contact.get("organization", {}).get("name"),
    }

    # publisher
    publisher_contact = [
        contact for contact in record["contact"] if "distributor" in contact["roles"]
    ]
    if not publisher_contact:
        raise Exception("No contact is associated with the role: distributor")
    # Consider the first publisher listed
    publisher_contact = publisher_contact[0]
    publisher = {
        "publisher_name": _get_contact(publisher_contact, "name"),
        "publisher_email": _get_contact(publisher_contact, "email"),
        "publisher_url": _get_contact(publisher_contact, "url"),
        "publisher_address": _get_contact(publisher_contact, "address"),
        "publisher_city": _get_contact(publisher_contact, "city"),
        "publisher_country": _get_contact(publisher_contact, "country"),
        "publisher_ror": _get_contact(publisher_contact, "ror"),
        "publisher_type": "person"
        if "individual" in publisher_contact
        else "institution",
        "publisher_institution": publisher_contact.get("organization", {}).get("name"),
    }

    # contributor
    contributors = {
        "contributor_name": ";".join(
            [_get_contributors_name(contact) for contact in record["contact"]]
        ),
        "contributor_role": ";".join(
            [",".join(contact["roles"]) for contact in record["contact"]]
        ),
    }

    # Get all instruments
    instruments = []
    if record.get("platform"):
        if record["platform"].get("instruments"):
            for instrument in record["platform"]["instruments"]:
                if instrument["id"]:
                    instruments = list(set(instruments + [str(instrument["id"])]))

    platform_l06 = record.get("platform", {}).get("type")
    bbox = record["spatial"]["bbox"]

    erddap_globals = {
        #    "sourceUrl": "",  # from erddap
        "institution": institution,
        "title": get_in_language(record["identification"]["title"], language),
        f"title_{language_alt}": get_in_language(
            record["identification"]["title"], language_alt
        ),
        "product_version": record["identification"].get("edition"),
        #    "program": "",
        #    "processing_level": "",
        #    "source": "",
        "project": record["identification"].get("project")
        and ",".join(record["identification"].get("project")),
        "date_created": record["identification"].get("dates", {}).get("creation"),
        "date_issued": record["metadata"].get("publication"),
        #   "date_metadata_modified": "",
        "date_modified": record["metadata"].get("revision"),
        "summary": get_in_language(record["identification"]["abstract"], language),
        f"summary_{language_alt}": get_in_language(
            record["identification"]["abstract"], language_alt
        ),
        **creator,
        **publisher,
        **contributors,
        "comment": get_in_language(record["metadata"].get("comment"), language),
        f"comment_{language_alt}": get_in_language(
            record["metadata"].get("comment"), language_alt
        ),
        "history": record["metadata"].get("history"),
        #    "acknowledgement": "",
        "license": license_urls.get(
            record["metadata"].get("use_constraints", {}).get("licence", {}).get("code")
        ),
        "limitations": get_in_language(
            record["metadata"].get("use_constraints", {}).get("limitations"), language
        ),
        f"limitations_{language_alt}": get_in_language(
            record["metadata"].get("use_constraints", {}).get("limitations"),
            language_alt,
        ),
        "infoUrl": metadata_link,
        "metadata_link": metadata_link,
        "references": doi_url or metadata_link,
        "doi": record["identification"].get("identifier"),
        "id": doi or record["metadata"]["identifier"],
        "naming_authority": "org.doi" if doi else record["metadata"]["naming_autority"],
        "Conventions": "ACDD-1.3,CF-1.6",
        "geospatial_bounds": record["spatial"]["polygon"] if not bbox else None,
        #    "geospatial_bounds_crs": "",
        #    "geospatial_bounds_vertical_crs": "",
        # "geospatial_lat_max": bbox[3] if bbox else None,
        # "geospatial_lat_min": bbox[1] if bbox else None,
        # "geospatial_lon_max": bbox[0] if bbox else None,
        # "geospatial_lon_min": bbox[2] if bbox else None,
        # "geospatial_vertical_max": record["spatial"]["vertical"][1],
        # "geospatial_vertical_min": record["spatial"]["vertical"][0],
        #    "geospatial_vertical_positive": "",
        #    "geospatial_vertical_resolution": "",
        #    "geospatial_vertical_units": "",
        "instrument": ",".join(instruments or []),
        #    "instrument_vocabulary": "",
        "platform": platform_l06,
        "platform_vocabulary": platform_l06
        and "http://vocab.nerc.ac.uk/collection/L06/current/",
        "keywords": ",".join(
            list(
                set(
                    record["identification"]["keywords"]["default"][language]
                    + record["identification"]["keywords"]["eov"][language]
                )
            )
        ),
        f"keywords_{language_alt}": ",".join(
            list(
                set(
                    record["identification"]["keywords"]["default"].get(
                        language_alt, []
                    )
                    + record["identification"]["keywords"]["eov"].get(language_alt, [])
                )
            )
        ),
        "keywords_vocabulary": "GOOS: Global Ocean Observing System essential ocean variables",
        #    "standard_name_vocabulary": "",
        #    "time_coverage_duration": "",
        #    "time_coverage_end": "",
        #    "time_coverage_resolution": "",
        #    "time_coverage_start": "",
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
