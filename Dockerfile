FROM python:3
COPY . .
RUN bash -c "pip install . && \
             python -m cioos_yaml_to_erddap ./sample_record.yaml"
