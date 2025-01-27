import os

from flask import Flask, request, jsonify, send_file

from apk_worker.apk_worker import generate_apk, return_io_stream, generate_apk_v2, use_default_keystore
from server.form_parser import parse_form
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['OUTPUTS_FOLDER'] = './outputs'

@app.route('/generate_apk', methods=['POST'])
async def generate_apk_route():
    package_name, version_code, version_name, size_apk, keystore_path, keystore_pass, keystore_alias, keystore_keypass = await parse_form(request, app.config['UPLOAD_FOLDER'])

    try:
        final_apk = await generate_apk(app.config['OUTPUTS_FOLDER'], package_name, version_code, version_name, size_apk,
                                       keystore_path, keystore_alias,
                                       keystore_keypass, keystore_pass)

        final_apk_path = os.path.join(app.config['OUTPUTS_FOLDER'], final_apk)
        response = await return_io_stream(final_apk_path)
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_apk_v2', methods=['POST'])
async def generate_apk_v2_route():
    package_name, version_code, version_name, size_apk, keystore_path, keystore_pass, keystore_alias, keystore_keypass = await parse_form(request, app.config['UPLOAD_FOLDER'])
    await generate_apk_v2(package_name, version_code, version_name, size_apk, keystore_path, keystore_pass, keystore_alias, keystore_keypass)
    return jsonify({'success': True}), 200


@app.route('/')
def web_print():
    return send_file("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
