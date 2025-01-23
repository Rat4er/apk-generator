import os

from flask import Flask, request, jsonify, send_file

from apk_worker.apk_worker import generate_apk, return_io_stream

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['OUTPUTS_FOLDER'] = './outputs'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUTS_FOLDER'], exist_ok=True)

@app.route('/generate_apk', methods=['POST'])
async def generate_apk_route():
    data = request.form
    package_name = data.get('package_name')
    version_code = data.get('version_code')
    version_name = data.get('version_name')
    size_apk = int(data.get('size_apk', 0))
    keystore_alias = data.get('keystore_alias')
    keystore_keypass = data.get('keystore_keypass')
    keystore_pass = data.get('keystore_pass')
    keystore_file = request.files['keystore_file']
    keystore_path = os.path.join(app.config['UPLOAD_FOLDER'], keystore_file.filename)
    keystore_file.save(keystore_path)

    try:
        final_apk = await generate_apk(app.config['OUTPUTS_FOLDER'], package_name, version_code, version_name, size_apk,
                                       keystore_path, keystore_alias,
                                       keystore_keypass, keystore_pass)

        final_apk_path = os.path.join(app.config['OUTPUTS_FOLDER'], final_apk)
        response = await return_io_stream(final_apk_path)
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/')
def web_print():
    return send_file("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
