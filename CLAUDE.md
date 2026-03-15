# CLAUDE.md

このファイルは、このリポジトリで作業するAIアシスタント（Claude Codeなど）向けのガイドラインです。

## リポジトリ概要

- **リポジトリ**: nobu-jp/nobu_claude
- **ステータス**: 新規作成 — まだソースコードはコミットされていません
- **メインブランチ**: `main`（またはプロジェクトオーナーが設定したブランチ）

> ソースコードが追加されたら、実際のプロジェクトの目的・技術スタック・構成を反映してこのファイルを更新してください。

## Gitワークフロー

### ブランチ命名規則

- Claudeが作成するブランチは必ず `claude/<説明>-<セッションID>` の形式に従うこと
  - 例: `claude/add-claude-documentation-Tg7np`
- 人間が作成するフィーチャーブランチ: `feature/<説明>` または `<作者>/<説明>`

### コミットメッセージの規則

明確で命令形のコミットメッセージを書くこと:

```
Add CLAUDE.md with initial repository documentation
Fix authentication bug in login flow
Update dependencies to latest versions
```

- 件名は72文字以内に収める
- 現在形を使う（"Added" ではなく "Add"）
- 関連するIssue番号があれば参照する: `Fix login bug (#42)`

### プッシュの手順

```bash
# 初回プッシュ時は必ずアップストリームを設定する
git push -u origin <ブランチ名>
```

- **`main`/`master` へのフォースプッシュは絶対に禁止**
- ネットワークエラーでプッシュが失敗した場合は、指数バックオフ（2秒、4秒、8秒、16秒）で最大4回リトライする

## 開発環境セットアップ

> ソースコードが追加された後に記載してください。

一般的なセットアップ手順:

1. リポジトリをクローン
2. 依存関係をインストール（例: `npm install`、`pip install -r requirements.txt` など）
3. 環境設定をコピー: `cp .env.example .env` して値を記入
4. 開発サーバーまたはビルドを実行

## テスト

> テストが設定されたら記載してください。

コミット前にテストを実行すること。主なコマンド:

```bash
# JavaScript/TypeScript
npm test
npm run test:watch

# Python
pytest
python -m pytest tests/

# Go
go test ./...
```

## コードスタイルとリント

> リンター・フォーマッターが設定されたら記載してください。

コミット前に必ずリンターとフォーマッターを実行すること:

```bash
# JavaScript/TypeScript（一般的）
npm run lint
npm run format

# Python（一般的）
ruff check .
black .
```

## プロジェクト構成

> ソースコードが追加されたら更新してください。

```
nobu_claude/
├── CLAUDE.md          # このファイル
├── README.md          # 人間向けドキュメント（プロジェクト設定時に追加）
├── .gitignore         # 使用する技術スタックに合わせた除外設定
└── src/               # ソースコード（作成予定）
```

## AIアシスタント向け重要規則

1. **編集前に必ず読む** — ファイルを変更する前に必ず内容を確認する
2. **最小限の変更** — タスクに必要な変更のみ行い、無関係なコードのリファクタリングは避ける
3. **シークレットをコードに含めない** — APIキー・パスワード・トークンは絶対にコミットしない。環境変数を使用する
4. **破壊的な操作は確認を取る** — ファイル削除・データ削除・フォースプッシュの前に必ず確認する
5. **このファイルを最新に保つ** — プロジェクト構成やワークフローが変わったら CLAUDE.md を更新する
6. **セキュリティ最優先** — OWASP Top 10の脆弱性（SQLインジェクション、XSS、コマンドインジェクションなど）を混入させない

## 環境変数

> プロジェクトが設定されたら必要な環境変数をここに記載してください。

```
# 例
DATABASE_URL=postgres://user:password@localhost:5432/dbname
API_KEY=your_api_key_here
```

`.env` ファイルは絶対にコミットしないこと。`.env.example` をプレースホルダー値のテンプレートとして使用する。
