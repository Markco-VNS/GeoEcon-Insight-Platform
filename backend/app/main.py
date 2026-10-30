import os
import sys

# Ensure parent and root dirs are in sys.path so imports work regardless of launch directory
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
_root_dir = os.path.dirname(_parent_dir)

for _p in [_parent_dir, _current_dir, _root_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any

try:
    from app.data_loader import data_engine, QUADRANT_DEFINITIONS
    from app.models import (
        ProvinceData,
        SummaryMetrics,
        QuadrantSummary,
        SimulationRequest,
        SimulationResponse
    )
except ImportError:
    from data_loader import data_engine, QUADRANT_DEFINITIONS
    from models import (
        ProvinceData,
        SummaryMetrics,
        QuadrantSummary,
        SimulationRequest,
        SimulationResponse
    )

app = FastAPI(
    title="GeoEcon Insight API",
    description="Analisis pengeluaran konsumsi antarprovinsi dari CSV Susenas/BPS 2024–2025",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for local Vite dev server and external clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    print(f"[GeoEcon Insight] Loaded {len(data_engine.provinces_data)} provinces from CSV datasets.")

@app.get("/api/health")
def get_health():
    return {
        "status": "healthy",
        "service": "GeoEcon Insight Backend API",
        "version": "2.0.0",
        "provinces_loaded": len(data_engine.provinces_data),
        "data_source": "CSV Susenas/BPS 2024–2025 (pengeluaran dan komposisi konsumsi)"
    }

@app.get("/api/summary", response_model=SummaryMetrics)
def get_summary():
    """Mengembalikan ringkasan yang dihitung dari tiga CSV Susenas."""
    return data_engine.summary_metrics

@app.get("/api/provinces", response_model=List[ProvinceData])
def get_provinces(
    kuadran: Optional[str] = Query(None, description="Filter kuadran: I, II, III, IV"),
    pulau: Optional[str] = Query(None, description="Filter pulau/region"),
    sort_by: Optional[str] = Query("pengeluaran_total", description="Sort by field"),
    order: Optional[str] = Query("desc", description="Sort order: asc or desc")
):
    """
    Mengembalikan data 38 provinsi di Indonesia dengan indikator ekonomi,
    klasifikasi kuadran kebijakan, dan rekomendasi utama.
    """
    results = list(data_engine.provinces_data)
    
    if kuadran:
        results = [p for p in results if p["kuadran"] == kuadran.upper()]
    if pulau:
        results = [p for p in results if p.get("pulau", "").lower() == pulau.lower()]
        
    reverse = (order.lower() == "desc")
    if sort_by in ["pengeluaran_total", "pengeluaran_makanan", "pengeluaran_non_makanan", "persen_makanan", "persen_non_makanan", "pertumbuhan_total_persen", "pertumbuhan_makanan_persen", "pertumbuhan_non_makanan_persen"]:
        results.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
    elif sort_by == "provinsi":
        results.sort(key=lambda x: x.get("provinsi", ""), reverse=reverse)
        
    return results

@app.get("/api/provinces/{provinsi_id}", response_model=ProvinceData)
def get_province_detail(provinsi_id: str):
    """
    Mengambil detail analitis lengkap untuk satu provinsi berdasarkan ID (contoh: ID-PP, ID-JK)
    atau nama provinsi (contoh: Papua Pegunungan, DKI Jakarta).
    """
    target = data_engine.provinces_dict.get(provinsi_id)
    if not target:
        # Search case-insensitive
        for k, v in data_engine.provinces_dict.items():
            if k.lower() == provinsi_id.lower() or v.get("provinsi", "").lower() == provinsi_id.lower():
                target = v
                break
                
    if not target:
        raise HTTPException(status_code=404, detail=f"Provinsi dengan ID/Nama '{provinsi_id}' tidak ditemukan.")
    return target

@app.get("/api/quadrants", response_model=List[QuadrantSummary])
def get_quadrants():
    """
    Mengembalikan rincian 4 kuadran kebijakan ekonomi:
    - Kuadran I: Rawan Rentan
    - Kuadran II: Anomali Logistik 3TP
    - Kuadran III: Transisi Berkembang
    - Kuadran IV: Mature Urban
    """
    return data_engine.quadrants_summary

@app.get("/api/geojson")
def get_geojson(indicator: Optional[str] = "pengeluaran_total"):
    """
    Mengembalikan GeoJSON 38 provinsi Indonesia yang telah di-enrich dengan
    data pengeluaran, proporsi makanan, klasifikasi kuadran, dan deviasi median.
    Cocok langsung untuk visualisasi Choropleth Leaflet.
    """
    if not data_engine.geojson_enriched:
        raise HTTPException(status_code=500, detail="Data GeoJSON belum tersedia.")
    return data_engine.geojson_enriched

@app.post("/api/simulate", response_model=List[SimulationResponse])
def simulate_policy_impact(payload: SimulationRequest):
    """
    Simulasi Dampak Intervensi Kebijakan:
    - potongan_pangan_persen: efisiensi harga pangan/logistik kargo udara (contoh Tol Udara)
    - stimulus_pendapatan_persen: stimulus daya beli masyarakat & upah riil
    Menghitung ulang posisi kuadran dan rasio konsumsi.
    """
    return data_engine.simulate_policy(
        provinsi_id=payload.provinsi_id,
        potongan_pangan_persen=payload.potongan_pangan_persen,
        stimulus_pendapatan_persen=payload.stimulus_pendapatan_persen
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, app_dir=_parent_dir)
