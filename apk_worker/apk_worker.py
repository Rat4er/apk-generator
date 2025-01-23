import io
import os
import shutil
import subprocess
import uuid
import yaml


async def generate_apk(output_folder, package_name, version_code, version_name, size_apk, keystore_path, keystore_alias,
                       keystore_keypass,
                       keystore_pass):
    unique_id = str(uuid.uuid4())
    assets_dir = f"./apk_data/assets/{unique_id}"
    os.makedirs(assets_dir, exist_ok=True)
    apk_name = f"{package_name}_{version_code}_{version_name}"
    output_apk = os.path.join(output_folder, apk_name + ".apk")
    try:
        await edit_apktool_conf(package_name, version_code, version_name)
        if size_apk > 0:
            temp_file_path = os.path.join(assets_dir, "outputfile.tempfile")
            with open(temp_file_path, 'wb') as f:
                f.write(b'\0' * (size_apk * 1024 * 1024 - 113999))
        await run_command(
            ["java", "-jar", "./utils/apktool_2.9.3.jar", "b", "apk_data", "--use-aapt2", "-o", output_apk])
        await run_command([
            "java", "-jar", "./utils/uber-apk-signer-1.2.1.jar", "-a", output_apk,
            "--ks", keystore_path, "--ksAlias", keystore_alias,
            "--ksKeyPass", keystore_keypass, "--ksPass", keystore_pass
        ])
        return apk_name + '-aligned-signed.apk'

    except Exception as e:
        raise e

    finally:
        if os.path.exists(output_apk):
            os.remove(output_apk)
        if os.path.exists(assets_dir):
            shutil.rmtree(assets_dir)
        if os.path.exists(keystore_path):
            os.remove(keystore_path)


class APKWorker:
    pass


async def edit_apktool_conf(package_name, version_code, version_name):
    with open("./apk_data/apktool.yml", "r+") as comp:
        data = yaml.safe_load(comp)
        data["packageInfo"]["renameManifestPackage"] = package_name
        data["versionInfo"]["versionCode"] = version_code
        data["versionInfo"]["versionName"] = version_name
        comp.truncate(0)
        comp.seek(0)
        yaml.dump(data, comp)


async def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Command failed: {' '.join(command)}\nError: {stderr.decode('utf-8')}")
    return stdout.decode("utf-8").splitlines()

async def return_io_stream(apk_path):
    return_stream = io.BytesIO()
    with open(apk_path, 'rb') as apk:
        return_stream.write(apk.read())
    return_stream.seek(0)
    os.remove(apk_path)
    return return_stream
