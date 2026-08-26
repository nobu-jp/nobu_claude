# catawiki Orders → マネーフォワード仕訳インポート

catawiki Seller の Orders レポート（.xlsx）から月次売上を集計し、マネーフォワードクラウド会計の
仕訳インポートCSVと、換算根拠付きの集計Excelを生成する。

## 集計ルール

| 項目 | 内容 |
|---|---|
| 計上額 | `Highest bid`（落札額）＋ `Shipping costs`（送料）の総額 |
| 計上日 | `Order date`（落札・注文成立日） |
| 通貨 | EUR建て |
| 除外 | `Cancellation date` があるキャンセル取引（`Order date` が空） |
| 手数料 | `Commission (incl. VAT)` は控除せず、別資料で費用計上（明細に参考表示） |
| 円換算 | 取引ごとに `Order date` のEUR/JPYレートで換算、円未満四捨五入 |
| 仕訳 | 月次1本、各月末日付 |

## 仕訳パターン

借）売掛金［catawiki］対象外 ／ 貸）売上高［catawiki］輸出売上 0%

## 為替レート

`catawiki_rates.csv`（`date,eurjpy`）を参照する。レート表はGoogleスプレッドシートの
GOOGLEFINANCE関数で作成する（eBay側と同一の出典に揃える）:

```
=IFERROR(INDEX(GOOGLEFINANCE("CURRENCY:EURJPY","close",DATE(2026,6,30)),2,2),"NA")
```

## 実行

```bash
pip install openpyxl
python3 catawiki_build.py   # 集計 → MF仕訳インポートCSV + catawiki.pkl
python3 catawiki_xlsx.py    # catawiki.pkl → 集計Excel
```

`catawiki_build.py` 冒頭の `SRC`（Ordersレポートのパス）を対象期間に合わせて書き換える。
