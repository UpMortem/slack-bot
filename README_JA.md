# Haly AI Slack Bot

GPTによって駆動されるチャットボットで、セマンティック検索を使用して組織に関する質問に答えることができます。

## 特徴

- ユーザーの質問にリアルタイムで応答します。
- OpenAI APIを使用して回答を生成します。
- チャットチャネルで直接回答を提供するためにSlackと統合します。

## インストール

1. このリポジトリをクローンします。
2. `pip install -r requirements.txt`で依存関係をインストールします。
3. 必要な環境変数を設定します（設定セクションを参照）。
4. `python main.py`でボットを実行します。

## 設定

次の環境変数が必要です：

- `SLACK_BOT_TOKEN`: Slackボットのトークン。
- `SLACK_SIGNING_SECRET`: Slackアプリの署名シークレット。
- `OPENAI_API_KEY`: OpenAI APIのキー。

## ライセンス

このプロジェクトはGNU Affero General Public License v3.0の下でライセンスされています。詳細は[LICENSE](LICENSE)ファイルをご覧ください。
