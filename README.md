# SE職 二次応募/追加募集 監視システム

NTTデータ・野村総合研究所・日立製作所・富士通・トヨタ自動車・ソニーグループの6社について、新卒SE職の**二次応募**・**追加募集**が掲載された際に `m.shinoharaforrecruit@gmail.com` へ自動通知するシステムです。

## 監視対象

| 企業 | 監視URL |
|------|---------|
| NTTデータ | nttdata-recruit.com |
| 野村総合研究所 | working.nri.co.jp/recruit |
| 日立製作所 | hitachi.com/ja-jp/recruit |
| 富士通 | fujitsu.recruiting.jp.fujitsu.com |
| トヨタ自動車 | recruit.toyota |
| ソニーグループ | recruit.sony.co.jp/2027 |

## 検出ロジック

各社の採用ページを定期的に取得し、以下のキーワードを検出します。

- **二次募集系**: 二次応募、追加募集、再募集、エントリー再開 など
- **SE系**: SE、システムエンジニア、ソリューションエンジニア など

両方のキーワードが同一ページ内に存在する場合に通知します。重複通知を防ぐため、ページ内容のハッシュを記録し、変更があった場合のみ通知します。

## セットアップ

### 1. 依存関係のインストール

```bash
cd se-recruit-monitor
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Gmail アプリパスワードの取得

1. [Google アカウント](https://myaccount.google.com/) にログイン
2. **セキュリティ** → **2段階認証** を有効化
3. **アプリパスワード** を生成（[直接リンク](https://myaccount.google.com/apppasswords)）
4. 生成された16文字のパスワードを控える

### 3. 環境変数の設定

```bash
cp .env.example .env
```

`.env` を編集:

```
SMTP_USER=送信元Gmailアドレス@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
NOTIFY_EMAIL_TO=m.shinoharaforrecruit@gmail.com
```

## 使い方

### 1回だけチェック

```bash
python main.py --once
```

### ドライラン（メール送信なし）

```bash
python main.py --dry-run -v
```

### 常時監視（1時間ごと）

```bash
python main.py --loop --interval 3600
```

## Windows タスクスケジューラ（推奨）

PCを常時起動している場合、1時間ごとの自動実行:

```powershell
# 管理者権限 PowerShell で実行
.\scripts\setup_windows_task.ps1
```

## GitHub Actions（24時間監視）

リポジトリ: [MSforMurataLab/se-recruit-monitor](https://github.com/MSforMurataLab/se-recruit-monitor)

6時間ごとに自動実行されます（手動実行: Actions → SE Recruit Monitor → Run workflow）。

### Secrets の設定（必須）

[Settings → Secrets and variables → Actions](https://github.com/MSforMurataLab/se-recruit-monitor/settings/secrets/actions) で以下を登録:

| Secret | 入力する値（例） |
|--------|----------------|
| `SMTP_USER` | `yourname@gmail.com`（実際のGmailアドレス） |
| `SMTP_PASSWORD` | `abcd efgh ijkl mnop`（アプリパスワード16文字） |
| `NOTIFY_EMAIL_TO` | `m.shinoharaforrecruit@gmail.com`（通知先メール） |

> **注意:** 「送信元 Gmail アドレス」のような説明文をそのまま入力しないでください。実際のアドレス・パスワードを入力します。

Secrets 設定後、Actions タブから手動実行して動作確認できます。

## ファイル構成

```
se-recruit-monitor/
├── main.py              # エントリポイント
├── config.yaml          # 監視対象・キーワード設定
├── monitor/
│   ├── checker.py       # 監視メインロジック
│   ├── fetcher.py       # ページ取得
│   ├── matcher.py       # キーワード判定
│   ├── notifier.py      # メール送信
│   └── storage.py       # 状態管理
├── data/state.json      # 監視状態（自動生成）
└── .github/workflows/   # GitHub Actions
```

## カスタマイズ

`config.yaml` で以下を変更できます:

- 監視URL の追加・変更
- キーワードの追加
- 通知先メールアドレス

## 注意事項

- 各社の採用サイト構造変更により取得に失敗する場合があります。その際は `config.yaml` の URL を更新してください。
- 「追加日程」（セミナー等）も検出対象に含めています。誤検知の場合は `config.yaml` からキーワードを削除してください。
- Gmail の送信制限（1日500通程度）内で運用してください。
