# Deployment of the repository on Openshift


**Find and replace `<project>` with your desired name and `<namespace>` with the name of the namespace in which to deploy.**


## 1. Configure access to github repo

### 1.1. Create a new SSH keypair for the project
```bash 
ssh-keygen -t ed25519 -C "<project>@deploy.com" -f id_ed25519_<project>
ssh-keyscan -t rsa github.ibm.com > known_hosts
``` 
more info on [how to create deploy keys](https://docs.github.com/en/enterprise-server@3.11/authentication/connecting-to-github-with-ssh/managing-deploy-keys#deploy-keys)

### 1.2. Add the public part to the repository deployment keys
get the *.pub and put it on the deploy keys section of the repo (https://github.ibm.com/tech-garage-spgi/<project>-backend/settings/keys)


### 1.3. Add the keypair to OCP to be able to use it for the pull
```bash
oc create secret generic <project>-deploy-key \
    --type=kubernetes.io/ssh-auth \
    --from-file=ssh-privatekey=id_ed25519_<project> \
    --from-file=known_hosts
```

**Note: steps 1.1 and 1.3 only need to be done once, each repo can have a different keypair but it is not required, one for project is enough**

## 2. Deploy and configure the app
### 2.1 Envs & TLS file
Create the configmap and secrets with the required information

```bash
oc create configmap <project>-backend-cm --from-env-file .env
oc create secret generic <project>-backend-secret --from-env-file .env.secret
oc create secret generic elastic-cert --from-file cert_elastic.pem # use the same way for other certificate files
```


### 2.2 Create the new-app from the repository

```bash
oc new-app --name <project>-backend \
    git@github.ibm.com:tech-garage-spgi/<project>-backend.git \
    --source-secret=<project>-deploy-key 
```

Add a probe to restart the pod if it hangs 
```bash
oc set probe deployment/<project>-backend --readiness --open-tcp=5000 --timeout-seconds=5 --initial-delay-seconds=15
oc set probe deployment/<project>-backend --liveness --get-url=http://:5000/health --timeout-seconds=5 --initial-delay-seconds=30
```

*Note: it will fail to start, do not bother as we are missing the configuration*

### 2.3 Add the Configmap, Secrets and Volumes to the deployment

These from the configmap and secrets
```bash
oc patch deployment/<project>-backend -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "<project>-backend",
          "envFrom": [
            {
              "configMapRef": {"name": "<project>-backend-cm" }
            },
            {
              "secretRef": {"name": "<project>-backend-secret"}
            }
          ]
        }]
      }
    }
  }
}'

oc set volumes deployment/<project>-backend --add --name=elastic-cert --type=secret --secret-name=elastic-cert --mount-path=/app/cert
```

This to have write permission for the logs
```bash
oc set volumes deployment/<project>-backend --add --name=logs --type=emptyDir --mount-path=/app/logs
```


### 2.4 Expose the service and add TLS support
```bash
oc expose svc/<project>-backend
oc patch route route/<project>-backend -p '{
  "spec": {
    "tls": {
      "termination": "edge"
    }
  }
}'
```

### 2.5 (Optional) Configure the webhook for the build on push to repo

First give permission to the role to be able to trigger the builds (https://docs.openshift.com/container-platform/4.16/cicd/builds/triggering-builds-build-hooks.html#unauthenticated-users-system-webhook_triggering-builds-build-hooks)
```bash
cat << EOF > rbac-webhook.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  annotations:
    rbac.authorization.kubernetes.io/autoupdate: "true"
  name: webhook-access-unauthenticated
  namespace: <namespace>
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: 'system:webhook'
subjects:
  - apiGroup: rbac.authorization.k8s.io
    kind: Group
    name: "system:unauthenticated"
EOF

oc apply -f rbac-webhook.yaml
```
**Note: this step only needs to be done once per namespace**

Then get the webhook url, get the url for the generic webhook
```bash
oc describe bc/<project>-backend
```
ie: `https://c114-e.eu-de.containers.cloud.ibm.com:31309/apis/build.openshift.io/v1/namespaces/<namespace>/buildconfigs/<project>-backend/webhooks/<secret>/generic`

Then get the secret to replace in the url. Get the secret under `triggers>generic>secret`
```bash
oc get bc/<project>-backend -o yaml
```

Replace the secret on the webhook's url

Add the webhook on the github page hooks section (https://github.ibm.com/tech-garage-spgi/<project>-backend/settings/hooks)

### pdf-highlighter - TODO

deploy with from the pdf-highligther repository  with `readme#deploy` section or `k8s/deployment.yaml`
```bash
oc apply -f k8s/deployment.yaml
```
