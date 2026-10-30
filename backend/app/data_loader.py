"""CSV-backed Susenas data processing and regional intelligence indicators."""
import glob
import json
import os
from typing import Any, Dict, List

import numpy as np
import pandas as pd

PROV_METADATA = {
    'Aceh': ('ID-AC', '11', 'Sumatera'), 'Sumatera Utara': ('ID-SU', '12', 'Sumatera'),
    'Sumatera Barat': ('ID-SB', '13', 'Sumatera'), 'Riau': ('ID-RI', '14', 'Sumatera'),
    'Jambi': ('ID-JA', '15', 'Sumatera'), 'Sumatera Selatan': ('ID-SS', '16', 'Sumatera'),
    'Bengkulu': ('ID-BE', '17', 'Sumatera'), 'Lampung': ('ID-LA', '18', 'Sumatera'),
    'Kepulauan Bangka Belitung': ('ID-BB', '19', 'Sumatera'), 'Kepulauan Riau': ('ID-KR', '21', 'Sumatera'),
    'DKI Jakarta': ('ID-JK', '31', 'Jawa'), 'Jawa Barat': ('ID-JB', '32', 'Jawa'),
    'Jawa Tengah': ('ID-JT', '33', 'Jawa'), 'DI Yogyakarta': ('ID-YO', '34', 'Jawa'),
    'Jawa Timur': ('ID-JI', '35', 'Jawa'), 'Banten': ('ID-BT', '36', 'Jawa'),
    'Bali': ('ID-BA', '51', 'Bali & Nusa Tenggara'), 'Nusa Tenggara Barat': ('ID-NB', '52', 'Bali & Nusa Tenggara'),
    'Nusa Tenggara Timur': ('ID-NT', '53', 'Bali & Nusa Tenggara'),
    'Kalimantan Barat': ('ID-KB', '61', 'Kalimantan'), 'Kalimantan Tengah': ('ID-KT', '62', 'Kalimantan'),
    'Kalimantan Selatan': ('ID-KS', '63', 'Kalimantan'), 'Kalimantan Timur': ('ID-KI', '64', 'Kalimantan'),
    'Kalimantan Utara': ('ID-KU', '65', 'Kalimantan'), 'Sulawesi Utara': ('ID-SA', '71', 'Sulawesi'),
    'Sulawesi Tengah': ('ID-ST', '72', 'Sulawesi'), 'Sulawesi Selatan': ('ID-SN', '73', 'Sulawesi'),
    'Sulawesi Tenggara': ('ID-SG', '74', 'Sulawesi'), 'Gorontalo': ('ID-GO', '75', 'Sulawesi'),
    'Sulawesi Barat': ('ID-SR', '76', 'Sulawesi'), 'Maluku': ('ID-MA', '81', 'Maluku'),
    'Maluku Utara': ('ID-MU', '82', 'Maluku'), 'Papua Barat': ('ID-PB', '91', 'Papua'),
    'Papua Barat Daya': ('ID-PD', '92', 'Papua'), 'Papua': ('ID-PA', '94', 'Papua'),
    'Papua Selatan': ('ID-PS', '93', 'Papua'), 'Papua Tengah': ('ID-PT', '96', 'Papua'),
    'Papua Pegunungan': ('ID-PP', '95', 'Papua'),
}

QUADRANT_DEFINITIONS = {
    'I': {'nama': 'Rentan konsumsi', 'karakteristik': 'Pengeluaran di bawah median; porsi makanan di atas median',
          'definisi': 'Pengeluaran relatif rendah dengan porsi konsumsi makanan tinggi.',
          'rekomendasi_strategis': 'Pantau keterjangkauan pangan, perlindungan daya beli, dan stabilisasi harga komoditas pokok.',
          'sektor_prioritas': ['Keterjangkauan pangan', 'Perlindungan daya beli', 'Stabilisasi harga']},
    'II': {'nama': 'Tekanan pangan tinggi', 'karakteristik': 'Pengeluaran minimal median; porsi makanan di atas median',
           'definisi': 'Pengeluaran total relatif tinggi tetapi porsi makanan juga tinggi; perlu ditelusuri bersama faktor harga dan struktur wilayah.',
           'rekomendasi_strategis': 'Telusuri harga, distribusi, dan akses pangan sebelum menetapkan intervensi logistik.',
           'sektor_prioritas': ['Harga dan pasokan pangan', 'Distribusi', 'Daya beli']},
    'III': {'nama': 'Transisi konsumsi', 'karakteristik': 'Pengeluaran di bawah median; porsi makanan maksimal median',
            'definisi': 'Pengeluaran total relatif rendah dengan porsi makanan relatif lebih kecil.',
            'rekomendasi_strategis': 'Pantau perkembangan pengeluaran dan akses terhadap kebutuhan non-makanan dasar.',
            'sektor_prioritas': ['Peluang pendapatan', 'Layanan dasar', 'Pemantauan konsumsi']},
    'IV': {'nama': 'Konsumsi non-pangan besar', 'karakteristik': 'Pengeluaran minimal median; porsi makanan maksimal median',
           'definisi': 'Pengeluaran total relatif tinggi dan porsi non-makanan lebih besar.',
           'rekomendasi_strategis': 'Pantau keterjangkauan kebutuhan non-makanan dan perubahan biaya hidup.',
           'sektor_prioritas': ['Biaya hidup', 'Hunian dan transportasi', 'Layanan publik']},
}


