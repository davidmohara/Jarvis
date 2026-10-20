# AWS HealthImaging

## What it is, in plain language

AWS HealthImaging (formerly AWS Medical Imaging) takes a different architectural bet than the others: on import, DICOM is converted into a cloud-native, frame-based format (High-Performance Image Sets, "image sets"), and the API operates at image-set and image-frame granularity rather than passing DICOM verbatim. This is the reference for high-throughput, frame-level access, which matters for AI inference pipelines that want to pull exactly the frames they need.

## What it processes and doesn't

**Accepts:** DICOM instances (CT, MR, PET, ultrasound, X-ray/CR/DX, nuclear medicine, and non-image DICOM such as SR where supported) submitted as bulk import jobs from S3. During import the service validates integrity and converts each study into an image set: a metadata record of DICOM attributes plus per-frame pixel data stored in the optimized format. All transfer syntaxes in common clinical use are supported at import (the service transcodes on ingestion).

**Frame-level retrieval** means an inference job can pull one frame, a subset, or all frames without retrieving full instances, and at far lower latency than DICOM multipart retrieval. Metadata is retrieved as DICOM JSON.

**Doesn't process:** it is not a PACS and not a DICOMweb endpoint. There is no STOW/QIDO/WADO; you query image sets with the proprietary `searchImageSets` and access data with `getImageFrame`. It does not render images (no rendered-image or PNG endpoints; the viewer consumes frames and renders client-side, which OHIF supports via an AWS adapter). No de-identification endpoint (de-id must happen before upload, e.g., in S3 pipeline), no inference, and it does not serve DICOM protocol (C-STORE/C-FIND) at all. Legacy DICOM consumers need a translation layer, which is the main interop trade-off of this architecture.

## What the endpoints do

Key endpoint groups (REST, data plane `medical-imaging.<region>.amazonaws.com`):

- **SearchImageSets**: `POST /searchImageSets` — filter image sets by DICOM attributes, tags, and update timestamps; paginated
- **GetImageSet** / **GetImageSetMetadata**: full image set record and metadata (DICOM attributes, including support for supplement DICOM metadata)
- **GetImageFrame**: `GET /imageSets/{id}/frames/{frameId}` — per-frame binary retrieval (this is the distinctive endpoint: frame-level, not instance-level, access)
- **Data plane vs control plane**: `ListDICOMInstances` and import/export jobs are on the control plane (`health-imaging.<region>.amazonaws.com`), data access on the separate data-plane hostname for throughput isolation
- **Import jobs**: bulk import from S3 via `StartDICOMInstanceImportJob` (server-side DICOM conversion), export to S3 via `StartDICOMInstanceExportJob`
- **Tagging / SOA**: image sets carry status (e.g., `INTEGRITY_VALIDATED` after checksum validation during import)

## API URL

- Service docs: https://docs.aws.amazon.com/healthimaging/
- API reference: https://docs.aws.amazon.com/healthimaging/latest/APIReference/ (control plane) plus the data-plane API guide
- Python SDK support is in boto3 (`medical-imaging` control plane client; data plane via SigV4-signed requests or the AWS HealthImaging data plane helpers)

## How to access

1. **Prerequisites**: AWS account, HealthImaging enabled (it is opt-in; request activation per account/region), an S3 bucket for import, and a data store created via the console or `CreateDatastore`.
2. **Auth**: IAM. The console/CLI use SigV4; data-plane requests are standard AWS-signed HTTPS. Use IAM roles (e.g., `AWSHealthImagingFullAccess` managed policy or scoped custom policies) and tag-based access control for PHI segregation. HIPAA BAA required for real patient data (standard AWS BAA covers HealthImaging).
3. **Import and query flow**:
   ```
   aws medical-imaging start-dicom-instance-import-job \
     --datastore-id ds_... --input-s3-uri s3://bucket/in/ \
     --output-s3-uri s3://bucket/out/ --role-arn arn:aws:iam::...
   # then, data plane:
   curl -X POST https://medical-imaging.us-east-1.amazonaws.com/searchImageSets \
     -H "Authorization: AWS4-HMAC-SHA256 ..." -d '{"searchCriteria": {...}}'
   ```
   In practice use boto3 or the aws-healthimaging-data-plane SDK helpers rather than hand-signing.
4. **Cost model**: storage per GB, plus data-plane requests and pixel-data retrieval charges; frame-level retrieval is priced to reward selective access, reinforcing the architecture.

## MCP status

No official MCP endpoint. AWS exposes this only through its SDKs/REST. An MCP wrapper would map `search_image_sets`, `get_image_set_metadata`, `get_image_frame`, and `start_import_job` to tools, with IAM credentials from the environment.
