FROM greyltc/archlinux-aur:paru AS apk_bulder

RUN pacman -Syu --noconfirm

RUN sudo -u ab -D~ bash -c 'paru -Syu --removemake --needed --noprogressbar --noconfirm python3 python-pip android-sdk android-sdk-platform-tools sdkmanager jdk-openjdk python-setuptools'
RUN yes | sdkmanager --license
RUN sdkmanager --install "platforms;android-34"

WORKDIR /app

COPY /server/app.py /app/server
COPY /server/form_parser.py /app/server
COPY /server/index.html /app/server
COPY /apk_data /app/apk_data
COPY /apk_data_v2 /app/apk_data_v2
COPY /apk_worker /app/apk_worker
COPY /utils /app/utils
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "600", "server.app:app"]
