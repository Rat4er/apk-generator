import os

from apk_worker.apk_worker import use_default_keystore


async def parse_form(request, keystore_path):
    data = request.form
    package_name = data.get('package_name')
    version_code = data.get('version_code')
    version_name = data.get('version_name')
    size_apk = int(data.get('size_apk', 0))
    if len(request.files) == 0:
        keystore_path, keystore_pass, keystore_alias, keystore_keypass = await use_default_keystore()
        return package_name, version_code,version_name, size_apk, keystore_path, keystore_pass, keystore_alias, keystore_keypass
    else:
        keystore_alias = data.get('keystore_alias')
        keystore_keypass = data.get('keystore_keypass')
        keystore_pass = data.get('keystore_pass')
        keystore_file = request.files['keystore_file']
        keystore_path = os.path.join(keystore_path, keystore_file.filename)
        keystore_file.save(keystore_path)
        keystore_absolute = os.path.abspath(keystore_path)
        return package_name, version_code, version_name, size_apk, keystore_absolute, keystore_pass, keystore_alias, keystore_keypass