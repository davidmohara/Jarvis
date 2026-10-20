# OHIF Viewer (reference client, bonus)

## What it is, in plain language

OHIF is not an image processing endpoint, it is the reference open-source web viewer for DICOM. It is included because studying which endpoints a production viewer actually calls (and in what order, with what caching) tells you exactly which backend endpoints a viewer-driven system must prioritize for performance.

## What it processes and doesn't

**Consumes:** DICOM via any of several backend adapters: DICOMweb (QIDO-RS for the study list, WADO-RS for frames and metadata, and rendered endpoints where available), Orthanc, dcm4chee, Google Cloud Healthcare, AWS HealthImaging, and DIMSE proxies. Multi-frame studies, enhanced objects, PET/CT fusion overlays, RT structure sets, segmentations (SEG), and SR rendering are supported via its extension system.

**Doesn't process:** it renders client-side in the browser (Cornerstone3D), it does not store DICOM (no STOW except through specific adapters), does not run inference or image processing server-side, and is not itself a service. It is the front end; every backend above is what it points at.

## What the endpoints look like from its side

For a viewer-driven system, the call sequence OHIF makes is the performance spec:

1. `QIDO /studies` and `/studies/{study}/series` for lists and thumbnails
2. `WADO-RS /studies/{study}/series/{series}/instances/{instance}/metadata` (DICOM JSON) for each instance
3. Frame-level retrieval (`/frames/{n}` or rendered endpoints), with HTTP range/caching and priority loading (current slice first)
4. Prefetch heuristics around the current viewport for smooth scrolling

## API URL

- Repo: https://github.com/OHIF/Viewers
- Docs: https://docs.ohif.org/

## How to access

1. **Run the demo against a public data source**: OHIF's hosted demo points at a DICOMweb server with sample data (viewer.ohif.org). Zero setup.
2. **Self-host with Orthanc in minutes** (the best pairing for a working reference stack):
   ```
   docker run -p 8042:8042 -p 4242:4242 orthancteam/orthanc
   # then run OHIF with a mode/config pointed at http://localhost:8042/dicom-web
   ```
   The OHIF repo includes ready-made platform configurations for Orthanc, dcm4chee, Google, AWS, and Azure.
3. **Auth**: whatever the backing server requires (basic auth, OAuth2); OHIF supports token-based auth and can be configured per data source.

## MCP status

Not applicable, OHIF is a browser client. Its value here is as the pattern for what your rendered and frame endpoints must support for a real viewer.
