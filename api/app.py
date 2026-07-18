from flask import Flask, request, jsonify, send_from_directory
import requests
import re
import os

app = Flask(__name__, static_folder='../static', static_url_path='/static')

@app.route('/')
def index():
    return send_from_directory('../static', 'index.html')

@app.route('/api/upload', methods=['POST'])
def upload_to_roblox():
    try:
        cookie = request.form.get('cookie')
        name = request.form.get('name', 'RoyalAsset')
        file = request.files.get('file')
        
        if not cookie or not file:
            return jsonify({'status': 'error', 'message': 'Cookie atau file kosong'}), 400
        
        file_data = file.read()
        filename = file.filename
        
        session = requests.Session()
        session.cookies.set('.ROBLOSECURITY', cookie, domain='.roblox.com')
        
        csrf_resp = session.get('https://www.roblox.com/asset/upload')
        csrf_token = csrf_resp.headers.get('x-csrf-token')
        if not csrf_token:
            return jsonify({'status': 'error', 'message': 'Gagal ambil CSRF. Cookie tidak valid?'}), 401
        
        files = {'file': (filename, file_data, 'application/octet-stream')}
        data = {'name': name, 'assetType': 1}
        headers = {'X-CSRF-TOKEN': csrf_token, 'User-Agent': 'Mozilla/5.0 (compatible; RoyalUploader)'}
        
        upload_resp = session.post('https://www.roblox.com/asset/upload', data=data, files=files, headers=headers)
        
        asset_id = None
        if upload_resp.headers.get('Location'):
            match = re.search(r'/library/(\d+)/', upload_resp.headers.get('Location'))
            if match: asset_id = match.group(1)
        if not asset_id:
            match = re.search(r'assetId["\']?\s*[:=]\s*["\']?(\d+)', upload_resp.text)
            if match: asset_id = match.group(1)
        
        if asset_id:
            return jsonify({'status': 'success', 'assetId': asset_id})
        elif upload_resp.status_code in [200, 302]:
            return jsonify({'status': 'success', 'assetId': 'SUKSES (cek dashboard Creator Store)', 'raw': upload_resp.text[:300]})
        else:
            return jsonify({'status': 'error', 'message': f'HTTP {upload_resp.status_code}', 'detail': upload_resp.text[:200]})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
