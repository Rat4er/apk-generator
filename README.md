-gui

Tool for generate apk

![chrome_GyrPD8iHcV](https://github.com/user-attachments/assets/5505fc7e-b826-48ba-a7de-84e78d0361cf)

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
  cd apk-generator
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
