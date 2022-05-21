

Quick Automation project using Python and Terraform to deploy in GCP

1. Go to Credentials in Cloud Console and create a new OAuth app
2. Download the credentials file and name it client_secret.json in the directory
3. Deploy a new function

gcloud functions deploy nbooks_oauth --source nov16_oauth --entry-point main --allow-unauthenticated \
    --trigger-http --runtime python39

4. Whitelist the http trigger of the function in the OAuth2 app
5. Set the environment variable REDIRECT_URL of the function  to the HTTP trigger
