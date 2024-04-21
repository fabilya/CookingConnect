
# CookingConnect

<img alt="Снимок экрана 2024-04-21 180715" height="350" src="https://github.com/fabilya/RandoMovie/assets/105780672/327db0f3-af94-4078-8bcf-c87d28c37ef8" width="500"/>

## Content:
- [Description](#project-description)
- [Capabilities](#service-capabilities)
- [Technologies](#technologies)
- [Deployment](#deploy-the-project-on-a-remote-server)
- [Authors](#authors)

### Project description
“Food Assistant”: an application where users publish recipes for culinary products, you can subscribe to the publications of other authors and add recipes to your favorites.
The “Shopping List” service will allow the user to create a list of products that need to be purchased to prepare the selected dishes according to the recipe/s.

### Service capabilities
- share your recipes
- see recipes from other users
- add recipes to favorites
- quickly create a shopping list by adding a recipe to your cart
- download a summary list of products
- keep track of your friends and colleagues

<img alt="image" height="250" src="https://github.com/fabilya/RandoMovie/assets/105780672/77c0fd4c-fcfe-4668-a3e0-a8e6f6ad97b1" width="400"/>

<img alt="image" height="250" src="https://github.com/fabilya/RandoMovie/assets/105780672/25845414-91c3-4140-8d48-b45313ab5231" width="450"/>

### Technologies
`Python` `Django` `Django Rest Framework` `Docker` `Gunicorn` `NGINX` `PostgreSQL` `Yandex Cloud` `Continuous Integration` `Continuous Deployment`

## Deploy the project on a remote server:
- Clone the repository
```Bash
https://github.com/fabilya/cookingconnect.git
```
- Install Docker compose on the server:
```bash
sudo apt install curl                                     # install the utility for downloading files
curl -fsSL https://get.docker.com -o get-docker.sh        # download installation script
sh get-docker.sh                                          # run script
sudo apt-get install docker-compose-plugin                # latest version of docker compose
```
- To work with GitHub Actions, you need to create environment variables in the repository in the Secrets > Actions section:

```bash
SECRET_KEY              # Django project secret key
DOCKER_PASSWORD         # Docker Hub password
DOCKER_USERNAME         # Docker Hub login
HOST                    # public IP of the server
USER                    # username on the server
PASSPHRASE              # *if the ssh key is password protected
SSH_KEY                 # private ssh key
TELEGRAM_TO             # Telegram account ID for sending a message
TELEGRAM_TOKEN          # token of the bot sending the message

DB_ENGINE               # django.db.backends.postgresql
POSTGRES_DB             # postgres
POSTGRES_USER           # postgres
POSTGRES_PASSWORD       # postgres
DB_HOST                 # db
DB_PORT                 # 5432 (default port)
```

Everything we need is installed, then create the /infra folder in the home directory /home/username/:
First, from the /backend and /frontend folders, upload the current data to DockerHub (on your PC)
```bash
docker login -u fabilya
cd backend
docker build -t fabilya/foodgram_backend:latest .
docker push fabilya/foodgram_backend:latest
```
We are preparing the front for the application, this is a template for sending to DH (where fabilya is your login for DH):
```bash
docker build -t fabilya/foodgram_frontend:latest .
docker push fabilya/foodgram_frontend:latest
```
Move the docker-compose.yml and default.conf files to the server, from the infra folder in the current repository (on your PC).
```bash
cd infra
scp docker-compose.yml username@server_ip:/home/username/
scp default.conf username@server_ip:/home/username/
```
This completes the setup, then in the infra folder we execute the command:
```bash
docker-compose up -d --build
```
The project will run on the VM and will be available at the address or IP you specified.
To access the backend container and build the final part, run the following commands:
```bash
docker-compose exec backend python manage.py makemigrations users
docker-compose exec backend python manage.py makemigrations recipes
```
```bash
docker-compose exec backend python manage.py migrate --noinput
```
```bash
docker compose exec backend python manage.py load_tags
docker compose exec backend python manage.py load_ingrs
```
```bash
docker-compose exec backend python manage.py createsuperuser
```
```bash
docker-compose exec backend python manage.py collectstatic --no-input
```
The CookingConnect has been launched, you can fill it with recipes and share it with friends!

### Authors:
[Fabiyanskiy Ilya](https://github.com/fabilya)
