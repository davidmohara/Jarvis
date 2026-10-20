# dcm4chee Archive (dcm4chee-arc-light)

## What it is, in plain language

dcm4chee-arc-light is the enterprise-grade open-source PACS/VNA (Java, WildFly/JBoss based, from the dcm4che project). If Orthanc is the small system you can read in an afternoon, dcm4chee is the large one you model production behavior on.

## What it processes and doesn't

**Accepts:** the full range of DICOM objects across all modalities: CT, MR (including enhanced multi-frame MR), PET, ultrasound (including enhanced US), X-ray (CR/DX, including mammography DX with presentation states), radiotherapy objects (RTPLAN/RTDOSE/RTSTRUCT/RTIMAGE), structured reports (SR), ECG waveforms, and secondary capture. It handles compressed transfer syntaxes (JPEG, JPEG 2000, JPEG-LS, RLE) and converts between them on the fly. It also accepts HL7 v2 messages (ADT, ORM/ORU) alongside DICOM, updating and routing studies on patient events, plus UPS worklists for orchestrating external processors.

**Doesn't process:** it is not a rendering or AI service itself. It stores, routes, converts, and governs DICOM, but image analysis or inference must be external processors wired in via UPS worklists, DICOM C-STORE/REST routing, or IHE profiles (XDS-i, IOCM, ATNA). FHIR support exists (an XDS-to-FHIR bridge in newer versions) but it is not a FHIR server. It is Java-stack-heavy: LDAP for config, database for metadata, WildFly runtime; operationally demanding compared to Orthanc's single binary.

## What the endpoints do It is the most spec-complete DICOMweb implementation in open source and the best taxonomy baseline for modeling a production system.

Key endpoint groups (DICOMweb, REST):

- **STOW-RS** (store): `POST /aets/{AET}/rs/studies` — upload DICOM instances as multipart/related over HTTP
- **QIDO-RS** (query): `GET /aets/{AET}/rs/studies?PatientID=...&StudyDate=...` — REST queries with standard DICOM match keys, plus paging and `includefield` support
- **WADO-RS** (retrieve): `GET /aets/{AET}/rs/studies/{studyUID}` — full studies, series, or instances as multipart DICOM; `/rendered` variants return viewer-ready rendered images
- **WADO-URI** (legacy single-instance retrieval)
- **UPS-RS** (worklist):Unified Procedure Step REST endpoints for orchestrating processing jobs, the most relevant piece for an AI pipeline model: external processors claim work items, update progress, and complete with results
- **IOCM / object lifecycle**: rejection and restoration endpoints for governed deletion
- **Non-standard REST**: archive management, monitoring, and the IHE-ATNA audit trail integration

## API URL

- Wiki (primary docs, includes REST endpoint reference): https://github.com/dcm4che/dcm4chee-arc-light/wiki
- Swagger/OpenAPI spec ships with the server and is published in the repo (`dcm4chee-arc-aet` modules) for exact, version-pinned endpoint definitions
- Self-hosted base URL pattern: `http://<host>:8080/dcm4chee-arc/aets/{AET}/rs/...`

## How to access

1. **Self-host via Docker** (the practical path, there is no public demo):
   ```
   docker run -d --name ldap -p 389:389 dcm4che/slapd-dcm4chee
   docker run -d --name arc -p 8080:8080 -p 11112:11112 \
     --link ldap:ldap dcm4che/dcm4chee-arc-psql
   ```
   Requires a backing Postgres and its bundled LDAP for config (the Docker images wire this up).
2. **Test with DICOMweb** once running:
   ```
   curl -u admin:admin "http://localhost:8080/dcm4chee-arc/aets/DCM4CHEE/rs/studies?limit=10"
   curl -u admin:admin -X POST \
     "http://localhost:8080/dcm4chee-arc/aets/DCM4CHEE/rs/studies" \
     -H "Content-Type: multipart/related; type=application/dicom" \
     -F "dicom=@file.dcm;type=application/dicom"
   ```
3. **Auth**: HTTP basic against WildFly realm by default; production deployments front it with Keycloak/OIDC. DICOM AETITLE association auth (port 11112) is separate from REST auth.

## MCP status

No official MCP endpoint, and no widely adopted community wrapper (unlike Orthanc). Access path for LLM tooling is wrapping its DICOMweb endpoints: STOW, QIDO, WADO, and UPS map cleanly to MCP tools (`store_instances`, `search_studies`, `get_study`, `claim_workitem`).
