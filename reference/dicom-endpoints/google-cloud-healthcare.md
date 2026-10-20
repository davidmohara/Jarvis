# Google Cloud Healthcare API: DICOM stores

## What it is, in plain language

Google's commercial DICOM implementation, the cleanest spec-conformant DICOMweb service among the cloud vendors. DICOM data lives in named DICOM stores inside a dataset, and all interaction is REST.

## What it processes and doesn't

**Accepts:** standard DICOM instances via STOW-RS or the `import` API from GCS buckets, across all imaging modalities: CT, MR, PET, ultrasound, X-ray/CR/DX, nuclear medicine, and secondary capture. Handles most compressed and uncompressed transfer syntaxes, but a few transfer syntaxes (notably MPEG video and a handful of rare lossless ones) are rejected at ingestion; check Google's published list of supported transfer syntaxes before ingesting video-ultrasound data. Also stores non-image DICOM (SR, presentation states) as long as they are valid instances.

**Metadata beyond DICOM:** all standard DICOM attributes are indexed and searchable, plus custom "revertible" tag indexing can be added; metadata can be exported to BigQuery for analytics.

**Doesn't process:** it stores and serves DICOM, it does not interpret it. There is no inference, no report generation, no image enhancement, and de-identification is metadata-level (tag modification per PS3.15), not burned-in-pixel removal (Google explicitly notes it does not remove burned-in PHI from pixel data, which matters for ultrasound and secondary-capture images that often have patient names burned into the frame). Pixel-level processing must be your pipeline. Rendering endpoints produce basic rendered frames, not diagnostic-grade viewer output.

## What the endpoints do

Key endpoint groups (REST, `healthcare.googleapis.com`):

- **Store (STOW-RS)**: `POST https://healthcare.googleapis.com/v1/projects/{project}/locations/{loc}/datasets/{ds}/dicomStores/{store}/dicomWeb/studies` — multipart DICOM upload; supports `application/dicom+json` metadata-only ingestion and bulk-data references
- **Query (QIDO-RS)**: `GET .../dicomWeb/studies?PatientID=...` — JSON instance/study/series search
- **Retrieve (WADO-RS/URI)**: `GET .../dicomWeb/studies/{studyUID}` — full DICOM or `application/dicom+json`; `.../rendered` endpoints return viewer-ready rendered frames
- **De-identify** (the standout for AI pipeline modeling): `POST .../datasets/{ds}:deidentify` — server-side de-identification of entire stores into a new store, using DICOM PS3.15 de-id profiles with per-tag configs (keep, remove, regenerate UIDs, shift dates)
- **Notifications**: Pub/Sub topics fire on `DicomInstanceStored` events — the pattern worth stealing for triggering an inference pipeline on ingest
- **View metadata**: `GET .../dicomStores/{store}:exportMetadata` (BigQuery metadata export for analytics)
- **FHIR store siblings** in the same API enable DICOM-to-FHIR linkage if a clinical-records side is ever needed

## API URL

- Docs (how-to, DICOM): https://cloud.google.com/healthcare-api/docs/how-tos/dicom
- REST API reference: https://cloud.google.com/healthcare-api/docs/reference/rest/v1/projects.locations.datasets
- Client libraries: Python/Java/Go on PyPI/Maven (package `google-cloud-healthcare`)

## How to access

1. **Prerequisites**: GCP project with the Cloud Healthcare API enabled, billing active. DICOM data is PHI-relevant: sign the Google Cloud HIPAA BAA (available in Cloud Console, requires a support plan) before storing real patient data.
2. **Auth**: standard Google OAuth2. `gcloud auth application-default login` for local testing, or a service account with `roles/healthcare.dicomeViewer` (read) / `roles/healthcare.dicomEditor` (read/write) on the store.
3. **Create a store, then use DICOMweb**:
   ```
   gcloud healthcare dicom-stores create my-store --dataset=my-dataset --location=us-central1
   curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
     -X POST -H "Content-Type: multipart/related; type=application/dicom" \
     -F "dicom=@file.dcm" \
     "https://healthcare.googleapis.com/v1/projects/PROJ/locations/us-central1/datasets/my-dataset/dicomStores/my-store/dicomWeb/studies"
   ```
4. **Cost model**: storage per GB plus API operations (A/B/C tier pricing by operation cost), so a de-identify-then-inference flow should be architected with operation counts in mind.

## MCP status

No official MCP endpoint. Google's ecosystem exposes this via REST and client libraries only. An MCP wrapper would surface `store_instances`, `search_instances`, `get_study_rendered`, and `deidentify` as tools, with OAuth handled by the host. A local mock of that shape exists at `~/develop/improving/gehc/` (Google MCP on port 8443).
