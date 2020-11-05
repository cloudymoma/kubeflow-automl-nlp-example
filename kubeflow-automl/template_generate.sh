#compile components
python dateset_component.py

#compile template
dsl-compile --py automl_nlp_pipeline_caip.py --output automl_nlp_pipeline_caip.tar.gz