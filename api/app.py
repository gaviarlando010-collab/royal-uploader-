from flask import Flask, request, jsonify, render_template_string
import requests
import re

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>👑 Royal Uploader - Vercel</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',sans-serif; }
        body { background:#0b0e1a; display:flex; justify-content:center; align-items:center; min-height:100vh; padding:20px; }
        .card { background:#1a1f30; border-radius:28px; padding:35px; max-width:520px; width:100%; border:1px solid #f1c40f44; box-shadow:0 20px 40px #00000080; }
        h1 { color:#f1c40f; text-align:center; font-size:26px; border-bottom:1px solid #334; padding-bottom:15px; }
        .sub { color:#aab; text-align:center; margin:10px 0 25px 0; font-size:14px; }
        .sub strong { color:#2ecc71; }
        label { color:#ccd; font-weight:600; font-size:13px; display:block; margin-top:18px; }
        input, select { width:100%; padding:12px; border-radius:12px; border:none; background:#262d44; color:#fff; font-size:14px; outline:1px solid #3e4764; }
        input:focus { outline:2px solid #f1c40f; }
        input[type="file"] { padding:10px; background:#1f253b; cursor:pointer; }
        .btn { width:100%; margin-top:25px; padding:14px; border:none; border-radius:40px; font-weight:bold; font-size:18px; background:linear-gradient(135deg,#f1c40f,#f39c12); color:#0b0e1a; cursor:pointer; box-shadow:0 6px 0 #b37b0e; transition:0.2s; }
        .btn:hover { transform:translateY(-2px); box-shadow:0 10px 0 #b37b0e; }
        .btn:active { transform:translateY(4px); box-shadow:0 2px 0 #b37b0e; }
        .btn:disabled { opacity:0.5; transform:translateY(4px); box-shadow:0 2px 0 #b37b0e; pointer-events:none; }
        #log { background:#0b0e1a; border-radius:16px; padding:15px; margin-top:20px; max-height:220px; overflow-y:auto; font-family:monospace; font-size:13px; color:#8cf; border:1px solid #2a3350; white-space:pre-wrap; line-height:1.7; }
        .success { color:#2ecc71; }
        .error { color:#e74c3c; }
        .warn { color:#f1c40f; }
        .info { color:#85c1e9; }
        .footer { text-align:center; color:#445; font-size:12px; margin-top:18px; }
        .footer span { color:#f1c40f; }
        ::-webkit-scrollbar { width:4px; }
        ::-webkit-scrollbar-thumb { background:#f1c40f; border-radius:10px; }
    </style>
</head>
<body>
<div class="card">
    <h1>🚀 ROYAL UPLOADER</h1>
    <div class="sub">⚡ Hosting di <strong>Vercel</strong> — Upload langsung ke Creator Store</div>

    <label>👑 Cookie .ROBLOSECURITY (WAJIB!)</label>
    <input type="text" id="cookie" placeholder="_|WARNING:-DO-NOT-SHARE..." />

    <label>📁 Pilih File Model (.rbxm / .obj / .fbx / .glb)</label>
    <input type="file" id="fileInput" />

    <label>🏷️ Nama Aset (Publik)</label>
    <input type="text" id="assetName" placeholder="Misal: Istana Emas" value="RoyalAsset_{{timestamp}}" />

    <button class="btn" id="uploadBtn">⬆️ PUBLISH KE CREATOR STORE</button>

    <div id="log">⟳ Menunggu perintah, Yang Mulia...</div>
    <div class="footer">🛡️ Setelah berhasil, ID aset muncul → semua orang bisa pakai</div>
</div>
<script>
    document.getElementById('uploadBtn').addEventListener('click', async function() {
        const log = document.getElementById('log');
        const cookie = document.getElementById('cookie').value.trim();
        const fileInput = document.getElementById('fileInput');
        const name = document.getElementById('assetName').value || 'RoyalAsset_' + Date.now();

        if (!cookie) { log.innerHTML = '<span class="error">❌ Cookie wajib diisi, Yang Mulia!</span>'; return; }
        if (!fileInput.files[0]) { log.innerHTML = '<span class="error">❌ Pilih file dulu!</span>'; return; }

        const formData = new FormData();
        formData.append('cookie', cookie);
        formData.append('file', fileInput.files[0]);
        formData.append('name', name);

        log.innerHTML = '<span class="warn">⏳ Mengirim ke server Vercel... sedang diproses...</span>';
        this.disabled = true;
        this.textContent = '⏳ PROSES...';

        try {
            const res = await fetch('/api/upload', { method: 'POST', body: formData });
            const data = await res.json();
            if (data.status === 'success') {
                log.innerHTML = `<span class="success">✅ BERHASIL!</span>\n` +
                                `<span class="info">📌 Asset ID: ${data.assetId}</span>\n` +
                                `<span class="success">🔗 https://www.roblox.com/library/${data.assetId}/</span>\n` +
                                `<span class="warn">🌍 Aset kini PUBLIK untuk semua pengguna!</span>`;
            } else {
                log.innerHTML = `<span class="error">❌ Gagal: ${data.message || 'Cek cookie atau format file'}</span>`;
            }
        } catch(e) {
            log.innerHTML = `<span class="error">❌ Error: ${e.message}</span>`;
        }
        this.disabled = false;
        this.textContent = '⬆️ PUBLISH KE CREATOR STORE';
    });
</script>
</body>
</html>
'''

@app.route('/')
@app.route('/index.html')
def index():
    return render_template_string(HTML_TEMPLATE)

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
