from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from flask import render_template
import os
import pprint
import json
from json.decoder import JSONDecodeError
from werkzeug.exceptions import BadRequest
from notebook_configv2 import config


flow = Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/cloud-platform'],
    redirect_uri=os.environ.get('REDIRECT_URL')
)

LOCATION = "us-central1-a"
ALLOWED_IMAGE_FAMILIES = {
    "tf2-2-6-cu110",
    "tf2-2-5-cu110",
    "tf2-2-4-cu110",
    "tf2-2-3-cu110",
    "tf2-2-0-cu100",
    "r-4-1-cpu-experimental",
    "r-3-6-cpu-experimental",
    "pytorch-latest-cu100",
    "pytorch-1-9-cu110",
    "pytorch-1-6-cu110",
    "common-cu110"    
}

def get_variable(request, name):
    value = request.get(name)
    if value is None:
        raise BadRequest(f"'{name}' is missing")
    return value

def get_expiration_hours(request):
    value = request.get("expiration_hours", "96")
    if not value.isnumeric():
         raise BadRequest(f"'expiration_hours' is not valid: must be a number")
    return value
        

def create_notebook(project_id, instance_id, image_family, machine_type, requestor, expiration_hours, api):
    requestor = requestor.split('@')[0].replace('.', '_').lower()
    return api.projects().locations().instances().create(
        instanceId=instance_id,
        parent=f'projects/{project_id}/locations/{LOCATION}',
        body=config(
            project_id=project_id,
            image_family=image_family,
            machine_type=machine_type,
            requestor=requestor,
            expiration_hours=expiration_hours
        )
    ).execute()

def start_notebook(project_id, instance_id, api):
    return api.projects().locations().instances().start(
        name=f"projects/{project_id}/locations/{LOCATION}/instances/{instance_id}"
    ).execute()

def stop_notebook(project_id, instance_id, api):
    return api.projects().locations().instances().stop(
        name=f"projects/{project_id}/locations/{LOCATION}/instances/{instance_id}"
    ).execute()

def delete_notebook(project_id, instance_id, api):
    return api.projects().locations().instances().delete(
        name=f"projects/{project_id}/locations/{LOCATION}/instances/{instance_id}"
    ).execute()

def get_ai_notebooks(project_id, api):
    request = api.projects().locations().instances().list(
        parent=f"projects/{project_id}/locations/{LOCATION}"
    )
    response = request.execute()
    instances = response.get("instances", [])
    return {
        "instances": [
            {
                'name': data['name'].split('/')[-1],
                'state': data['state'].split('/')[-1],
            } for data in instances
        ]
    }
    

def manage_notebooks(request, api):
    try:
        action = get_variable(request, "action")
        project_id = get_variable(request, "project_id")

        if action.upper() == 'CREATE':
            image = get_variable(request, "notebook_type")
            if image not in ALLOWED_IMAGE_FAMILIES:
                error_msg = 'Invalid "notebook_type", available options: ' + str(list(ALLOWED_IMAGE_FAMILIES))
                raise BadRequest(error_msg)

            return create_notebook(
                project_id=project_id, 
                instance_id=get_variable(request, "instance_id"),
                image_family=image, 
                machine_type=get_variable(request, 'machine_type'),
                requestor=get_variable(request, 'requestor'),
                expiration_hours=get_expiration_hours(request),
                api=api
            )
        elif action.upper() == 'START':
            return start_notebook(
                project_id=project_id, 
                instance_id=get_variable(request, 'instance_id'),
                api=api
            )
        elif action.upper() == 'STOP':
            return stop_notebook(
                project_id=project_id, 
                instance_id=get_variable(request, 'instance_id'), 
                api=api
            )
        elif action.upper() == 'DELETE':
            return delete_notebook(
                project_id=project_id, 
                instance_id=get_variable(request, 'instance_id'), 
                api=api
            )
        elif action.upper() == "LIST":
            return get_ai_notebooks(
                project_id=project_id,
                api=api
            )
    except BadRequest as e:
        return {"error": e.description}, 400
    except HttpError as e:
        return {"error": e.reason}, 400
    return {"error": f"Invalid action: {action}" }, 400


def main(request):
    if request.method == 'POST':
        token = request.form['token']
        cred = Credentials(token)
        if not cred.valid:
            return render_template(
                "login.html", 
                login_url=flow.authorization_url()[0])                    
        try:
            req_json = json.loads(request.form["request"])
            notebooks = build("notebooks", "v1", credentials=cred)
            response = manage_notebooks(req_json, api=notebooks)
            response = json.dumps(response, indent=2)
        except JSONDecodeError:
            response="Invalid json request"
        return render_template(
            "main.html",
            token=token,
            action=os.environ.get('REDIRECT_URL'),
            request_sent=json.dumps(req_json, indent=2),
            response = response
        )
    if "code" in request.args:
        flow.fetch_token(code=request.args['code'])

        return render_template(
            "main.html",
            action=os.environ.get('REDIRECT_URL'),
            token=flow.credentials.token
        )
    return render_template(
        "login.html", 
        login_url=flow.authorization_url()[0])