from cioos_yaml_to_erddap.__main__ import cioos_yaml_to_erddap

from pathlib import Path

MODULE_PATH = Path(__file__).parent


def test_yaml_conversion_on_sample():
    xml = cioos_yaml_to_erddap(MODULE_PATH / ".." / "sample_record.yaml")
    assert xml, "xml is empty"
