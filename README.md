# oracli　client tool for OracleDB

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

- pyinstallerで実行ファイルにする場合
```bash
uv run pyinstaller --onedir src/oracli/cli.py
```

- 直接tool installする場合
```bash
uv tool install git+https://github.com/Yasuotem/oracli.git
```
`oracli`で実行

## 設定
環境変数または.envファイルに以下の様な形式でDBの設定を記述してください

例
- Oracleの場合
```.env
ORACLI_DB=oracle
ORACLI_USER=scott
ORACLI_PASSWORD=tiger
ORACLI_DSN=localhost:1521/orcl
```
- duckdbの場合
```.env
ORACLI_DB=duckdb
ORACLI_PATH=test.duckdb
```


## コマンド
- `add-job`

一回の実行単位になるJobを新規に作成します。Jobはyamlファイルで記録されます
```bash
oracli add-job　test_job
```

- `add-step`

sqlの実行とファイル出力を行うStepをJob内に追加します
```bash
oracli add-step test_job.yaml
```

- `run`

Jobを実行します
```bash
oracli run test_job.yaml
```

- `check`

Jobファイルで定義されているsqlファイルをsqlglotで構文チェックします
```bash
oracli check test_job.yaml
```

- `query`

単体のSQLの実行とファイル出力を行います

```bash
oracli query --sql sql/test.sql --output data/test.csv
```
