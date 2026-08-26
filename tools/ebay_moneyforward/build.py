# -*- coding: utf-8 -*-
import csv, datetime, calendar, collections
from decimal import Decimal, ROUND_HALF_UP

SRC = '/root/.claude/uploads/0c867270-6134-559c-b370-bc08d577020c'
FILES = {
    'go-go-japan':      f'{SRC}/03b1e945-TransactionAug18202603_21_36070011328269153.csv',
    'yokoso2020japan2': f'{SRC}/98b686e0-TransactionAug18202604_23_36070013321890847.csv',
    'visit3japan2':     f'{SRC}/c3793e6b-TransactionAug18202603_26_48070013321880801.csv',
}
RATE_SOURCE = 'Google Finance（GOOGLEFINANCE関数・日次終値）／スプレッドシート「eBay円換算用_日次為替レート_2025-07〜2026-06」'

SALES_TYPES  = ('Order', 'Adjustment')                      # 収益側
RETURN_TYPES = ('Refund', 'Claim', 'Payment dispute')        # 返還等
TAX_ADJ_KEYS = ('TAX Only', 'VAT Credit')                    # 売上に含める Adjustment

rates = {}
for r in csv.DictReader(open('rates.csv')):
    rates[(r['date'], r['currency'])] = Decimal(r['jpy_rate'])

def load(path):
    rows = list(csv.reader(open(path, encoding='utf-8-sig')))
    i = [k for k, r in enumerate(rows) if r and r[0] == 'Transaction creation date'][0]
    h = rows[i]
    return [dict(zip(h, r)) for r in rows[i+1:] if r and r[0].strip() and len(r) >= 30]

def dec(s):
    s = (s or '').replace(',', '').strip()
    return None if s in ('', '--') else Decimal(s)

def yen(x):
    return int(x.quantize(Decimal('1'), rounding=ROUND_HALF_UP))

detail, excluded, applied_rates = [], [], {}
for acct, path in FILES.items():
    for x in load(path):
        d = datetime.datetime.strptime(x['Transaction creation date'], '%b %d, %Y').date()
        t = x['Type']
        gross = dec(x['Gross transaction amount'])
        cur = x['Transaction currency'] if x['Transaction currency'] != '--' else ''
        desc = x['Description'] if x['Description'] != '--' else ''
        base = dict(日付=d.isoformat(), アカウント=acct, 種別=t, 注文番号=x['Order number'].replace('--',''),
                    通貨=cur, 外貨額=float(gross) if gross is not None else '', 摘要元=desc)

        if t in SALES_TYPES or t in RETURN_TYPES:
            if gross is None:                       # 複数商品注文の明細行（合計行に集約済み）
                excluded.append({**base, '除外理由': '明細行（合計行に金額集約済み・二重計上防止）'}); continue
            if t == 'Adjustment' and not any(k in desc for k in TAX_ADJ_KEYS):
                excluded.append({**base, '除外理由': f'手数料関連の調整（別資料で計上）: {desc}'}); continue
        else:
            excluded.append({**base, '除外理由': f'集計対象外の取引種別（{t}）'}); continue

        rate = rates.get((d.isoformat(), cur))
        assert rate is not None, (acct, d, cur, t)
        applied_rates[(d.isoformat(), cur)] = rate
        jpy = yen(gross * rate)
        detail.append({**base, '適用レート': float(rate), 'レート基準日': d.isoformat(),
                       'レート出典': RATE_SOURCE, '円換算額': jpy,
                       '計上区分': '売上' if t in SALES_TYPES else '売上返還等'})

# ---- 月次集計 ----
agg = collections.defaultdict(lambda: {'jpy': 0, 'fx': Decimal('0'), 'n': 0, 'cur': set()})
for r in detail:
    k = (r['日付'][:7], r['アカウント'], r['種別'])
    a = agg[k]; a['jpy'] += r['円換算額']; a['fx'] += Decimal(str(r['外貨額'])); a['n'] += 1; a['cur'].add(r['通貨'])

# ---- 仕訳 ----
AR, SALES = '売掛金', '売上高'
TAX_NONE, TAX_EXPORT, TAX_RETURN = '対象外', '輸出売上 0%', '輸出売上-返還等 0%'
journals = []
for (ym, acct, t), a in sorted(agg.items()):
    if a['jpy'] == 0: continue
    y, m = int(ym[:4]), int(ym[5:])
    date = datetime.date(y, m, calendar.monthrange(y, m)[1]).strftime('%Y/%m/%d')
    sub = f'ebay_{acct}'
    amt = abs(a['jpy'])
    forward = a['jpy'] > 0
    if t in SALES_TYPES:
        tax = TAX_EXPORT
    else:
        tax = TAX_RETURN
        forward = False if a['jpy'] < 0 else True
    if forward:   # 売上計上： 借)売掛金 / 貸)売上高
        dr, dr_tax, cr, cr_tax = AR, TAX_NONE, SALES, tax
    else:         # 売上取消： 借)売上高 / 貸)売掛金
        dr, dr_tax, cr, cr_tax = SALES, tax, AR, TAX_NONE
    label = {'Order': '売上', 'Adjustment': '調整（税額調整）', 'Refund': '返金',
             'Claim': 'クレーム返金', 'Payment dispute': '支払異議（チャージバック）'}[t]
    journals.append(dict(取引日=date, 借方勘定科目=dr, 借方補助科目=sub, 借方税区分=dr_tax, 借方金額=amt,
                         貸方勘定科目=cr, 貸方補助科目=sub, 貸方税区分=cr_tax, 貸方金額=amt,
                         摘要=f'eBay {label} {y}年{m}月 {acct}（{t} {a["n"]}件 {"/".join(sorted(a["cur"]))} {a["fx"]}）',
                         月=ym, アカウント=acct, 種別=t))

# ---- MFインポートCSV ----
MF_COLS = ['取引No','取引日','借方勘定科目','借方補助科目','借方部門','借方取引先','借方税区分','借方インボイス','借方金額(円)','借方税額',
           '貸方勘定科目','貸方補助科目','貸方部門','貸方取引先','貸方税区分','貸方インボイス','貸方金額(円)','貸方税額',
           '摘要','仕訳メモ','タグ','MF仕訳タイプ','決算整理仕訳','作成日時','作成者','最終更新日時','最終更新者']
with open('マネーフォワード仕訳インポート_eBay売上_2025年7月-2026年6月.csv','w',newline='',encoding='utf-8-sig') as f:
    w = csv.writer(f); w.writerow(MF_COLS)
    for i, j in enumerate(journals, 1):
        w.writerow([i, j['取引日'], j['借方勘定科目'], j['借方補助科目'], '', '', j['借方税区分'], '', j['借方金額'], 0,
                    j['貸方勘定科目'], j['貸方補助科目'], '', '', j['貸方税区分'], '', j['貸方金額'], 0,
                    j['摘要'], '', '', '', '', '', '', '', ''])

import json
json.dump({'detail_n': len(detail), 'excluded_n': len(excluded), 'journals_n': len(journals),
           'total_jpy': sum(r['円換算額'] for r in detail)}, open('stats.json','w'))
import pickle
pickle.dump((detail, excluded, dict(agg), journals, applied_rates), open('data.pkl','wb'))
print('明細', len(detail), '除外', len(excluded), '仕訳', len(journals), '円合計', f"{sum(r['円換算額'] for r in detail):,}")
