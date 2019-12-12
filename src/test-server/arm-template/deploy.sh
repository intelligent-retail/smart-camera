#!/usr/bin/env bash

# replace with your resource group location
LOCATION=japaneast

# replace with your resource group name
RESOURCE_GROUP=myresourcegroup


# Create Resource Group
az group create \
  --name ${RESOURCE_GROUP} \
  --location ${LOCATION}

# Deploy resources into the resource group
az group deployment create \
  --resource-group ${RESOURCE_GROUP} \
  --template-file template.json \
  --parameters @parameters.json \

