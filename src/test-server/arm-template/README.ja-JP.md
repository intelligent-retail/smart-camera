
# ダッシュボードサーバをデプロイする

※ 作業ディレクトリ：`<repository_root_dir>/src/test-server/arm-template`

## デプロイ対象

- Stream Analytics
- Cosmos DB
- Container Instances

## 環境セットアップ

Azure CLI をインストールしてアカウントにログイン

- https://docs.microsoft.com/ja-jp/cli/azure/

`deploy.sh` - リソースグループの名前及び場所を置き換える

```
# replace with your resource group location
LOCATION=japaneast

# replace with your resource group name
RESOURCE_GROUP=myresourcegroup
```

`parameters.json` - リソースグループ及び Cosmos DB の名前を置き換える

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

## デプロイ

### Azure リソースを作成

- Stream Analytics
- Cosmos DB

```
$ sh deploy.sh
```

下記のようなエラーが出る場合は数分間の間隔を開けてから再度実行してください：

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

## プロビジョニング

Azure ポータルサイトにて設定を行う

- Cosmos DB
  - データベース及びコンテナを作成
- Stream Analytics
  - 入力出力を定義

### Stream Analytics

IoT Hub 入力を新規追加

![image](https://user-images.githubusercontent.com/767859/61112682-63200200-a4c7-11e9-86ee-3e4a0403b008.png)

Cosmos DB 出力を新規追加し、データベース及びコンテナを新規作成

![image](https://user-images.githubusercontent.com/767859/61273650-fd908600-a7e4-11e9-8c7d-378476049562.png)

クエリを作成

![image](https://user-images.githubusercontent.com/767859/61112870-d4f84b80-a4c7-11e9-8587-d1c8e122088d.png)


## Setup Container Instances

設定をセットアップし、Docker イメージを作成

- 設定：[Setup](../dashboard/README.ja-JP.md#setup)
- イメージ作成：[Build](../dashboard/README.ja-JP.md#build)

Azure Container Registry にログイン

```
$ az acr login --name <your-acr-name>
```

Docker イメージにタグを追加

```
$ docker tag dashboard-app <your-acr-name>.azurecr.io/dashboard-app:v1
```

Azure Container Registry 上に Docker イメージをプッシュ

```
$ docker push <your-acr-name>.azurecr.io/dashboard-app:v1
```

Container Registry から Container Instances へコンテナをデプロイ

- `<your-acr-password>` : Azure ポータルサイトから確認 (Container Registry -> Access Key)
- `<your-dns-label-name>` : 任意の名前

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

デプロイ終了まで時間がかかる可能性があり、下記コマンドでデプロイ状態を確認できる：

```
$ az container show \
  --resource-group <your-resource-group-name> \
  --name dashboard-app \
  --query instanceView.state
```

コマンド結果に `Running` が表示されたら、下記アドレスでダッシュボードにアクセスしてください：`http://<your-dns-label-name>.<your-location>.azurecontainer.io:8080`

### Reference

- https://docs.microsoft.com/ja-jp/azure/container-instances/container-instances-tutorial-prepare-acr
- https://docs.microsoft.com/ja-jp/azure/container-instances/container-instances-tutorial-deploy-app


## 開始 & 停止

Azure ポータルサイトにて

- Stream Analytics Jobs ページで "開始" / "停止" ボタンをクリック
- Container Instances ページで "開始" / "停止" ボタンをクリック
