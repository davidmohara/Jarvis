# Orthanc REST API

## What it is, in plain language

Orthanc is a lightweight, open-source DICOM server (C++). Its core value as a modeling reference: the entire system, storage included, is exposed and documented through one small REST API over its internal object hierarchy (Patients, Studies, Series, Instances).

## What it processes and doesn't

**Accepts:** any standard DICOM instance (`.dcm` files or DICOM streams) in the Part-10 file format or raw DICOM datasets. That covers all imaging modalities: CT, MR, ultrasound, X-ray/CR/DX, PET, nuclear medicine, secondary-capture screenshots, and non-image DICOM objects such as structured reports (SR), presentation states, radiotherapy objects (RTPLAN/RTDOSE), and non-image waveform data. Storage is file-based, with plugins for PostgreSQL, MySQL/MariaDB, or MongoDB indexing.

**Doesn't process:** compressed transfer syntaxes need codec plugins (JPEG 2000, JPEG-LS, and some MPEG video transfer syntaxes are only decodable with the paid/for-compliance Orthanc Pills or external tools; standard JPEG lossless and most uncompressed syntaxes work out of the box). It does not natively understand HL7 v2/FHIR (a community plugin adds HL7), it is not a report-generation or AI service, and it has no built-in de-identification beyond the anonymize endpoint, which remaps UIDs and patient fields but is not a certified PS3.15 de-identifier on its own. It renders frames server-side only as PNG/preview images, not as full diagnostic-grade viewer output.

## What the endpoints do

Key endpoint groups:

- **Upload**: `POST /instances` (multipart DICOM file upload), `POST /tools/create-dicom` (server-side synthetic DICOM creation)
- **Query / navigate**: `GET /patients`, `GET /patients/{id}`, `GET /studies?...`, plus a system-wide `POST /tools/find` search that mirrors DICOM C-FIND semantics
- **Retrieve**: `GET /instances/{id}/file` (original DICOM file), `GET /series/{id}/...` for bulk
- **Rendering (viewer support)**: `GET /instances/{id}/preview` (PNG render), `GET /instances/{id}/image-uint16`, andMatroska/AVI series export
- **DICOMweb plugin**: adds full STOW-RS, QIDO-RS, and WADO-RS under `/dicom-web/` (studies, series, instances, and rendered frames)
- **Routing / pipeline**: anonymization (`POST /patients/{id}/anonymize`), modification (`/modify`), and auto-routing rules via Lua scripting or the `OrthancPeers` forwarding API. This is the interesting part for an AI pipeline model: an instance lands, a rule fires, it gets anonymized and forwarded to a processing peer.

## API URL

- Self-hosted base URL: `http://<host>:8042/` (default port 8042 for REST, 4242 for DICOM protocol)
- Public demo server (read/write, unstable): `https://orthanc.uclouvain.be/demo/`
- Documentation: https://orthanc.uclouvain.be/book/users/rest.html
- DICOMweb plugin docs: https://orthanc.uclouvain.be/book/plugins/dicomweb.html

## How to access

1. **Fastest**: use the public demo server. Basic auth is documented on the demo page (username `demo`, password `demo` at time of writing, verify before relying on it).
   ```
   curl http://demo:demo@orthanc.uclouvain.be/demo/system
   curl http://demo:demo@orthanc.uclouvain.be/demo/instances | python3 -m json.tool
   ```
2. **Self-host**: Docker one-liner:
   ```
   docker run -p 4242:4242 -p 8042:8042 orthancteam/orthanc
   ```
   Enable the DICOMweb plugin by adding it to the `{"Plugins": [...]}` config. No auth by default, so set `"Authentication": {"Registered": true}` with users in `orthanc.json` before exposing beyond localhost.
3. **Explore interactively**: the demo server includes an embedded REST explorer UI at the root URL.

## MCP status

No official MCP endpoint. Community MCP wrappers exist (search GitHub for "orthanc mcp"), but none is maintained by the Orthanc project. If LLM access is the goal, wrap the REST API above in a thin MCP server: `system`, `tools/find`, `instances/{id}/file`, and `preview` are the four tools that cover most of it. A local mock of exactly that shape exists at `~/develop/improving/gehc/` (Orthanc MCP on port 8042).
