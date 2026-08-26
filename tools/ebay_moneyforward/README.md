# eBay取引レポート → マネーフォワード仕訳インポート

eBay Seller Hub の Transaction report（アカウント別CSV）から、月次・アカウント別に売上を集計し、
マネーフォワードクラウド会計の仕訳インポートCSVと、換算根拠付きの集計Excelを生成する。

## 集計ルール

| 項目 | 内容 |
|---|---|
| 対象取引種別 | `Order` / `Adjustment`（税額調整分のみ） / `Refund` / `Claim` / `Payment dispute` |
| 除外 | `Other fee` / `Payout` / `Charge` / `Hold` / `Shipping label`、手数料関連の`Adjustment`（別資料で計上） |
| 計上金額 | `Gross transaction amount`（商品代＋送料。eBay代理徴収税は含まない） |
| 二重計上防止 | 複数商品注文は合計行のみ計上し、金額欄が空欄の明細行は除外 |
| 円換算 | 取引ごとに `Transaction creation date` のレートで換算、円未満四捨五入 |
| 仕訳 | 月×アカウント×種別で1本に集約し、各月末日付で起票 |

## 仕訳パターン

- 売上計上: 借）売掛金［対象外］／ 貸）売上高［輸出売上 0%］
- 返金・クレーム・支払異議: 借）売上高［輸出売上-返還等 0%］／ 貸）売掛金［対象外］
- 補助科目はアカウント別（`ebay_<アカウント名>`）

## 為替レート

`rates.csv`（`date,currency,jpy_rate`）を参照する。レート表はGoogleスプレッドシートの
GOOGLEFINANCE関数で作成する:

```
=GOOGLEFINANCE("CURRENCY:USDJPY","close",DATE(2025,7,1),DATE(2026,6,30),"DAILY")
```

市場終値であり銀行公示のTTM（仲値）ではないため、継続適用を前提とする。
銀行TTMを使う場合は `rates.csv` を差し替えれば他の処理は変更不要。

## 実行

```bash
pip install openpyxl
python3 build.py   # 明細集計 → MF仕訳インポートCSV + data.pkl
python3 xlsx.py    # data.pkl → 集計Excel
```

`build.py` 冒頭の `FILES`（アカウント名 → Transaction reportのパス）を対象期間に合わせて書き換える。
