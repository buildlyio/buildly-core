"""
Sends information about new build to Walhall webhook.
Gets repository name and build tag as arguments.
"""
import os
import sys
import argparse
import hmac
import hashlib
import json
import requests


WEBHOOK_URLS = [
        "https://dev-local-api.walhall.io/webhooks/new_version/",
        "https://dev-api.walhall.io/webhooks/new_version/",
]


def create_signature(signer: str, payload: str) -> str:
    """ Creates signature for signing request """
    repo_secret = bytes(signer.encode('utf-8'))
    return hmac.new(repo_secret, payload.encode('utf-8'), hashlib.sha1).hexdigest()


def main(repo: str, tag: str) -> None:
    payload = {
        "repository": repo,
        "tag": tag,
    }
    try:
        signer = os.environ['REPO_SIGNER']
    except KeyError:
        sys.exit('REPO_SIGNER is not set')
    signature = create_signature(signer, json.dumps(payload))
    headers = {
        'X-Signature': signature,
        'X-Repo-Name': repo,
    }
    for url in WEBHOOK_URLS:
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code // 100 == 2:
            print("{url}: OK")
        else:
            print(f'{url}: error response')
            print(r.text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send build info to Walhall')
    parser.add_argument("-r", "--repo", help="Repository (format: 'ownwer/repo_name')", required=True)
    parser.add_argument("-t", "--tag", help="Tag")
    args = parser.parse_args()

    main(args.repo, args.tag)
