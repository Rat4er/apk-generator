import io
import os
import shutil
import subprocess
import uuid

import yaml

async def cleanup():
    assets_dir = f"./apk_data_v2/app/src/main/assets"
    output_dir = f"./apk_data_v2/app/build"
    upload_dir = f"/app/uploads"
    upload_2_dir = f"/opt/project/uploads"
    if os.path.exists(assets_dir):
        shutil.rmtree(assets_dir)
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)
    if os.path.exists(upload_2_dir):
        shutil.rmtree(upload_2_dir)


async def generate_apk_v2(package_name, version_code, version_name, size_apk, keystore_path, keystore_password, alias, keypass):
    unique_id = str(uuid.uuid4())
    assets_dir = f"./apk_data_v2/app/src/main/assets/"
    os.makedirs(assets_dir, exist_ok=True)
    await set_parameters(package_name, version_code, version_name, keystore_path, keystore_password, alias, keypass)
    if size_apk > 0:
        temp_file_path = os.path.join(assets_dir, f"{unique_id}.tempfile.txt")
        with open(temp_file_path, 'wb') as f:
            f.write(b'\0' * (size_apk * 1024 * 1024 - 113999))
    try:
        await run_command_v2(['./gradlew', 'assembleRelease'])
        output_dir = f"./apk_data_v2/app/build/outputs/apk/release/app-release.apk"
        return output_dir
    except subprocess.CalledProcessError as e:
        raise e



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
        if os.path.exists(keystore_path) and "public" not in keystore_path:
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

async def run_command_v2(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd='./apk_data_v2')
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Command failed: {' '.join(command)}\nError: {stderr.decode('utf-8')}")
    return stdout.decode("utf-8").splitlines()


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

async def set_parameters(package_name, version_code, version_name, keystore_path, keystore_password, alias, keypass):
    os.environ["APPLICATION_ID"] = package_name
    os.environ["VERSION_CODE"] = version_code
    os.environ["VERSION_NAME"] = version_name
    os.environ["KEYSTORE_PATH"] = keystore_path
    os.environ["KEYSTORE_PASS"] = keystore_password
    os.environ["KEY_ALIAS"] = alias
    os.environ["KEY_PASSWORD"] = keypass

async def sign_apk(apk_path, keystore_path, keystore_alias, keystore_keypass, keystore_pass):
    await run_command_v2(["jarsigner","-verbose", "-sigalg", "SHA1withRSA", "-digestalg", "SHA1", "-keystore", keystore_path, "-storepass", keystore_pass, "-keypass", keystore_keypass, apk_path, keystore_alias, ])


async def use_default_keystore():
    keystore_path = f"./utils/public.jks"
    keystore_pass = "123456"
    keystore_alias = "main"
    key_pass = "123456"
    return keystore_path, keystore_pass, keystore_alias, key_pass
