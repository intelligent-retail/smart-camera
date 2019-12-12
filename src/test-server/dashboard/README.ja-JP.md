# ダッシュボード

※ 作業ディレクトリ：`<repository_root_dir>/src/test-server/dashboard`

## Setup

- `.env_sample` を `.env` にリネームし、必要設定を入れる
  - `ENDPOINT` : Cosmos DB URI
  - `PRIMARYKEY` : Cosmos DB プライマリ キー
  - `DATABASE` : Cosmos DB データベース名
  - `CONTAINER` : Cosmos DB コンテナ名

- `camera_settings_sample.json` を `camera_settings.json` にリネームし、必要設定の追加/変更を行う

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

- `map` : （オプション）カメラレイアウト図の定義
  - `image`
    - `src` : String - 画像の URL
    - `width` : Integer - 画像の幅 [px]
    - `height` : Integer - 画像の高さ [px]
  - `areas` : Array
    - `id` : String - `cameras` に設定した値に対応する
    - `coords`: Array - `<area shape="rect">` に対応する座標値 [left, top, right, bottom]
- `cameras` : Array （必須）
  - `id` : String - ユニークな値でカメラ ID (camID) に一致しなければならない
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

#### Azure Container Registry にイメージをデプロイ

- Azure CLI をインストール
  - https://docs.microsoft.com/ja-jp/cli/azure/install-azure-cli?view=azure-cli-latest
- Azure Container Registry にイメージをプッシュ
  - https://docs.microsoft.com/ja-jp/azure/container-instances/container-instances-tutorial-prepare-acr

#### Azure Container Instances にコンテナをデプロイ

- コンテナをデプロイ
  - https://docs.microsoft.com/ja-jp/azure/container-instances/container-instances-tutorial-deploy-app
- 下記アドレスでダッシュボードにアクセスしてください：`http://<Your FQDN>:8080/`


## ローカル環境下での開発

### Setup

- 要件： Node.js >=10.16.0

```
$ npm i
```

### Run

```
$ npm run dev
```
