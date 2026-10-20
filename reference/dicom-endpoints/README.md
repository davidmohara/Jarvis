# DICOM Image Processing Endpoints: Reference Systems

Research date: 2026-10-20
Context: GE HealthCare engagement research, general DICOM architecture modeling. Scope covers store & retrieve (VNA/PACS), AI/inference pipeline, and viewer rendering.

## Note on MCP

None of the five systems below ship an official MCP endpoint. They are all REST/HTTP APIs (DICOMweb or proprietary REST). Where a community MCP wrapper exists it is flagged in the individual doc. Any of these could be wrapped in a custom MCP server by exposing their REST endpoints as MCP tools, which is the practical path if you want LLM-driven access.

## Local mocks

Orthanc, Google, and Azure are mocked as three isolated MCP servers (endpoint shapes modeled on the live APIs, live-verified 2026-10-20) at `~/develop/improving/gehc/` — see its README for endpoints (ports 8042/8443/8080) and wiring.

## Contents

| System | Type | Docs |
|---|---|---|
| [Orthanc](orthanc.md) | Open source, self-hosted | https://orthanc.uclouvain.be/book/users/rest.html |
| [dcm4chee Archive](dcm4chee.md) | Open source, self-hosted | https://github.com/dcm4che/dcm4chee-arc-light/wiki |
| [Google Cloud Healthcare API](google-cloud-healthcare.md) | Commercial cloud | https://cloud.google.com/healthcare-api/docs/how-tos/dicom |
| [AWS HealthImaging](aws-healthimaging.md) | Commercial cloud | https://docs.aws.amazon.com/healthimaging/ |
| [Azure Health Data Services DICOM](azure-dicom.md) | Commercial cloud | https://learn.microsoft.com/en-us/azure/healthcare-apis/dicom/dicom-services-overview |
| [OHIF Viewer](ohif-viewer.md) | Open source viewer client (bonus) | https://github.com/OHIF/Viewers |

## Modeling recommendation

Use dcm4chee as the endpoint taxonomy baseline (most spec-complete DICOMweb), Google's de-identify plus Pub/Sub notification pattern for the AI pipeline trigger, and Azure's change feed for event ordering. That trio covers store/retrieve, inference routing, and viewer rendering.

## Verification caveat

URLs were compiled from research references and were not live-fetched at write time. Confirm each before citing in a client-facing deliverable.
