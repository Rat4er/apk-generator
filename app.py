import io
import os
import subprocess
from flask import Flask, render_template, request, jsonify, send_file
import yaml
import shutil

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['OUTPUTS_FOLDER'] = './outputs'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUTS_FOLDER'], exist_ok=True)


def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = [], []
    while process.poll() is None:
        line = process.stdout.readline()
        if line:
            stdout.append(line.decode("utf-8"))
    stderr.extend(process.stderr.readlines())
    if process.returncode != 0:
        error_message = ''.join(stderr.decode("utf-8") for stderr in stderr)
        raise Exception(f"Command failed: {command}\nError: {error_message}")
    return stdout


def generate_apk(package_name, version_code, version_name, size_apk, keystore_path, keystore_alias, keystore_keypass,
                 keystore_pass):
    total_steps = 5 if size_apk > 0 else 4
    step = 0

    try:
        print("Starting APK generation...")
        step += 1

        print("Generation of apk with params:")
        print(f"package={package_name}")
        print(f"versionCode={version_code}")
        print(f"versionName={version_name}")
        print(f"sizeAPK={size_apk}")
        #print(f"outputDir={output_dir}")
        print(f"keystorePath={keystore_path}")
        print(f"keystoreAlias={keystore_alias}")

        # Modify package
        print("1) Modifying package...")
        edit_apktool_conf(package_name, version_code, version_name)
        step += 1

        # Generate temp file
        if size_apk > 0:
            print("2) Generating temp file...")
            if not os.path.exists("./apkdata/assets"):
                os.mkdir("./apkdata/assets")
            file_path = "./apkdata/assets/outputfile.tempfile"
            with open(file_path, 'wb') as f:
                f.write(b'\0' * (size_apk * 1024 * 1024 - 113999))
            step += 1

        # Build APK
        print("3) Building APK...")
        output_apk = os.path.join(f"outputs", f"{package_name}_{version_code}_{version_name}.apk")
        for line in run_command(f"java -jar ./utils/apktool_2.9.3.jar b apkdata --use-aapt2 -o {output_apk}"):
            print(line)
        step += 1

        # Sign APK
        print("4) Signing APK...")
        for loutput_dirine in run_command(
                f"java -jar ./utils/uber-apk-signer-1.2.1.jar -a {output_apk} --ks {keystore_path} "
                f"--ksAlias {keystore_alias} --ksKeyPass {keystore_keypass} --ksPass {keystore_pass}"):
            print(line)
        step += 1

        # Remove old
        print("5) Removing old files...")
        if os.path.exists(output_apk):
            os.remove(output_apk)
        temp_file_path = "./apkdata/assets/outputfile.tempfile"
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        # Rename package
        print("6) Renaming package...")
        signed_apk = f"{package_name}_{version_code}_{version_name}-aligned-signed.apk"
        final_apk = os.path.join(f"outputs", f"{signed_apk}")
        if os.path.exists(signed_apk):
            os.rename(signed_apk, final_apk)

        print("APK generation completed.")
        return final_apk
    except Exception as e:
        print("APK generation failed.")
        raise e


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
        final_apk = generate_apk(package_name, version_code, version_name, size_apk,
                                 keystore_path, keystore_alias, keystore_keypass, keystore_pass)

        return send_file(final_apk, as_attachment=True)
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
