# Ghofle

# Running the Project:
To run the project, you need to create a .env file in the project's root directory and enter the required values. (Instructions are provided below)

To run the project on your local system, follow these steps:
1. Create a file named `.env` in the root directory of the project.
2. Open the `.env` file and enter the necessary configuration values.

Next, open your terminal and enter the following command:

To run on your system, enter the following command in the terminal:
```
docker-compose --file docker-compose-develope.yml up -d
```

To deploy the project in a production environment, use the following command:
```
docker-compose up -d
```

To build the database and Redis containers, run the following command:
```
docker-compose --file docker-compose-develope.yml up -d
```

for generate a new crypto key:
```python
from Crypto import Random

key = Random.get_random_bytes(32)
```


## Setting Environment Variables

This project relies on environment variables to configure database, sms service settings etc. 

Create a `.env` file in the root directory and add the following(Value is a sample):

```
SECRET_KEY='Django Secret Key, you can generate with get_random_secret_key() function from django.core.management.utils.'

DEBUG=True # Boolean

WEB_DOMAIN=127.0.0.1
WEB_FRONT_DOMAIN=localhost:3000

DB_NAME=my_database
DB_USER=root
DB_PASS=mypassword
DB_PORT=5432
DB_HOST=myhost
DB_HOST_DEBUG=localhost

REDIS_HOST=redis_bio_host
REDIS_HOST_DEBUG=localhost
REDIS_PASSWORD=redis_bio_password
REDIS_PORT=6388

LOGGER=seq

SEQ_PORT=5345
SEQ_HOST=seq_container
SEQ_HOST_DEBUG=localhost
SEQ_API_KEY=seq_api_key

SMS_SERVICE_NAME=dummy

AWS_ACCESS_KEY_ID=aws_access_key
AWS_SECRET_ACCESS_KEY=aws_secret_key
AWS_STORAGE_BUCKET_NAME=himedic
AWS_S3_ENDPOINT_URL=aws_endpoint_url
AWS_SERVICE_NAME=s3
AWS_EXPIRE_LINK=expire_link_seconds

RABBITMQ_HOST=rabbit_ghofle_host
RABBITMQ_HOST_DEBUG=localhost
RABBITMQ_USER=rabbit_ghofle_user
RABBITMQ_PASS=rabbit_ghofle_user
RABBITMQ_PORT=5985
```
