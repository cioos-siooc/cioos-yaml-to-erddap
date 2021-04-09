#!/usr/bin/env python3

"""

This file handles argparse and the actual writing of the XML.

Converts a record in yaml format into a chunk of <addAttributes>
to use in erddap. Outputs to STDOUT

"""

import argparse

import yaml

from .yaml_to_erddap_snippet import create_xml_snippet


def main():
    "Handles argparse stuff and calls create_xml_snippet()"
    parser = argparse.ArgumentParser(
        prog="metadata_xml", description="Convert yaml into CIOOS xml"
    )

    parser.add_argument(
        "-f",
        type=str,
        dest="yaml_file",
        help="Enter filename of yaml file.",
        required=True,
    )

    args = parser.parse_args()
    filename = args.yaml_file

    # write xml snippet
    with open(filename) as stream:
        record = yaml.safe_load(stream)
        xml = create_xml_snippet(record)
        print(xml)


if __name__ == "__main__":
    main()
