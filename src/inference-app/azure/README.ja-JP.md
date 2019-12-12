# Azure IoT エッジデバイスをデプロイする

## システム環境要件

- 開発 PC（OS：Ubuntu 18.04）
- Raspberry Pi 3B+（OS：Raspbian Stretch）
    - microSDCard 32GB A1 V30
    - Movidius NCS2（NCS1も可）
    - Raspberry Pi カメラモジュール V2.1

## 開発 PC の環境構築

### [Azure CLI](https://docs.microsoft.com/ja-jp/cli/azure/install-azure-cli-apt?view=azure-cli-latest) をインストール

```bash
# Install Azure CLI
$ curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to your Azure Account
$ az login

# Add Microsoft Azure IoT Extension for Azure CLI
$ az extension add --name azure-cli-iot-ext
```

### このレポジトリをクローンし、必要なソフトウェアをインストール

※ 作業ディレクトリ：`<repository_root_dir>/src/inference-app/azure`

```bash
$ ./0-setup-pc-enviroment.sh
```

- Docker を新規インストールした場合、 `docker` コマンドを sudo なしで利用するため、現在のユーザーを docker グループに追加する必要がある：
```bash
$ sudo usermod -aG docker $(whoami)
```

## Raspberry Pi の環境構築

### 本体セットアップ

- Raspbian イメージをダウンロード：
http://downloads.raspberrypi.org/raspbian/images/raspbian-2019-04-09/

- Etcher（SD カード書き込みツール）をダウンロードし、開発 PC にインストール：
https://www.balena.io/etcher/

- 公式ガイドに従い、microSD カードに Raspbian イメージを書き込む：
https://www.raspberrypi.org/documentation/installation/installing-images/

- カメラモジュール、Movidius NCS2 及び microSD カードを Raspberry Pi 本体に差し込み、電源を入れる
    - 初回起動時に OS の初期設定を行う必要がある
    - SSH 及びカメラ、必要に応じて VNC も有効にしてください

- 直接 Raspberry Pi 本体にアクセスできない場合：
    - microSD カードのブートパーティションに `ssh` という名前のファイルを作成し、Raspberry Pi 起動後に SSH で接続してください（詳細については [公式ガイド](https://www.raspberrypi.org/documentation/remote-access/ssh/) をご参照ください）
    - Raspberry Pi にログイン後、下記コマンドで初期設定を行い、カメラを（必要であればVNCも）有効にしてください：`sudo raspi-config`

### 必須ライブラリのセットアップ

- [OpenVINO ツールキット](https://download.01.org/opencv/2019/openvinotoolkit/R1/l_openvino_toolkit_raspbi_p_2019.1.094.tgz) を Raspberry Pi 上にダウンロード
- 下記コマンドに従い、`/opt/intel/inference_engine_vpu_arm` に解凍したツールキットを配置：
    ```bash
    $ tar xzf l_openvino_toolkit_raspbi_p_<version>.tgz
    $ sudo mkdir /opt/intel/ && sudo mv inference_engine_vpu_arm /opt/intel/
    ```
- 下記コマンドに従い、Raspberry Pi カメラモジュールの設定を行ってください：
    ```bash
    $ sudo /bin/bash -c 'echo "bcm2835-v4l2"  >> /etc/modules'
    $ sudo reboot
    ```

## Azure リソース及びエッジデバイスのデプロイ

### 必要リソースの作成（開発 PC 側）

- 環境設定ファイル [.deploy.env](.deploy.env#L1) を編集し、Azure Resource に関する各種変数を設定：
    ```
    RESOURCE_GROUP=
    LOCATION=
    ACR_NAME=
    HUB_NAME=
    DEVICE_ID=
    ```

- スクリプト1~3を順次に実行：
    ```bash
    # Setup Azure Rersource (Resource Group, Container Registry, IoT Hub)
    $ ./1-deploy-azure-resources.sh

    # Build Image and push to Azure Container Registry
    $ ./2-build-image-and-push-acr.sh

    # Register Edge Device on Azure IoT Hub
    $ ./3-register-edge-device.sh
    ```

### エッジデバイス（Raspberry Pi）側の設定

- `edge-runtime` フォルダー全体をエッジデバイスにコピーし、中にあるスクリプト4を実行：
    ```bash
    # Setup Docker and IoT Edge Runtime for Raspberry Pi
    $ ./4-setup-edge-device.sh
    ```
- スクリプトが正常終了時に出力されるデバイス ID（`camID`）を記録してください
- 下記フォルダーがスクリプトによって自動的に作成される：`/home/pi/Desktop/videos`

### モジュールを Azure IoT Hub にデプロイ（開発 PC 側）

- 引き続き開発 PC にて環境設定ファイル [.deploy.env](.deploy.env#L50) を編集し、ビデオ入力モードを指定（デフォルトでは [PiCamera mode](.deploy.env#L52) を使用）
- ビデオファイルを入力として使用したい場合（[Video files mode](.deploy.env#L61)）、入力ファイルをエッジデバイス `/home/pi/Desktop/videos/input` の直下に配置してください

- スクリプト5を実行し、モジュールのデプロイを行う（デバイス側で全部のモジュールが正常に起動されるまで時間がかかる可能性がある）：
    ```bash
    # Deploy edge module to Azure IoT Hub
    $ ./5-deploy-edge-module.sh
    ```

#### Azure IoT Hub からデプロイ済みのモジュールを削除したい場合

- （開発 PC 側で）スクリプト6を実行：
    ```bash
    # Delete module from Azure Iot Hub
    $ ./6-delete-edge-module.sh
    ```
