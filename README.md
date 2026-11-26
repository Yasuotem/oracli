# oracli　client tool for oracleDB

## 特徴
主に自分用のOracleDBのクライアントツール
- SQLを実行してファイル出力する処理を複数登録して実行することができます

タスクスケジューラ等に設定して実行するような用途を想定して作成しました
- 対話的に処理の登録ができます
- csv, parquetの出力に対応しています
- 日付を利用したsqlのパラメータ変数に対応しています
- 営業日等の日付の変更時間の設定ができます

## インストール
uvを使用します

```bash
git clone https://github.com/Yasuotem/oracli.git
uv sync
```
`uv run oracli`で実行

pyinstallerで実行ファイルにする場合
```bash
uv run pyinstaller --onedir src/oracli/cli.py
```

直接tool installする場合
```bash
uv tool install git+https://github.com/Yasuotem/oracli.git
```
`oracli`で実行

## コマンド
```bash
oracli add-job
```
