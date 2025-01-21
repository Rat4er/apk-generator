import os
import subprocess
import uuid

from flask import Flask, render_template, request, jsonify, send_file, after_this_request
import yaml
import shutil

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['OUTPUTS_FOLDER'] = './outputs'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUTS_FOLDER'], exist_ok=True)


def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Command failed: {' '.join(command)}\nError: {stderr.decode('utf-8')}")
    return stdout.decode("utf-8").splitlines()


def generate_apk(package_name, version_code, version_name, size_apk, keystore_path, keystore_alias, keystore_keypass,
                 keystore_pass):
    unique_id = str(uuid.uuid4())
    assets_dir = f"./apkdata/assets/{unique_id}"
    os.makedirs(assets_dir, exist_ok=True)
    output_apk = os.path.join(app.config['OUTPUTS_FOLDER'], f"{package_name}_{version_code}_{version_name}.apk")
    try:
        edit_apktool_conf(package_name, version_code, version_name)
        if size_apk > 0:
            temp_file_path = os.path.join(assets_dir, "outputfile.tempfile")
            with open(temp_file_path, 'wb') as f:
                f.write(b'\0' * (size_apk * 1024 * 1024 - 113999))
        run_command(["java", "-jar", "./utils/apktool_2.9.3.jar", "b", "apkdata", "--use-aapt2", "-o", output_apk])
        run_command([
            "java", "-jar", "./utils/uber-apk-signer-1.2.1.jar", "-a", output_apk,
            "--ks", keystore_path, "--ksAlias", keystore_alias,
            "--ksKeyPass", keystore_keypass, "--ksPass", keystore_pass
        ])
        return output_apk

    except Exception as e:
        raise e

    finally:
        if os.path.exists(assets_dir):
            shutil.rmtree(assets_dir)


def edit_apktool_conf(package_name, version_code, version_name):
    with open("./apkdata/apktool.yml", "r+") as comp:
        data = yaml.safe_load(comp)
        data["packageInfo"]["renameManifestPackage"] = package_name
        data["versionInfo"]["versionCode"] = version_code
        data["versionInfo"]["versionName"] = version_name
        comp.truncate(0)
        comp.seek(0)
        yaml.dump(data, comp)


@app.route('/generate_apk', methods=['POST'])
def generate_apk_route():
    data = request.form
    package_name = data.get('package_name')
    version_code = data.get('version_code')
    version_name = data.get('version_name')
    size_apk = int(data.get('size_apk', 0))
    #output_dir = data.get('output_dir')
    keystore_alias = data.get('keystore_alias')
    keystore_keypass = data.get('keystore_keypass')
    keystore_pass = data.get('keystore_pass')

    if 'keystore_file' not in request.files:
        try:
            keystore_file = data.get('keystore_file')
            if keystore_file == 'Default':
                keystore_path = os.path.join(f"utils", f"cert", f"keystore.jks")
                keystore_alias = 'key0'
                keystore_keypass = '123456'
                keystore_pass = '123456'
        except Exception as e:
            return jsonify({'errr': str(e)}), 500
    else:
        keystore_file = request.files['keystore_file']
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        keystore_path = os.path.join(app.config['UPLOAD_FOLDER'], keystore_file.filename)
        keystore_file.save(keystore_path)

    try:
        final_apk = generate_apk(package_name, version_code, version_name, size_apk, keystore_path, keystore_alias,
                                 keystore_keypass, keystore_pass)

        response = send_file(final_apk, as_attachment=True)
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/')
def webprint():
    return send_file("index.html")

@app.teardown_request
def teardown_request_func(test):
    try:
        shutil.rmtree(f"{os.path.join(app.config['OUTPUTS_FOLDER'])}")
    except:
        pass
    try:
        shutil.rmtree(f"{os.path.join(app.config['UPLOAD_FOLDER'])}")
    except:
        pass



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
