# Copied from the retired workflows/content-pipeline/ghost_update_v2.py during the
# content-pipeline -> content-discovery/content-approval split (Rigby capability build).
#
# FLAGGED FOR HUMAN REVIEW: the original file has a hardcoded Ghost Admin API `key_id` and
# `hex_secret` (a live credential) plus a hardcoded `post_id` and full post body from a one-off
# manual fix ("Two Kinds of Public Servant"). Per org policy this session does not propagate
# authentication credentials into a new file, so the secret and post-specific values below are
# redacted placeholders — this copy is kept only as a reference for the JWT-generation and
# PUT-update pattern used elsewhere in step-01-approve.md, not as a runnable script.
#
# Action needed from a human: decide whether to (a) rotate the Ghost Admin API key since it has
# lived in plaintext in git history, and (b) delete this file (and the original in
# workflows/content-pipeline/) once the pattern is no longer needed for reference, since as
# written it is a one-off debug script, not a reusable utility.

import jwt, requests, json, time

key_id = 'REDACTED-SEE-CLAUDE-DESKTOP-CONFIG'
hex_secret = 'REDACTED-ROTATE-BEFORE-REUSE'
ghost_url = 'https://driventodevelop.com'
post_id = 'REDACTED-EXAMPLE-ONLY'

iat = int(time.time())
payload = {'iat': iat, 'exp': iat + 300, 'aud': '/admin/'}
token = jwt.encode(payload, bytes.fromhex(hex_secret), algorithm='HS256', headers={'kid': key_id})

headers = {
    'Authorization': f'Ghost {token}',
    'Content-Type': 'application/json',
    'Accept-Version': 'v5.0'
}

r = requests.get(f'{ghost_url}/ghost/api/admin/posts/{post_id}/', headers=headers)
post = r.json()['posts'][0]
updated_at = post['updated_at']
print('Got post, updated_at:', updated_at)

# --- Example only: build a lexical body and PUT it back. ---
# See workflows/content-approval/steps/step-01-approve.md, section 6d "Link Insertion" / "Image
# Swap", and workflows/content-discovery/steps/step-01-discover.md Step 7 for the canonical,
# non-hardcoded version of this pattern used in the actual workflows.

children = [
    # {'children': [{'detail': 0, 'format': 0, 'mode': 'normal', 'style': '', 'text': p, 'type': 'text', 'version': 1}],
    #  'direction': 'ltr', 'format': '', 'indent': 0, 'type': 'paragraph', 'version': 1}
    # for p in paragraphs
]

lexical = json.dumps({
    'root': {'children': children, 'direction': 'ltr', 'format': '', 'indent': 0, 'type': 'root', 'version': 1}
})

update_payload = {
    'posts': [{
        'updated_at': updated_at,
        'lexical': lexical,
        # title / slug / feature_image / twitter_image / meta_title / meta_description /
        # twitter_title / twitter_description / tags — set per the actual post being edited.
    }]
}

r2 = requests.put(f'{ghost_url}/ghost/api/admin/posts/{post_id}/', headers=headers, json=update_payload)
result = r2.json()
if 'posts' in result:
    p2 = result['posts'][0]
    print('Updated post OK')
    print('title:', p2.get('title'))
    print('feature_image:', p2.get('feature_image'))
    print('tags:', [t.get('name') for t in p2.get('tags', [])])
    print('lexical length:', len(p2.get('lexical', '')))
    print('excerpt:', (p2.get('excerpt') or '')[:120])
else:
    print('ERROR:', json.dumps(result, indent=2))
