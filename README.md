# Python FastAPI Backend Template

Python backend using fastapi

Check the #TODO tag to see necessary configurations before running the back

To customize this backend project:
TODO: replace all `fastapi_template` on the project files with your desired project name **IMPORTANT: project name cannot use hypens '-', use underscores (_) instead**
TODO: also rename the folder `./fastapi_template/` with that same project name **IMPORTANT: project name cannot use hypens '-', use underscores (_) instead**

TODO: In the file `./fastapi_template/__init__.py` adjust the title of the swagger Documentation to your project

```python
info = Info(title="Backend Project API", version="1.0.0")
```

Tasks to be done for this backend templates:

TODO: Add routes with Blueprint in case many api endpoint/ service integration exists, example: navantia_maintenance_backend

# Deployment

For deployment instructions check `DEPLOYMENT.md`

# Development

This project uses [poetry](https://python-poetry.org/)

If you don't have poetry install it with 
```bash
brew install poetry
poetry config virtualenvs.in-project true # so VScode can find the libraries for autocompletion
```

To install the dependencies creating automatically a venv with the correct python version use:
```bash
poetry install
```

To start the server in development mode (with auto refresh on file change):
```bash
poetry run dev
```


## Start

To start the server in production mode(without auto refresh) use:
```bash
poetry run pro
```

#### Docker

Some example of the usage(but you are going to get more info in the `Makefile`)

```bash
make start
```

or

```
docker build -f Dockerfile -t fastapi-backend:latest . && \
docker run -d -p 8000:8000 \
		--name project-back \
		--env-file .env \
		fastapi-backend:latest
```

## IBM Security Verify
[IBM Security Verify](https://www.ibm.com/products/verify-identity), a smart identity and access management
(IAM) solutions for the hybrid, multicloud enterprise. Powered by AI.

Verify is configured with OpenID Connect 1.0 Single Sign-On (SSO) provider. Please follow this [step-by-step OpenID Connect single sign-on in the custom application documentation](https://www.ibm.com/docs/en/security-verify?topic=ss-configuring-openid-connect-single-sign-in-custom-application) to configure your Verify application.
See [here](https://docs.verify.ibm.com/ibm-security-verify-access/reference/getmetadata) to get the necessary endpoints for login.


> Take into consideration following set-ups for IBM Security Verify:
>
> - **Sign-on method**: OpenID Connect 1.0
> - **Application URL**: http://localhost:3000 (for local installation)
> - **Grant types**: Authorization code
> - **Client authentication method**: Default
> - **Redirect URIs**: http://localhost:3000 (for local installation)
> - **Access token format**: JWT

Required credentials are:
```bash
VERIFY_LOGIN_CLIENT_ID=     #client ID, get from verify once configured
VERIFY_LOGIN_SECRET=        #client secret, get from verify once configured
VERIFY_LOGIN_SERVICE_URL=   #your verify service url
VERIFY_LOGIN_REDIRECT_URL=  #one of the set redirect URIs in verify
```

### How-to secure a route

To secure a route using IBM verify add the following to the route's function
`token: Annotated[str, Depends(VerifyValidator)]` as follows


`app/routers/verify_routes.py#79`
```Python
@verify_bp.get('/example', summary="verify example endpoint")
def example(token: Annotated[str, Depends(VerifyValidator)]):
    return "Route correctly secured with verify"
```

If the token is correct the code inside the function will be executed, otherwise a 401 HTTP error would be returned and nothing executed

## Instana monitoring

This project includes by default the required code and packages to connect to the instana agent and send the required information for its monitoring.

It can be seen on the `fastapi_template/__init__.py` as `import instana`. The default configuration should be enough to find the instana agent that relays the information to the instana dashboard. 

The only requisite for it to work is that the appropiate agent has to be installed in the platform and this agent has to be able to communicate with this project. For more information on how to install the required agent refeer to the agents sections on the instana dashboard.

In case that the project cannot find the agent because it is not using the default connection information, this can be changed by using environment variables as follows:

*Note: all this variables are optional but can be used to change the information sent to the agent*
```bash
INSTANA_AGENT_HOST	IP address or DNS name	Allows users to manually specify location of the Instana host agent.
INSTANA_AGENT_PORT	Port number	Manually specify the port of the Instana host agent.
INSTANA_DEBUG	Any value	Used to enable debug logging. It should be used for only a limited time to avoid overhead and log spamming.
INSTANA_SERVICE_NAME	String	Set the application-wide service name.
INSTANA_PROCESS_NAME	String	Set a custom label for the infrastructure entity that represents that runtime.[1]

INSTANA_DISABLE_AUTO_INSTR	true or false	Disable automatic instrumentation. # Not required as it is done via code with the `import instana` line
INSTANA_DISABLE_USE_OPENTELEMETRY	true or false	Set this variable to true to disable opentelemetry integration. The default value is false.
INSTANA_STACK_TRACE_LENGTH	Integer	Set this variable to limit the number of captured stack trace frames in a span.
```

## Milvus

If using Milvus from watsonx.data user is `ibmlhtoken` and the password is the apikey token given on watsonx.data. 
If using other Milvus username and password is used as regular.

For more information refeer to [watsonx.data documentation](https://cloud.ibm.com/docs/watsonxdata?topic=watsonxdata-conn-to-milvus#conn-to-milvusapikey)

## Handle errors

### ibm-db2 library bug

If the following error displays due to DB2 library

```bash
Traceback (most recent call last):
  File "/Users/<your-project-folder-path>/templates/python-fastapi-back/app.py", line 9, in <module>
    from connectors.db2client.db2functions import getDBConnection,getDataTable, insertOrUpdateTable
  File "/Users/<your-project-folder-path>/templates/python-fastapi-back/connectors/db2client/db2functions.py", line 4, in <module>
    import ibm_db
ImportError: dlopen(/Users/<your-project-folder-path>/templates/python-fastapi-back/venv/lib/python3.11/site-packages/ibm_db.cpython-311-darwin.so, 0x0002): Symbol not found: ___cxa_throw_bad_array_new_length
  Referenced from: <2EBF1080-6589-3997-9B48-2943098C1CE2> /Users/<your-project-folder-path>/templates/python-fastapi-back/venv/lib/python3.11/site-packages/clidriver/lib/libdb2.dylib
  Expected in:     <8D23CC51-7D92-32C9-8416-8D06AE3BA034> /usr/lib/libstdc++.6.dylib
make: *** [dev-prod] Error 1
```

Try the following workaround:

```bash
export DYLD_LIBRARY_PATH=/usr/local/Cellar/gcc/13.2.0/lib/gcc/13:${DYLD_LIBRARY_PATH}
```

By default this workaround is included in the Makefile `make dev`

## Project Structure

Project is structured in folders with the main python file being `app.py`. Each folder contains the routes definitions and the specific functions to provide the service. Additionally there is the `connectors` folder with some more cross functions and clients used by several of the other parts of the code. To sum up:

TODO:

### Envs

To see the required environment variables refer to `env.example` if any of the required variables is not set the program will fail to start and log the missing var.

Project will load the environment variables is this order and override the previous values if a variable is present in a file loaded after the previous one:

```bash
.env
.env.pre
.env.dev
.env.secret
'OS environment'
```

for example if `.env` declares `foo=bar` and `.env.pre` declares `foo=baz` the result of the env `foo` will be `baz`


### k8s Deployments

Replace "project" with the name of your project in all the files of the folder

## Developer Tips&Tricks

### Singleton

_The Singleton pattern is a design pattern that restricts the instantiation of a class to a single instance. This is useful when exactly one object is needed to coordinate actions across the system. The concept is sometimes generalized to systems that operate more efficiently when only one object exists, or that restrict the instantiation to a certain number of objects._

To sum-up using a singleton could be usefull in some situation in which having only one instance is beneficial because due to resource or performance reasons, for example to omit the initialization time of the WML library in each call.

To create a singleton class in python the best approach is the `metaclass`. Simply import the `connectors/Singleton.py` class and then declare your desired class as an instance of this Singleton class by doing it's definition like

```python
from connectors.Singleton import Singleton
class MyClass(metaclass=Singleton)
  [...]
```

Then just add the methods and properties as usual to your class, which will behave as a singleton from now on.

_Singletons are useful when you need to control access to a resource or when you need to limit the instantiation of a class to a single object. This is typically useful in scenarios such as logging, driver objects, caching, thread pools, and database connections._ **BUT THEY ARE NOT A SILVER BULLET** so analyze if they are required.

### Async

After some tinkering we have found that fastapi can benefict from the usage of the `async` keyword in I/O bound tasks.

https://fastapi.palletsprojects.com/en/latest/async-await/

These kind of tasks are the ones that are usually waiting on the completion of a long running external service,
like calling WML model inference. Other tasks might not benefit much and it con be omited.

To use it simply change the requirement for fastapi in the requirements to:

```
fastapi[async]==<version>
```

and then you are good to add `async` to the definition of the endpoints like:

```python
@watsonx_bp.get('/wxai', summary="Test IBM Watsonx AI Connection")
async def wxai_test():
  [...]
```

From fastapi's documentation: _Async is not inherently faster than sync code. Async is beneficial when performing concurrent IO-bound tasks, but will probably not improve CPU-bound tasks._

# Documentation

## Openapi

The backend contains an Openapi file that is generated on server start and it is served on the url
`<backend-url>/openapi`, like for example `localhost:8000/openapi`

It can be seen on the `openapi.json` file on this repo as well for the current code

To access this documentation from Frontend add the to the end of the URL `/api/docs`

To create the openapi for a private endpoint deployment create an environment variable named `PRIVATE_ENDPOINT` with `True`, it will create the correspoding endpoint when using Code Engine to be able to use the Openapi to test the backend
