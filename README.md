# Ansible dynamic inventory for sakura cloud

## 動作条件

- Python 3
- [usacloud](https://github.com/sacloud/usacloud)


## インストール

実行に必要なファイルは `sacloud_inventory.py` の1つなので、ファイルを単にダウンロードすることでも可能です。

```
$ git init # まだ行っていない場合
$ git submodule add https://github.com/sakura-internet/sacloud-ansible-inventory.git
```


## インスタンスオプション

インスタンス説明文にJSON文字列を指定することで、細かな挙動を制御することが出来ます。

```json
{
  "sacloud_inventory": {
    "hostname_type": "nic1_ip",
    "host_vers": {
      "sample-key": "sample-value"
    }
  }
}
```

### .sacloud_inventory.hostname_type

`ansible_host` 変数に利用される項目を制御します。
ドメイン名・任意のNICに設定されるIPアドレスを設定することが出来ます。

設定値|説明
---|---
instance_name|デフォルト挙動です。コントロールパネルで指定されたインスタンスの名前を使用します。インスタンスの名前にドメイン名を利用している場合に使用します。
nic0_ip|1個目のNIC(eth0)にコントロールパネルで指定されたIPアドレスを使用します。共有グローバルアドレスが利用できる際は、そのIPアドレスを指定します。
nicN_ip|2個目以降のNICのIPアドレスを指定する際は、Nを数字に置き換えてください。

### .sacloud_inventory.host_vers

Ansibleで利用する追加のホストの変数を指定します。


## 環境変数

### SACLOUD_INVENTORY_FILTER_TAGS

初期状態では、 `__with_sacloud_inventory` タグが付与されたインスタンスのみ結果に出力されます。
カンマ区切りで環境変数を設定することで、フィルタを上書きすることが出来ます。

```shell script
# タグ__with_sacloud_inventoryとcluster1が付いているインスタンスのみを対象にする
SACLOUD_INVENTORY_FILTER_TAGS=__with_sacloud_inventory,cluster1 ./sacloud_inventory.py
```
