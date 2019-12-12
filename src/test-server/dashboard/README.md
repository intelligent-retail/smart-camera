# Dashboard

\* Working directory: `<repository_root_dir>/src/test-server/dashboard`

## Setup

- rename `.env_sample` to `.env` and fill your settings
  - `ENDPOINT` : Cosmos DB URI
  - `PRIMARYKEY` : Cosmos DB Primary Key
  - `DATABASE` : Cosmos DB Database Name
  - `CONTAINER` : Cosmos DB Container Name 

- rename `camera_settings_sample.json` to `camera_settings.json` and fill your settings

```json
{
  "map": {
    "image": {
      "width": 886,
      "height": 862,
      "src": "https://example.com/store.jpg"
    },
    "areas": [
      { "id": "0", "coords": [390, 137, 480, 251] },
      { "id": "1", "coords": [373, 120, 495, 283] }
    ]
  },
  "cameras": [
    { "id": "0", "name": "Entrance" },
    { "id": "1", "name": "Cashier" }
  ]
}
```

- `map` : Optional. HTML Image Map definition
  - `image`
    - `src` : String. Url of image
    - `width` : Integer. Image width [px]
    - `height` : Integer. Image height [px]
  - `areas` : Array
    - `id` : String. Correspond to the value in `cameras`
    - `coords`: Array. Coordinates of `<area shape="rect">`. [left, top, right, bottom]
- `cameras` : Array. Required.
  - `id` : String. Need to be unique and same as CameraID (camID)
  - `name` : String

## Docker

### Build

```
$ docker build -t dashboard-app .
```

### Run

```
$ docker run -it -p 8080:8080 dashboard-app
```

### Deploy 

#### Deploy container to Azure Container Registry

- Install and setup Azure CLI
  - https://docs.microsoft.com/ja-jp/cli/azure/install-azure-cli?view=azure-cli-latest
- Create your resource group and push container to Azure Container Registry
  - https://docs.microsoft.com/ja-jp/azure/container-instances/container-instances-tutorial-prepare-acr

#### Deploy to Azure Container Instances

- Deploy your container to Azure Container Registry
  - https://docs.microsoft.com/ja-jp/azure/container-instances/container-instances-tutorial-deploy-app
- You can see the dashboard at `http://<Your FQDN>:8080/`


## Development on local environment

### Setup

- Requires Node.js v10.16.0 or higher

```
$ npm i
```

### Run

```
$ npm run dev
```
