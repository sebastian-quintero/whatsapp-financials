# whatsapp-financials

Track expenses and incomes via WhatsApp and get a full report.

This project uses:

- [FastAPI](https://fastapi.tiangolo.com) to stand up a server.
- [MySQL](https://dev.mysql.com/doc/refman/8.0/en/) as a database.
- [SQLModel](https://www.google.com/search?client=safari&rls=en&q=sql+tiangolo&ie=UTF-8&oe=UTF-8)
  to interact with the database.
- [Fixer API](https://apilayer.com/marketplace/fixer-api) for currency
  conversions.
- [Twilio's WhatsApp
  API](https://www.twilio.com/docs/whatsapp/tutorial/requesting-access-to-whatsapp)
  to enable an endpoint that can be used as a webhook to respond to WhatsApp
  messages.
  
Please make sure you have `mysql` installed and there is a MySQL server
available. You can visit [this
tutorial](https://dev.mysql.com/doc/refman/8.0/en/tutorial.html) to learn more
about standing up a MySQL server.

The server is enabled to interact with [Twilio's WhatsApp
API](https://www.twilio.com/docs/whatsapp/tutorial/requesting-access-to-whatsapp).
It provides a webhook which Twilio can `POST` to, so that it may record a
transaction, create a report and other useful commands.

When standing up the server locally, please visit `localhost:8000/docs` to read
the docs.

## Creating the database and tables

In a terminal, connect to the MySQL database server. You can visit [this
tutorial](https://dev.mysql.com/doc/refman/8.0/en/tutorial.html) to learn how
to connect locally to your server.

To connect locally to the server you can use this command:

```bash
mysql -u user -p
```

Once the `mysql>` prompt is available, you can create the database and tables.

The objective is to create the tables displayed here:

![Database Diagram](./diagram.svg)

Create the database:

```sql
mysql> CREATE DATABASE main;
```

Use the database you just created:

```sql
mysql> USE main;
```

Create the tables:

```sql
mysql> CREATE TABLE organization (
    id INT unsigned NOT NULL AUTO_INCREMENT,
    created_at DATETIME NOT NULL,
    name VARCHAR(150) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    language VARCHAR(2) NOT NULL,    
    PRIMARY KEY (id)
) ENGINE=INNODB;

mysql> CREATE TABLE user (
    id INT unsigned NOT NULL AUTO_INCREMENT,
    organization_id INT unsigned NOT NULL,
    created_at DATETIME NOT NULL,
    whatsapp_phone VARCHAR(15) NOT NULL,
    name VARCHAR(150) NOT NULL,
    is_admin BOOLEAN NOT NULL,
    PRIMARY KEY (id),
    INDEX org_id (organization_id),
    FOREIGN KEY (organization_id)
        REFERENCES organization(id)
) ENGINE=INNODB;

mysql> CREATE TABLE transaction (
    id INT unsigned NOT NULL AUTO_INCREMENT, 
    user_id INT unsigned NOT NULL,
    created_at DATETIME NOT NULL,
    label VARCHAR(150) NOT NULL,
    value FLOAT NOT NULL,
    currency VARCHAR(3) NOT NULL,
    value_converted FLOAT NOT NULL,
    description VARCHAR(150) NOT NULL,
    PRIMARY KEY (id),
    INDEX us_id (user_id),
    FOREIGN KEY (user_id)
        REFERENCES user(id)
) ENGINE=INNODB;
```

## Run locally

Some environment variables are required to run the application. They should be
defined in a standard `.env` file. Please copy the `.env.example` file into a
`.env` and replace the values with your own.

Before running the app, make sure the MySQL database server is running, the
tables are created and the environment variables are set.

Run the app:

```bash
uvicorn app.main:server --reload
```

Query the docs. Go to your web browser and visit the following url:
`localhost:8000/docs`.

Perform a health check:

```bash
curl --location --request GET 'localhost:8000' \
--header 'Content-Type: application/json'
```

A webhook can be submitted from Twilio. Please see the docs for the details on
using the `/twilio` endpoint.

Note that the sender in the `From` param must be authorized in the
`ALLOWED_FROM` environment variable.

## Run with Docker

Build the image.

```bash
docker build -t whatsapp-financials .
```

Run a container using the image. Do not forget to have the environment
variables set in the `.env` file.

```bash
docker run -d --name whatsapp-financials -p 80:8000 --env-file .env --rm whatsapp-financials
```

Now you can make all the same requests that were described in the previous
section, but to port `80`.

You can see the logs of your container with `docker logs whatsapp-financials` or
follow them adding the `-f` flag before the container name.
