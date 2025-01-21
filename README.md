
# apk-generator-gui

Tool for generate apk


## Run Locally

Clone the project

```bash
  git clone https://github.com/rat4er/apk-generator
```

Install Docker and Docker Compose (example for Ubuntu):

```bash
  sudo apt-get install docker docker-compose -y
```

Go to the project directory

```bash
  cd apk-generator-gui
```

Create a .env file containing your domain. Example:
``` bash
  touch .env
  echo "DOMAIN=example.com" >> .env 
```

And the last one:

```bash
  docker-compose up -d
```