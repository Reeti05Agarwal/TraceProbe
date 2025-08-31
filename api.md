API Endpoints

GET /api/cases

Queries Elasticsearch index cases.

Sorts by date_created.

Returns a list of cases.

POST /api/cases

Handles new case creation + file upload.

Expects: case_name, investigator_id, password, description, and a file.

Steps:

Validates inputs.

Creates a safe caseId (slugified name).

Renames uploaded file with unique timestamp.

Hashes password (bcrypt).

Saves metadata to Elasticsearch.

Creates a Kibana space for the case.

Imports a dashboard template into that space (dashboard_template.ndjson).

Creates an index pattern in Kibana (so dashboards work).

Calls the producer service to process the uploaded file.

Returns JSON response with case details.

GET /

Serves views/index.html (the UI form).