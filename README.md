# Identi-Authentication
Authentication Microservice for Identi Platform, based on OAuth + JWT

## Python Version
- Managed by **venv** python module, defined in **.python-version** file
- To create a python virtual environment, run:
```bash
python -m venv venv --clear
```

- Next, inside virtual environment (venv), install dependencies:
```bash
(venv) pip install -r src/requirements.txt
```

## Setup Local DEV
- Copy **src/example.env** file and save as **src/.env**
- Modify the values to desired implementation
- The example value for **APP_ACCESS_TOKEN** field, correspond to an example default value, then if you changed it, you need to update the value of **APP_ACCESS_TOKEN**.
- To view the TOKEN contents and change it, you could use the service on: <a href="https://jwt.io">https://jwt.io</a>, copy the value and paste there (in ENCODED field), next paste the value of JWT_SECRET in VERIFY SIGNATURE field on **jwt.io**.

## For Local Debug
- Use "Run and Debug" from VS Code, it's preconfigured on **.vscode/launch.json**, with the name **Authx Debug**
- In the requests use the value of **APP_ACCESS_TOKEN** and put it in the field **access_token**

## Future improvements
- Endpoint implement to register auth for applications
- Implement Docker Debug
- Integrate with Database, like MongoDB or PostgreSQL
- Automate image build through Jenkins or GitHub Actions