def _find_csv(data_dir: str, year: int, kind: str) -> str:
    candidates = glob.glob(os.path.join(data_dir, '*.csv'))
    if kind == 'share':
        match = [p for p in candidates if 'Persentase Pengeluaran' in os.path.basename(p) and str(year) in os.path.basename(p)]
    else:
        match = [p for p in candidates if 'Rata-rata Pengeluaran' in os.path.basename(p) and str(year) in os.path.basename(p)]
    if not match:
        raise FileNotFoundError(f'CSV {kind} untuk tahun {year} tidak ditemukan di {data_dir}')
    return match[0]


def _read_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding='utf-8-sig')
    df.columns = [str(c).strip() for c in df.columns]
    df['Provinsi'] = df['Provinsi'].astype(str).str.strip()
    return df


def _column(df: pd.DataFrame, suffix: str) -> str:
    matches = [c for c in df.columns if c.endswith(suffix)]
    if not matches:
        raise ValueError(f'Kolom berakhiran {suffix!r} tidak ditemukan: {list(df.columns)}')
    return matches[0]


class SusenasDataLoader:
    def __init__(self, data_dir: str = None, geojson_path: str = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = data_dir or os.path.join(base_dir, 'data')
        self.geojson_path = geojson_path or os.path.join(self.data_dir, 'indonesia_38_provinces.geojson')
        self.provinces_data: List[Dict[str, Any]] = []
        self.provinces_dict: Dict[str, Dict[str, Any]] = {}
        self.quadrants_summary: List[Dict[str, Any]] = []
        self.geojson_enriched: Dict[str, Any] = {}
        self.summary_metrics: Dict[str, Any] = {}
        self.national_row: Dict[str, Any] = {}
        self.load_and_process()

    def load_and_process(self):
        current_path = _find_csv(self.data_dir, 2025, 'total')
        previous_path = _find_csv(self.data_dir, 2024, 'total')
        share_path = _find_csv(self.data_dir, 2025, 'share')
        cur, prev, share = map(_read_csv, (current_path, previous_path, share_path))
        food_col, nonfood_col, total_col = (_column(cur, s) for s in ('- Makanan', '- Bukan Makanan', '- Jumlah'))
        old_food_col, old_nonfood_col, old_total_col = (_column(prev, s) for s in ('- Makanan', '- Bukan Makanan', '- Jumlah'))
        food_share_col, nonfood_share_col = (_column(share, s) for s in ('- Makanan', '- Bukan Makanan'))
        cur = cur.rename(columns={food_col: 'food', nonfood_col: 'nonfood', total_col: 'total'})
        prev = prev.rename(columns={old_food_col: 'food_2024', old_nonfood_col: 'nonfood_2024', old_total_col: 'total_2024'})
        share = share.rename(columns={food_share_col: 'food_share', nonfood_share_col: 'nonfood_share'})
        merged = cur.merge(prev[['Provinsi', 'food_2024', 'nonfood_2024', 'total_2024']], on='Provinsi', validate='one_to_one')
        merged = merged.merge(share[['Provinsi', 'food_share', 'nonfood_share']], on='Provinsi', validate='one_to_one')
        for col in ['food', 'nonfood', 'total', 'food_2024', 'nonfood_2024', 'total_2024', 'food_share', 'nonfood_share']:
            merged[col] = pd.to_numeric(merged[col], errors='raise')
        merged = merged[merged['Provinsi'] != 'Indonesia'].copy()
        if len(merged) != 38:
            raise ValueError(f'Diharapkan 38 provinsi dari CSV, ditemukan {len(merged)}')
        merged['food_share_calc'] = merged.food / merged.total * 100
        med_total = float(merged.total.median())
        med_food_share = float(merged.food_share.median())
        x = merged.total.to_numpy(dtype=float) / 1_000_000
        y = merged.food_share.to_numpy(dtype=float)
        slope, intercept = np.polyfit(x, y, 1)
        corr = float(np.corrcoef(x, y)[0, 1])
        records = []
        for _, row in merged.iterrows():
            name = row.Provinsi
            meta = PROV_METADATA.get(name, (f'ID-{name[:2].upper()}', '00', 'Lainnya'))
            if row.total < med_total and row.food_share > med_food_share: q = 'I'
            elif row.total >= med_total and row.food_share > med_food_share: q = 'II'
            elif row.total < med_total: q = 'III'
            else: q = 'IV'
            pred = float(slope * row.total / 1_000_000 + intercept)
            item = {
                'provinsi_id': meta[0], 'kode_bps': meta[1], 'pulau': meta[2],
                'geo_name': 'Daerah Istimewa Yogyakarta' if name == 'DI Yogyakarta' else name, 'provinsi': name,
                'pengeluaran_makanan': int(row.food), 'pengeluaran_non_makanan': int(row.nonfood), 'pengeluaran_total': int(row.total),
                'persen_makanan': round(float(row.food_share), 2), 'persen_non_makanan': round(float(row.nonfood_share), 2),
                'kuadran': q, 'kategori_wilayah': QUADRANT_DEFINITIONS[q]['nama'],
                'rekomendasi_utama': QUADRANT_DEFINITIONS[q]['rekomendasi_strategis'],
                'rank_total': int(merged.total.rank(ascending=False, method='min').loc[row.name]),
                'rank_persen_makanan': int(merged.food_share.rank(ascending=False, method='min').loc[row.name]),
                'deviasi_median_total_rp': int(row.total - med_total),
                'deviasi_median_total_persen': round((row.total / med_total - 1) * 100, 2),
                'deviasi_median_makanan_persen': round(float(row.food_share - med_food_share), 2),
                'engel_predicted_persen_makanan': round(pred, 2), 'engel_residual': round(float(row.food_share - pred), 2),
                'sektor_prioritas': QUADRANT_DEFINITIONS[q]['sektor_prioritas'],
                'pengeluaran_makanan_2024': int(row.food_2024), 'pengeluaran_non_makanan_2024': int(row.nonfood_2024),
                'pengeluaran_total_2024': int(row.total_2024),
                'pertumbuhan_total_persen': round((row.total / row.total_2024 - 1) * 100, 2),
                'pertumbuhan_makanan_persen': round((row.food / row.food_2024 - 1) * 100, 2),
                'pertumbuhan_non_makanan_persen': round((row.nonfood / row.nonfood_2024 - 1) * 100, 2),
                'perubahan_porsi_makanan_pp': round(float(row.food_share - row.food_2024 / row.total_2024 * 100), 2),
            }
            item['rekomendasi_kebijakan'] = [item['rekomendasi_utama'], f"Pantau perubahan porsi makanan ({item['perubahan_porsi_makanan_pp']:+.2f} poin persentase) dan pengeluaran nominal."]
            records.append(item)
        self.provinces_data = records
        self.provinces_dict = {v: r for r in records for v in (r['provinsi_id'], r['provinsi'], r['geo_name'])}
        top, low = max(records, key=lambda r:r['pengeluaran_total']), min(records, key=lambda r:r['pengeluaran_total'])
        top_food, low_food = max(records, key=lambda r:r['persen_makanan']), min(records, key=lambda r:r['persen_makanan'])
        nation_cur = cur.loc[cur.Provinsi == 'Indonesia'].iloc[0]
        nation_prev = prev.loc[prev.Provinsi == 'Indonesia'].iloc[0]
        self.national_row = {'provinsi':'Indonesia', 'pengeluaran_makanan':int(nation_cur.food), 'pengeluaran_non_makanan':int(nation_cur.nonfood),
            'pengeluaran_total':int(nation_cur.total), 'persen_makanan':round(float(nation_cur.food_share if 'food_share' in nation_cur else nation_cur.food/nation_cur.total*100),2)}
        # National current share comes from the percentage CSV, keeping the published percentage as source of truth.
        nat_share = share.loc[share.Provinsi == 'Indonesia'].iloc[0]
        self.national_row.update({'persen_makanan':round(float(nat_share.food_share),2),'persen_non_makanan':round(float(nat_share.nonfood_share),2)})
        national_2024 = {'provinsi':'Indonesia', 'pengeluaran_makanan':int(nation_prev.food_2024),
            'pengeluaran_non_makanan':int(nation_prev.nonfood_2024), 'pengeluaran_total':int(nation_prev.total_2024),
            'persen_makanan':round(float(nation_prev.food_2024/nation_prev.total_2024*100),2),
            'persen_non_makanan':round(float(nation_prev.nonfood_2024/nation_prev.total_2024*100),2)}
        self.summary_metrics = {
            'total_provinsi':len(records), 'median_pengeluaran_total':int(med_total),'median_proporsi_pangan':round(med_food_share,2),
            'rata_rata_pengeluaran_total':int(merged.total.mean()), 'rata_rata_proporsi_pangan':round(float(merged.food_share.mean()),2),
            'provinsi_tertinggi_total':{'provinsi_id':top['provinsi_id'],'provinsi':top['provinsi'],'nilai':top['pengeluaran_total'],'persen_makanan':top['persen_makanan']},
            'provinsi_terendah_total':{'provinsi_id':low['provinsi_id'],'provinsi':low['provinsi'],'nilai':low['pengeluaran_total'],'persen_makanan':low['persen_makanan']},
            'provinsi_tertinggi_pangan':{'provinsi_id':top_food['provinsi_id'],'provinsi':top_food['provinsi'],'nilai':top_food['persen_makanan'],'pengeluaran_total':top_food['pengeluaran_total']},
            'provinsi_terendah_pangan':{'provinsi_id':low_food['provinsi_id'],'provinsi':low_food['provinsi'],'nilai':low_food['persen_makanan'],'pengeluaran_total':low_food['pengeluaran_total']},
            'disparitas_rasio':round(top['pengeluaran_total']/low['pengeluaran_total'],2),'disparitas_selisih_rp':top['pengeluaran_total']-low['pengeluaran_total'],
            'korelasi_engel_r':round(corr,3),'korelasi_engel_r2':round(corr*corr,4),'regresi_slope':round(float(slope),4),'regresi_intercept':round(float(intercept),4),
            'nasional_susenas':self.national_row, 'nasional_2024':national_2024,
            'perubahan_nasional_total_persen':round((nation_cur.total/nation_prev.total_2024-1)*100,2),
            'perubahan_nasional_pangan_persen':round((nation_cur.food/nation_prev.food_2024-1)*100,2),
            'perubahan_nasional_non_pangan_persen':round((nation_cur.nonfood/nation_prev.nonfood_2024-1)*100,2),
            'perubahan_nasional_porsi_pangan_pp':round(float(nat_share.food_share - nation_prev.food_2024/nation_prev.total_2024*100),2),
            'periode':'2024–2025', 'sumber_data':'CSV Susenas/BPS yang disediakan pengguna',
        }
        self.quadrants_summary = []
        for q, definition in QUADRANT_DEFINITIONS.items():
            group = [r for r in records if r['kuadran'] == q]
            self.quadrants_summary.append({'kuadran':q, **definition, 'jumlah_provinsi':len(group),
                'persentase_provinsi':round(len(group)/len(records)*100,2),'daftar_provinsi':[r['provinsi'] for r in group],
                'provinsi_items':group,'rata_rata_total':int(np.mean([r['pengeluaran_total'] for r in group])) if group else 0,
                'rata_rata_persen_makanan':round(float(np.mean([r['persen_makanan'] for r in group])),2) if group else 0})
        if os.path.exists(self.geojson_path):
            with open(self.geojson_path, encoding='utf-8') as f: gj = json.load(f)
            gj['features'] = [{**feature, 'properties':{**feature.get('properties',{}), **self.provinces_dict.get(feature.get('properties',{}).get('PROVINSI',''),{})}} for feature in gj.get('features',[])]
            self.geojson_enriched = gj

    def simulate_policy(self, provinsi_id=None, potongan_pangan_persen=0.0, stimulus_pendapatan_persen=0.0):
        selected = [self.provinces_dict[provinsi_id]] if provinsi_id in self.provinces_dict else self.provinces_data
        results=[]
        for p in selected:
            food=p['pengeluaran_makanan']*(1-potongan_pangan_persen/100)
            total=(food+p['pengeluaran_non_makanan'])*(1+stimulus_pendapatan_persen/100)
            share=food/(food+p['pengeluaran_non_makanan'])*100
            med=self.summary_metrics['median_pengeluaran_total']; med_share=self.summary_metrics['median_proporsi_pangan']
            q='I' if total<med and share>med_share else 'II' if total>=med and share>med_share else 'III' if total<med else 'IV'
            results.append({'provinsi_id':p['provinsi_id'],'provinsi':p['provinsi'],'kuadran_lama':p['kuadran'],'kuadran_baru':q,
                'kategori_lama':p['kategori_wilayah'],'kategori_baru':QUADRANT_DEFINITIONS[q]['nama'],'pengeluaran_total_lama':p['pengeluaran_total'],
                'pengeluaran_total_baru':round(total),'persen_makanan_lama':p['persen_makanan'],'persen_makanan_baru':round(share,2),
                'perubahan_status':'Berpindah kuadran' if q!=p['kuadran'] else 'Tidak berpindah kuadran',
                'dampak_kebijakan':'Simulasi aritmetis berbasis asumsi perubahan; bukan estimasi dampak kausal.'})
        return results


data_engine = SusenasDataLoader()
