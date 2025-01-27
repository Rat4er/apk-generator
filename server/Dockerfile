FROM --platform=linux/amd64 ubuntu:24.04

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

ENV ANDROID_SDK_TOOLS_VERSION 11076708
ENV ANDROID_SDK_TOOLS_CHECKSUM 2d2d50857e4eb553af5a6dc3ad507a17adf43d115264b1afc116f95c92e5e258

ENV GRADLE_VERSION 8.3

ENV ANDROID_HOME "/opt/android-sdk-linux"
ENV ANDROID_SDK_ROOT $ANDROID_HOME
ENV PATH $PATH:$ANDROID_HOME/cmdline-tools:$ANDROID_HOME/cmdline-tools/bin:$ANDROID_HOME/platform-tools

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG en_US.UTF-8

RUN apt-get -qq update \
    && apt-get -qqy --no-install-recommends install \
    apt-utils \
    build-essential \
    openjdk-17-jdk \
    openjdk-17-jre-headless \
    software-properties-common \
    libssl-dev \
    libffi-dev \
    python3-dev \
    cargo \
    pkg-config\
    libstdc++6 \
    libpulse0 \
    libglu1-mesa \
    openssh-server \
    zip \
    unzip \
    curl \
    lldb \
    python3.12-venv \
    git > /dev/null \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN curl -s https://dl.google.com/android/repository/commandlinetools-linux-${ANDROID_SDK_TOOLS_VERSION}_latest.zip > /tools.zip \
    && echo "$ANDROID_SDK_TOOLS_CHECKSUM ./tools.zip" | sha256sum -c \
    && unzip -qq /tools.zip -d $ANDROID_HOME \
    && rm -v /tools.zip

RUN mkdir -p $ANDROID_HOME/licenses/ \
    && echo "8933bad161af4178b1185d1a37fbf41ea5269c55\nd56f5187479451eabf01fb78af6dfcb131a6481e\n24333f8a63b6825ea9c5514f83c2829b004d1fee" > $ANDROID_HOME/licenses/android-sdk-license \
    && echo "84831b9409646a918e30573bab4c9c91346d8abd\n504667f4c0de7af1a06de9f4b1727b84351f2910" > $ANDROID_HOME/licenses/android-sdk-preview-license --licenses \
    && yes | $ANDROID_HOME/cmdline-tools/bin/sdkmanager --licenses --sdk_root=${ANDROID_SDK_ROOT}

RUN mkdir -p /home/mobiledevops/.android \
    && mkdir -p /home/mobiledevops/app \
    && touch /home/mobiledevops/.android/repositories.cfg

ENV HOME /home/mobiledevops
WORKDIR $HOME/app

RUN curl -s "https://get.sdkman.io" | bash
SHELL ["/bin/bash", "-c"]

ADD packages.txt $HOME

RUN $ANDROID_HOME/cmdline-tools/bin/sdkmanager --sdk_root=${ANDROID_SDK_ROOT} --update \
    && $ANDROID_HOME/cmdline-tools/bin/sdkmanager --sdk_root=${ANDROID_SDK_ROOT} --install $PKGS \
    && rm $HOME/packages.txt

RUN source "${HOME}/.sdkman/bin/sdkman-init.sh" \
    && sdk install gradle ${GRADLE_VERSION}

WORKDIR /app
RUN python3 -m venv venv
COPY requirements.txt /app
RUN . /app/venv/bin/activate && pip install -r requirements.txt
ENV PATH="$PATH:/app/venv/bin"

COPY /server /app/server
COPY /apk_data /app/apk_data
COPY /apk_data_v2 /app/apk_data_v2
COPY /apk_worker /app/apk_worker
COPY /utils /app/utils

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "600", "server.app:app"]
