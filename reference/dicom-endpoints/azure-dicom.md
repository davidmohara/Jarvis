# Azure Health Data Services: DICOM service

## What it is, in plain language

Microsoft's managed DICOM service inside Azure Health Data Services, the DICOM service is a cloud DICOM store that speaks DICOMweb (STOW-RS, QIDO-RS, WADO-RS) with FHIR-adjacent tooling nearby. Its standout feature for pipeline modeling is the **change feed**: an ordered, paged log of every create/delete event in the store.

## What it processes and doesn't

**Accepts:** standard DICOM instances (Part-10) across all imaging modalities: CT, MR (including enhanced multi-frame), PET, ultrasound, X-ray/CR/DX, nuclear medicine, and secondary capture, plus non-image DICOM objects it can store (some SR and presentation-state support; check current conformance docs for object-level acceptance). Ingestion is STOW-RS with multipart DICOM or `application/dicom+json` metadata with bulk-data references. Most transfer syntaxes in common clinical use are accepted; a few (notably MPEG video and some rare lossless syntaxes) are not supported, and validation rules (a required-attribute subset, e.g., patient ID, study UID) reject non-conformant instances with informative error responses.

**Extended query tags:** beyond the standard QIDO-searchable attributes, you can register custom DICOM tags as indexed "extended query tags" so they become searchable, useful for pulling pipeline-relevant private tags into queries.

**Change feed:** `GET /changefeed` returns an ordered log of created/deleted instances with study/series/instance UIDs and sequence numbers, ideal as the event source that triggers an inference or archiving pipeline without polling QIDO.

**Doesn't process:** it does not interpret, infer, enhance, or de-identify images. There is no de-identification endpoint (de-id happens pre-upload), no rendered-image endpoints in the base service (viewers like OHIF render client-side from retrieved frames), no burned-in-pixel PHI handling, and no DICOM network protocol (C-STORE/C-FIND); legacy PACS traffic needs a gateway (e.g., Microsoft's DICOM proxy or dcm4che relay). It stores and serves DICOM and logs changes; everything else is your pipeline.

## What the endpoints do

Key endpoint groups (REST, `{workspace}-dicom.dicom.azurehealthcareapis.com`):

- **Store (STOW-RS)**: `POST /studies` — multipart DICOM upload; partial success reporting per instance
- **Query (QIDO-RS)**: `GET /studies?PatientID=...`, `/series`, `/instances` — JSON search, plus extended query tags
- **Retrieve (WADO-RS/URI)**: `GET /studies/{study}` — full DICOM (multipart) or metadata (`/metadata`), and single-instance WADO-URI
- **Delete**: instance/series/study deletion
- **Change feed**: `GET /changefeed` and `GET /changefeed/{sequence}` — ordered create/delete event log, the differentiator

## API URL

- Overview: https://learn.microsoft.com/en-us/azure/healthcare-apis/dicom/dicom-services-overview
- Conformance statements (exactly what is/isn't supported): https://learn.microsoft.com/en-us/azure/healthcare-apis/dicom/dicom-services-conformance-statement
- API reference: https://learn.microsoft.com/rest/healthcare-apis/

## How to access

1. **Prerequisites**: Azure subscription; create a Health Data Services workspace and a DICOM service within it in the portal or via CLI (`az healthcareapis`). Endpoint is generated as `{workspace}-dicom.dicom.azurehealthcareapis.com`.
2. **Auth**: Entra ID (Azure AD) OAuth2 bearer tokens. Register a client (or use managed identity from Azure-hosted compute) and grant it the appropriate role on the service (`Dicom Data Owner` for read/write, `Dicom Data Reader` for read). Azure BAA/healthcare terms apply for PHI.
3. **Use it**:
   ```
   TOKEN=$(az account get-access-token --resource https://dicom.healthcareapis.azure.com --query accessToken -o tsv)
   curl -H "Authorization: Bearer $TOKEN" -H "Accept: application/dicom+json" \
     "https://MYWORKSPACE-dicom.dicom.azurehealthcareapis.com/studies?limit=10"
   curl -H "Authorization: Bearer $TOKEN" -X POST \
     -H "Content-Type: multipart/related; type=application/dicom" \
     -F "dicom=@file.dcm" "https://MYWORKSPACE-dicom.dicom.azurehealthcareapis.com/studies"
   ```

## MCP status

No official MCP endpoint. Microsoft exposes this via REST only. An MCP wrapper would map `store_instances`, `search_studies`, `get_study_metadata`, and `get_changefeed` to tools with Entra auth handled by the host. A local mock of that shape exists at `~/develop/improving/gehc/` (Azure MCP on port 8080).
