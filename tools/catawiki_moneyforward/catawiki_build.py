# -*- coding: utf-8 -*-
import csv, collections, calendar, datetime, pickle, openpyxl
from decimal import Decimal, ROUND_HALF_UP

SRC = '/root/.claude/uploads/0c867270-6134-559c-b370-bc08d577020c/4df002aa-catawiki_Orders_1786330945_b30160d.xlsx'
RATE_SOURCE = 'Google Finance（GOOGLEFINANCE関数・日次終値）／スプレッドシート「catawiki円換算用_EURレート_2026-05〜06」'
CUR = 'EUR'

rates = {r['date']: Decimal(r['eurjpy']) for r in csv.DictReader(open('catawiki_rates.csv'))}
ws = openpyxl.load_workbook(SRC, data_only=True).active
rows = list(ws.iter_rows(values_only=True)); hdr = rows[0]
data = [dict(zip(hdr, r)) for r in rows[1:] if any(x is not None for x in r)]

def dec(v):
    return Decimal('0') if v is None else Decimal(str(v))
def yen(x):
    return int(x.quantize(Decimal('1'), rounding=ROUND_HALF_UP))

detail, excluded = [], []
for d in data:
    bid, ship = dec(d['Highest bid']), dec(d['Shipping costs'])
    fee = dec(d['Commission (incl. VAT)'])
    base = dict(注文番号=d['Order'] or '', 品名=(d['Object name'] or '')[:60], 国=d['Country'] or '',
                落札額=float(bid), 送料=float(ship), 手数料=float(fee), 請求書番号=d['Invoice number'] or '')
    if d['Order date'] is None or d['Cancellation date'] is not None:
        cd = d['Cancellation date']
        excluded.append({**base, '日付': cd.date().isoformat() if cd else '',
                         '除外理由': f'キャンセル済み（Cancellation date {cd.date().isoformat() if cd else "-"}／Payment status {d["Payment status"]}）'})
        continue
    dt = d['Order date'].date()
    gross = bid + ship
    rate = rates[dt.isoformat()]
    detail.append({**base, '日付': dt.isoformat(), '通貨': CUR, '売上額(外貨)': float(gross),
                   '適用レート': float(rate), 'レート基準日': dt.isoformat(), 'レート出典': RATE_SOURCE,
                   '円換算額': yen(gross * rate), '入金予定日': d['Payment date'].date().isoformat() if d['Payment date'] else '',
                   '手数料(外貨)': float(fee)})

agg = collections.defaultdict(lambda: {'jpy': 0, 'fx': Decimal('0'), 'n': 0, 'fee': Decimal('0')})
for r in detail:
    a = agg[r['日付'][:7]]
    a['jpy'] += r['円換算額']; a['fx'] += Decimal(str(r['売上額(外貨)'])); a['n'] += 1
    a['fee'] += Decimal(str(r['手数料(外貨)']))

journals = []
for ym, a in sorted(agg.items()):
    y, m = int(ym[:4]), int(ym[5:])
    date = datetime.date(y, m, calendar.monthrange(y, m)[1]).strftime('%Y/%m/%d')
    journals.append(dict(取引日=date, 借方勘定科目='売掛金', 借方補助科目='catawiki', 借方税区分='対象外', 借方金額=a['jpy'],
                         貸方勘定科目='売上高', 貸方補助科目='catawiki', 貸方税区分='輸出売上 0%', 貸方金額=a['jpy'],
                         摘要=f'catawiki 売上 {y}年{m}月（{a["n"]}件 EUR {a["fx"]}）', 月=ym))

MF_COLS = ['取引No','取引日','借方勘定科目','借方補助科目','借方部門','借方取引先','借方税区分','借方インボイス','借方金額(円)','借方税額',
           '貸方勘定科目','貸方補助科目','貸方部門','貸方取引先','貸方税区分','貸方インボイス','貸方金額(円)','貸方税額',
           '摘要','仕訳メモ','タグ','MF仕訳タイプ','決算整理仕訳','作成日時','作成者','最終更新日時','最終更新者']
with open('マネーフォワード仕訳インポート_catawiki売上_2026年5月-6月.csv','w',newline='',encoding='utf-8-sig') as f:
    w = csv.writer(f); w.writerow(MF_COLS)
    for i, j in enumerate(journals, 1):
        w.writerow([i, j['取引日'], j['借方勘定科目'], j['借方補助科目'], '', '', j['借方税区分'], '', j['借方金額'], 0,
                    j['貸方勘定科目'], j['貸方補助科目'], '', '', j['貸方税区分'], '', j['貸方金額'], 0,
                    j['摘要'], '', '', '', '', '', '', '', ''])

pickle.dump((detail, excluded, dict(agg), journals), open('catawiki.pkl','wb'))
for ym, a in sorted(agg.items()):
    print(ym, a['n'], '件  EUR', a['fx'], ' →', f"{a['jpy']:,}円", ' 手数料 EUR', a['fee'])
print('計上', len(detail), '件 / 除外', len(excluded), '件 / 円合計', f"{sum(r['円換算額'] for r in detail):,}")
print('除外:', [(e['日付'], e['落札額'], e['送料']) for e in excluded])
