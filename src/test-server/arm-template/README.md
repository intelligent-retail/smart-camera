
# Deploy with ARM Template

\* Working directory: `<repository_root_dir>/src/test-server/arm-template`

## Deploy target

- Stream Analytics
- Cosmos DB
- Container Instances

## Setup

Install Azure CLI and log in

- https://docs.microsoft.com/ja-jp/cli/azure/

`deploy.sh` - Fill in your resource group name and location

```
# replace with your resource group location
LOCATION=japaneast

# replace with your resource group name
RESOURCE_GROUP=myresourcegroup
```

`parameters.json` - Fill in your resource group names

```
"parameters": {
    "streamingjobs_myasa_name": {
        "value": "myasa" <- replace with your resource name
    },
    "databaseAccounts_my_cosmos_db_name": {
        "value": "mycosmosdb" <- replace with your resource name
    }
}
```

## Deployment

### Create resource group and create resources

- Stream Analytics
- Cosmos DB

```
$ sh deploy.sh
```

If you see the error like below, just wail a few minutes and try again

```
Deployment failed. Correlation ID: cf0b919a-2c95-4e61-829c-77c2f46b76ae. {
  "code": "NotFound",
  "message": "Request url is invalid.\r\nActivityId: fc20574c-470e-42c2-8947-08367d8425a0, Microsoft.Azure.Documents.Common/2.4.0.0"
}
```

```
Deployment failed. Correlation ID: 230eeaf2-7773-4d13-8637-dd1b3f0ea946. {
  "code": "BadRequest",
  "message": "Database account mycosmosdb is not online\r\nActivityId: e51f60b4-ff24-4e3f-a5e9-85e7791f8462, Microsoft.Azure.Documents.Common/2.4.0.0"
}
```

## Provisioning

On Azure portal

- Cosmos DB
  - Create database and container
- Stream Analytics
  - Define input and output

### Stream Analytics

Create IoT Hub input

![image](https://user-images.githubusercontent.com/767859/61112682-63200200-a4c7-11e9-86ee-3e4a0403b008.png)

Create Cosmos DB output and create new database and container

![image](https://user-images.githubusercontent.com/767859/61273650-fd908600-a7e4-11e9-8c7d-378476049562.png)

Create query

![image](https://user-images.githubusercontent.com/767859/61112870-d4f84b80-a4c7-11e9-8587-d1c8e122088d.png)


## Setup Container Instances

Setup Docker and build image

- [Setup](../dashboard/README.md#setup)
- [Build](../dashboard/README.md#build)

Login to Azure Container Registry

```
$ az acr login --name <your-acr-name>
```

Tag your docker image

```
$ docker tag dashboard-app <your-acr-name>.azurecr.io/dashboard-app:v1
```

Push image to Azure Container Registry 

```
$ docker push <your-acr-name>.azurecr.io/dashboard-app:v1
```

Deploy container from Container Registry to Container Instances

- `<your-acr-password>` : You can find on Azure Portal (Container Registry -> Access Key)
- `<your-dns-label-name>` : anything you like

```
$ az container create \
  --resource-group <your-resource-group-name> \
  --location <your-location> \
  --name dashboard-app \
  --image <your-acr-name>.azurecr.io/dashboard-app:v1 \
  --cpu 1 --memory 1 \
  --registry-login-server <your-acr-name>.azurecr.io \
  --registry-username <your-acr-name> \
  --registry-password <your-acr-password> \
  --dns-name-label <your-dns-label-name> \
  --ports 8080
```

Wait for deploy

```
$ az container show \
  --resource-group <your-resource-group-name> \
  --name dashboard-app \
  --query instanceView.state
```

When shows `Running`, deploy is finished and you can access to dashboard `http://<your-dns-label-name>.<your-location>.azurecontainer.io:8080`

### Reference

- https://docs.microsoft.com/ja-jp/azure/container-instances/container-instances-tutorial-prepare-acr
- https://docs.microsoft.com/ja-jp/azure/container-instances/container-instances-tutorial-deploy-app


## Run & Stop

On Azure portal

- press "Start" / "Stop" button on Stream Analytics Jobs
- press "Start" / "Stop" button on Container Instances
