import jwt, requests, json, time

key_id = '69b084ee2fa72d02909ce5b9'
hex_secret = '1e38cfe6434e7e4f072e43ffbd8155715d25609c6d43fd4addb9261bf43da0e6'
ghost_url = 'https://driventodevelop.com'
post_id = '6a264eb4a540680290141205'

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

paragraphs = [
    "Governor Pritzker said he wasn't willing to give \"billions of taxpayer dollars to a billionaire-owned team.\" He said it like it was a principled stand. The Illinois House never voted. Indiana said yes. The Bears are leaving Chicago.",
    "Samsung just moved its U.S. headquarters from New Jersey to Plano. New Jersey went from 22 Fortune 500 companies in 2018 to 15 in 2025. Site selection experts are calling it a \"five-alarm fire.\" The governor's response was more or less the same as Pritzker's: frame business as extraction, frame taxes as protection, frame losing as virtue.",
    "There are two kinds of people who end up in public office.",
    "The first kind came from somewhere. They made payroll. They signed the front of checks. They know what a lease costs, what a permit delay does to a timeline, what it means when a company decides a city isn't worth the friction. When they sit across from a business looking to relocate or expand, they understand the transaction because they've been inside one.",
    "The second kind never left the track. School, staff, campaign, office. The incentive structure rewards the frame that protects constituents from business, not the one that learns how business actually works. Calling a stadium deal \"billionaire welfare\" plays well. Explaining the hotel tax revenue, the construction jobs, the property value halo around a major venue (that's harder, and it doesn't fit on a mailer).",
    "I don't think the founding fathers designed public service as a career path. They designed it as a rotation. People who had built things and run things gave a few years to governing, then went home. The expectation was that you'd bring something from the real world into the office, not spend a career inside it.",
    "The ledger isn't complicated. The cities and states winning right now are led by people who see business as a partner in building a community. The ones losing have leaders who've decided it's something to manage, tax, and occasionally blame.",
    "Who's in the room when your clients are making location decisions? And do those people understand what's actually being decided?"
]

children = []
for p in paragraphs:
    children.append({
        'children': [{'detail': 0, 'format': 0, 'mode': 'normal', 'style': '', 'text': p, 'type': 'text', 'version': 1}],
        'direction': 'ltr', 'format': '', 'indent': 0, 'type': 'paragraph', 'version': 1
    })

lexical = json.dumps({
    'root': {'children': children, 'direction': 'ltr', 'format': '', 'indent': 0, 'type': 'root', 'version': 1}
})

update_payload = {
    'posts': [{
        'updated_at': updated_at,
        'title': 'Two Kinds of Public Servant',
        'slug': 'two-kinds-of-public-servant',
        'lexical': lexical,
        'feature_image': 'https://driventodevelop.com/content/images/2026/06/cities-that-win.jpg',
        'twitter_image': 'https://driventodevelop.com/content/images/2026/06/cities-that-win.jpg',
        'meta_title': 'Two Kinds of Public Servant',
        'meta_description': "There are two kinds of people in public office. One made payroll. The other never left the track. The difference shows up in the ledger.",
        'twitter_title': 'Two Kinds of Public Servant',
        'twitter_description': "There are two kinds of people in public office. One made payroll. The other never left the track. The difference shows up in the ledger.",
        'tags': [
            {'id': '637ea17e92f3300211b1b23a'},
            {'id': '637ea17e92f3300211b1b233'}
        ]
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
