from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ProvinceData(BaseModel):
    provinsi_id: str
    provinsi: str
    kode_bps: Optional[str] = None
    pulau: Optional[str] = None
    geo_name: Optional[str] = None
    pengeluaran_makanan: int
    pengeluaran_non_makanan: int
    pengeluaran_total: int
    persen_makanan: float
    persen_non_makanan: float
    kuadran: str
    kategori_wilayah: str
    rekomendasi_utama: str
    # Enriched analytical fields
    rank_total: Optional[int] = None
    rank_persen_makanan: Optional[int] = None
    deviasi_median_total_rp: Optional[int] = None
    deviasi_median_total_persen: Optional[float] = None
    deviasi_median_makanan_persen: Optional[float] = None
    engel_predicted_persen_makanan: Optional[float] = None
    engel_residual: Optional[float] = None
    sektor_prioritas: Optional[List[str]] = None
    rekomendasi_kebijakan: Optional[List[str]] = None
    pengeluaran_makanan_2024: Optional[int] = None
    pengeluaran_non_makanan_2024: Optional[int] = None
    pengeluaran_total_2024: Optional[int] = None
    pertumbuhan_total_persen: Optional[float] = None
    pertumbuhan_makanan_persen: Optional[float] = None
    pertumbuhan_non_makanan_persen: Optional[float] = None
    perubahan_porsi_makanan_pp: Optional[float] = None

class SummaryMetrics(BaseModel):
    total_provinsi: int
    median_pengeluaran_total: int
    median_proporsi_pangan: float
    rata_rata_pengeluaran_total: int
    rata_rata_proporsi_pangan: float
    provinsi_tertinggi_total: Dict[str, Any]
    provinsi_terendah_total: Dict[str, Any]
    provinsi_tertinggi_pangan: Dict[str, Any]
    provinsi_terendah_pangan: Dict[str, Any]
    disparitas_rasio: float
    disparitas_selisih_rp: int
    korelasi_engel_r: float
    korelasi_engel_r2: float
    regresi_slope: float
    regresi_intercept: float
    nasional_susenas: Dict[str, Any]
    perubahan_nasional_total_persen: Optional[float] = None
    perubahan_nasional_pangan_persen: Optional[float] = None
    perubahan_nasional_non_pangan_persen: Optional[float] = None
    perubahan_nasional_porsi_pangan_pp: Optional[float] = None
    nasional_2024: Optional[Dict[str, Any]] = None
    periode: Optional[str] = None
    sumber_data: Optional[str] = None

class QuadrantSummary(BaseModel):
    kuadran: str
    nama: str
    karakteristik: str
    definisi: str
    rekomendasi_strategis: str
    jumlah_provinsi: int
    persentase_provinsi: float
    daftar_provinsi: List[str]
    rata_rata_total: int
    rata_rata_persen_makanan: float

class SimulationRequest(BaseModel):
    provinsi_id: Optional[str] = None  # None means all or selected
    potongan_pangan_persen: float = Field(default=0.0, ge=-50.0, le=50.0)
    stimulus_pendapatan_persen: float = Field(default=0.0, ge=-50.0, le=50.0)

class SimulationResponse(BaseModel):
    provinsi_id: str
    provinsi: str
    kuadran_lama: str
    kuadran_baru: str
    kategori_lama: str
    kategori_baru: str
    pengeluaran_total_lama: int
    pengeluaran_total_baru: int
    persen_makanan_lama: float
    persen_makanan_baru: float
    perubahan_status: str
    dampak_kebijakan: str
