# CIOOS YAML to ERDDAP

Converts a yaml metadata record to a xml snippet that can be pasted into a datasets.xml file. Outputs to stdout

## Installation

`pip install -e .`

## Running

`python -m cioos_yaml_to_erddap <filename>`

Example result:

```xml
<iso19115File>/your/waf/title_in_english_3f342.xml</iso19115File>
<addAttributes>
        <att name="comment">just in the main language</att>
        <att name="contributor_name">Shiela Jones</att>
        <att name="contributor_role">pointOfContact</att>
        <att name="date_created">2011-11-11</att>
        <att name="geospatial_lat_max">84</att>
        <att name="geospatial_lat_min">42</att>
        <att name="geospatial_lon_max">-141</att>
        <att name="geospatial_lon_min">-52</att>
        <att name="geospatial_vertical_max">10</att>
        <att name="institution">Bill's Pubishing,Environment Canada</att>
        <att name="instrument">123</att>
        <att name="keywords">oxygen,kw2 in English,kw1 in English,kw3 in English</att>
        <att name="platform">platform_name</att>
        <att name="summary">abstract in French</att>
        <att name="title">title in english</att>
</addAttributes>
```

## Test

Test that the code works using docker with -

`docker build .`
