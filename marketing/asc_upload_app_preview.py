#!/usr/bin/env python3
"""Upload LayIt App Preview video to App Store Connect.

Steps:
  1. Find/create the appPreviewSet for IPHONE_65 on the en-GB localization
  2. Reserve an appPreview (returns uploadOperations[] with PUT URLs)
  3. Upload each part to the corresponding PUT URL
  4. PATCH the appPreview to commit (set uploaded=true with sourceFileChecksum)

Probes hard problem first: will Apple even let us create an appPreviewSet
while the version is WAITING_FOR_REVIEW? If POST returns 403/409, we report
that and bail without uploading.
"""
import sys, time, jwt, requests, hashlib, json
from pathlib import Path

ISSUER = "e7e83ad3-262a-4ebb-9451-4499a521c1d5"
KEY_ID = "VATJ3UH983"
KEY_PATH = Path.home() / ".appstoreconnect/private_keys/AuthKey_VATJ3UH983.p8"
BASE = "https://api.appstoreconnect.apple.com"
APP_ID = "6763955926"
LOCALIZATION_ID = "f2776a3c-ee63-4ac3-95e7-d436ed816607"  # en-GB on v1.0
PREVIEW_TYPE = "IPHONE_65"
VIDEO_PATH = Path("/tmp/LayIt-AppPreview-iPhone65.mp4")

def tok():
    now = int(time.time())
    payload = {"iss": ISSUER, "iat": now, "exp": now + 1200, "aud": "appstoreconnect-v1"}
    return jwt.encode(payload, KEY_PATH.read_text(), algorithm="ES256",
                      headers={"alg":"ES256","kid":KEY_ID,"typ":"JWT"})

T = tok()
H = {"Authorization": f"Bearer {T}"}
HJ = {**H, "Content-Type": "application/json"}

def get(p, **kw):
    return requests.get(f"{BASE}{p}", headers=H, timeout=30, **kw)
def post(p, body):
    return requests.post(f"{BASE}{p}", headers=HJ, json=body, timeout=30)
def patch(p, body):
    return requests.patch(f"{BASE}{p}", headers=HJ, json=body, timeout=30)

# 1. Look for an existing IPHONE_65 appPreviewSet on this localization
print(f"Step 1: looking for IPHONE_65 appPreviewSet on localization {LOCALIZATION_ID}...")
r = get(f"/v1/appStoreVersionLocalizations/{LOCALIZATION_ID}/appPreviewSets")
if r.status_code != 200:
    print(f"  HTTP {r.status_code}: {r.text[:400]}"); sys.exit(1)
sets = r.json()["data"]
preview_set_id = None
for s in sets:
    if s["attributes"].get("previewType") == PREVIEW_TYPE:
        preview_set_id = s["id"]
        print(f"  Found existing IPHONE_65 set: {preview_set_id}")
        break

# 2. Create a new one if not found
if not preview_set_id:
    print(f"  No existing IPHONE_65 set — creating new one...")
    body = {
      "data": {
        "type": "appPreviewSets",
        "attributes": {"previewType": PREVIEW_TYPE},
        "relationships": {
          "appStoreVersionLocalization": {
            "data": {"type": "appStoreVersionLocalizations", "id": LOCALIZATION_ID}
          }
        }
      }
    }
    r = post("/v1/appPreviewSets", body)
    print(f"  POST /v1/appPreviewSets → HTTP {r.status_code}")
    if r.status_code not in (200, 201):
        print(f"  RESPONSE: {r.text[:500]}")
        if r.status_code == 409:
            print("  → app version is locked because it's in review. Cannot upload until decision lands.")
        sys.exit(1)
    preview_set_id = r.json()["data"]["id"]
    print(f"  Created appPreviewSet: {preview_set_id}")

# 3. Reserve an appPreview (tells ASC about the file we want to upload)
file_size = VIDEO_PATH.stat().st_size
print(f"\nStep 3: reserving appPreview slot for {VIDEO_PATH.name} ({file_size} bytes)...")
body = {
  "data": {
    "type": "appPreviews",
    "attributes": {
      "fileName": VIDEO_PATH.name,
      "fileSize": file_size,
      "previewFrameTimeCode": "00:00:01.000",  # poster frame at t=1s
    },
    "relationships": {
      "appPreviewSet": {"data": {"type": "appPreviewSets", "id": preview_set_id}}
    }
  }
}
r = post("/v1/appPreviews", body)
print(f"  POST /v1/appPreviews → HTTP {r.status_code}")
if r.status_code not in (200, 201):
    print(f"  RESPONSE: {r.text[:600]}")
    sys.exit(1)
preview = r.json()["data"]
preview_id = preview["id"]
upload_ops = preview["attributes"]["uploadOperations"]
print(f"  Reserved appPreview: {preview_id}")
print(f"  Got {len(upload_ops)} upload operations")

# 4. Upload each part
print(f"\nStep 4: uploading {len(upload_ops)} part(s)...")
data = VIDEO_PATH.read_bytes()
for i, op in enumerate(upload_ops):
    method = op["method"]
    url = op["url"]
    offset = op["offset"]
    length = op["length"]
    headers = {h["name"]: h["value"] for h in op["requestHeaders"]}
    chunk = data[offset:offset+length]
    print(f"  Part {i+1}/{len(upload_ops)}: {method} bytes {offset}..{offset+length}", end=" ", flush=True)
    rr = requests.request(method, url, headers=headers, data=chunk, timeout=120)
    print(f"→ HTTP {rr.status_code}")
    if rr.status_code not in (200, 201, 204):
        print(f"    RESPONSE: {rr.text[:300]}")
        sys.exit(1)

# 5. Commit (set uploaded=true with checksum)
md5 = hashlib.md5(data).hexdigest()
print(f"\nStep 5: committing upload (md5={md5[:12]}...)")
body = {
  "data": {
    "type": "appPreviews",
    "id": preview_id,
    "attributes": {"uploaded": True, "sourceFileChecksum": md5}
  }
}
r = patch(f"/v1/appPreviews/{preview_id}", body)
print(f"  PATCH /v1/appPreviews/{preview_id} → HTTP {r.status_code}")
if r.status_code not in (200, 201):
    print(f"  RESPONSE: {r.text[:500]}")
    sys.exit(1)
attrs = r.json()["data"]["attributes"]
print(f"  Uploaded: {attrs.get('uploaded')}  AssetState: {attrs.get('assetDeliveryState', {}).get('state')}")
print(f"\n✅ App Preview successfully uploaded!")
print(f"   Preview ID: {preview_id}")
print(f"   It will appear in App Store Connect → LayIt → 1.0 → en-GB → App Previews")
print(f"   Apple will process it (~1-5 minutes) before it's visible.")
