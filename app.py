import os
import logging
from collections import defaultdict, deque
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
)
import anthropic

# ── ログ設定 ──────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── 設定 ──────────────────────────────────────────────────
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

# 会話履歴の保持ターン数（ユーザーメッセージ＋アシスタント返答の組）
MAX_HISTORY_TURNS = 5

# ── システムプロンプト ────────────────────────────────────
SYSTEM_PROMPT = """あなたは AIニュースと税務に特化した日本語の汎用アシスタントです。

【得意分野】
- AIの最新ニュース・技術トレンド・主要モデルのアップデート情報
- 日本の税務相談（所得税・法人税・消費税・確定申告・経費処理など）
- 上記に関連する一般的なビジネス質問

【回答スタイル】
- 簡潔かつ丁寧な日本語で回答する
- 税務については「一般的な情報」として提供し、個別の判断は税理士に相談するよう促す
- 情報の出典や根拠が不確かな場合は正直に伝える
- LINE上での読みやすさを意識し、適度に改行を入れる

税務アドバイスは参考情報であり、正式な税務申告には必ず税理士・公認会計士にご相談ください。"""

# ── Flask アプリ ──────────────────────────────────────────
app = Flask(__name__)

# ── LINE SDK 初期化 ───────────────────────────────────────
handler = WebhookHandler(LINE_CHANNEL_SECRET)
line_config = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)

# ── Anthropic クライアント ────────────────────────────────
claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ── 会話履歴ストア（メモリ内）────────────────────────────
# key: user_id (str)  value: deque of {"role": ..., "content": ...}
conversation_histories: dict[str, deque] = defaultdict(
    lambda: deque(maxlen=MAX_HISTORY_TURNS * 2)
)


def get_claude_response(user_id: str, user_message: str) -> str:
    """ユーザーのメッセージを受け取り、会話履歴を使って Claude から返答を得る。"""
    history = conversation_histories[user_id]

    # ユーザーメッセージを履歴に追加
    history.append({"role": "user", "content": user_message})

    try:
        response = claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=list(history),
        )
        assistant_text = response.content[0].text

        # アシスタント返答を履歴に追加
        history.append({"role": "assistant", "content": assistant_text})
        return assistant_text

    except anthropic.APIError as e:
        logger.error("Claude API error: %s", e)
        # 失敗したユーザーメッセージを履歴から取り除く
        history.pop()
        return "申し訳ありません、回答の生成中にエラーが発生しました。しばらくしてからもう一度お試しください。"


# ── Webhook エンドポイント ────────────────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    logger.info("Request body: %s", body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.warning("Invalid signature")
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    """テキストメッセージを受け取り、Claude の返答を LINE に送信する。"""
    user_id = event.source.user_id
    user_message = event.message.text
    logger.info("user_id=%s message=%s", user_id, user_message)

    reply_text = get_claude_response(user_id, user_message)

    with ApiClient(line_config) as api_client:
        line_api = MessagingApi(api_client)
        line_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)],
            )
        )


# ── ヘルスチェック ────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
