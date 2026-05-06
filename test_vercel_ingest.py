import urllib.request, urllib.parse, json, time

url = 'https://dev-hive-next.vercel.app/api/ingest'
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = ('--' + boundary + '\r\n'
        'Content-Disposition: form-data; name="file"; filename="test_upload.txt"\r\n'
        'Content-Type: text/plain\r\n\r\n'
        'This is a test document with some content to vectorise.\r\n'
        '--' + boundary + '--\r\n')
req = urllib.request.Request(url, data=body.encode('utf-8'), headers={'Content-Type': 'multipart/form-data; boundary=' + boundary})
try:
    with urllib.request.urlopen(req) as res:
        print(json.loads(res.read().decode()))
except Exception as e:
    if hasattr(e, 'read'):
        print({'error': str(e), 'detail': e.read().decode()})
    else:
        print({'error': str(e)})
