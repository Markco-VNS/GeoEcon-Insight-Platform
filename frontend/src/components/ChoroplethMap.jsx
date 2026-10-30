import { useEffect, useMemo, useRef, useState } from 'react';
import { GeoJSON, MapContainer, TileLayer, useMap } from 'react-leaflet';
import { MapPinned, RotateCcw, Search } from 'lucide-react';
import { formatRupiah, formatPercent } from '../utils/formatters';

const VIEWS = [
  { id: 'all', label: 'Indonesia', center: [-2.4, 118], zoom: 4.3 },
  { id: 'Sumatera', label: 'Sumatera', center: [-0.2, 101], zoom: 5.2 },
  { id: 'Jawa', label: 'Jawa', center: [-7.1, 110], zoom: 6 },
  { id: 'Kalimantan', label: 'Kalimantan', center: [0.1, 114], zoom: 5.2 },
  { id: 'Sulawesi', label: 'Sulawesi', center: [-2, 121], zoom: 5.2 },
  { id: 'Papua', label: 'Papua', center: [-4.3, 137], zoom: 5.2 },
];
const QUADRANTS = { I: '#f0785b', II: '#f1b85b', III: '#59b6ae', IV: '#76bd8b' };
function FlyTo({ view }) { const map = useMap(); useEffect(() => { if (view) map.flyTo(view.center, view.zoom, { duration: 1.1 }); }, [map, view]); return null; }

export default function ChoroplethMap({ geojsonData, provinces = [], selectedProvince, onSelectProvince }) {
  const [indicator, setIndicator] = useState('pengeluaran_total');
  const [view, setView] = useState(VIEWS[0]);
  const geoRef = useRef(null);
  const selected = selectedProvince?.provinsi_id;
  const minMax = useMemo(() => {
    const field = indicator === 'pengeluaran_total' ? 'pengeluaran_total' : indicator === 'persen_makanan' ? 'persen_makanan' : 'pertumbuhan_total_persen';
    const values = provinces.map(p => Number(p[field])).filter(Number.isFinite);
    return [Math.min(...values), Math.max(...values)];
  }, [indicator, provinces]);
  const color = (p) => {
    if (indicator === 'kuadran') return QUADRANTS[p.kuadran] || '#80959b';
    const value = Number(p[indicator === 'pengeluaran_total' ? 'pengeluaran_total' : indicator === 'persen_makanan' ? 'persen_makanan' : 'pertumbuhan_total_persen']);
    const t = Math.max(0, Math.min(1, (value - minMax[0]) / Math.max(1, minMax[1] - minMax[0])));
    const palette = indicator === 'persen_makanan'
      ? ['#fff0b5', '#f6d58a', '#efad68', '#e7895a', '#d96752']
      : ['#dcebd4', '#a8d6b9', '#74bda2', '#439d89', '#20766f'];
    return palette[Math.min(palette.length - 1, Math.floor(t * palette.length))];
  };
  const onEachFeature = (feature, layer) => {
    const p = feature.properties || {};
    const record = provinces.find(row => row.provinsi === p.provinsi || row.geo_name === p.PROVINSI);
    if (!record) return;
    layer.bindTooltip(`<b>${record.provinsi}</b><br/>Total ${formatRupiah(record.pengeluaran_total)}<br/>Porsi makanan ${formatPercent(record.persen_makanan)}<br/>Perubahan tahunan ${record.pertumbuhan_total_persen > 0 ? '+' : ''}${record.pertumbuhan_total_persen}%`, { sticky: true, className: 'atlas-tooltip' });
    layer.on({ click: () => onSelectProvince(record.provinsi_id), mouseover: e => e.target.setStyle({ weight: 2, color: '#eff5ed', fillOpacity: .98 }), mouseout: e => geoRef.current?.resetStyle(e.target) });
  };
  const style = feature => {
    const record = provinces.find(row => row.provinsi === feature.properties?.provinsi || row.geo_name === feature.properties?.PROVINSI);
    return { fillColor: record ? color(record) : '#42555a', fillOpacity: record?.provinsi_id === selected ? .98 : .82,
      color: record?.provinsi_id === selected ? '#f9d66b' : '#d8e6dc', weight: record?.provinsi_id === selected ? 2.4 : .8, opacity: .9 };
  };
  const rankField = indicator === 'kuadran' ? 'pengeluaran_total' : indicator;
  const mapRows = [...provinces].sort((a,b) => b[rankField] - a[rankField]).slice(0, 5);
  return <section className="atlas-card" id="map">
    <div className="atlas-heading"><div><span className="eyebrow">02 / INTELIJEN SPASIAL</span><h2>Peta pola konsumsi</h2><p>Jelajahi perbedaan pengeluaran, porsi pangan, dan perubahan nominal antarprovinsi.</p></div><span className="live-chip"><i /> 38 provinsi</span></div>
    <div className="map-toolbar">
      <div className="region-pills">{VIEWS.map(v => <button key={v.id} onClick={() => setView(v)} className={view.id === v.id ? 'active' : ''}>{v.label}</button>)}</div>
      <label className="map-select"><MapPinned size={16}/><select value={indicator} onChange={e => setIndicator(e.target.value)}><option value="pengeluaran_total">Pengeluaran total 2025</option><option value="persen_makanan">Porsi pengeluaran makanan</option><option value="pertumbuhan_total_persen">Perubahan total 2024–25</option><option value="kuadran">Kelompok konsumsi</option></select></label>
    </div>
    <div className="map-layout">
      <div className="map-canvas">
        {geojsonData && <MapContainer center={view.center} zoom={view.zoom} scrollWheelZoom={false} zoomControl className="thematic-map"><FlyTo view={view}/><TileLayer attribution='Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ' url="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}" maxZoom={16}/><GeoJSON key={indicator} data={geojsonData} ref={geoRef} style={style} onEachFeature={onEachFeature}/></MapContainer>}
        <div className="map-overlay-title"><span>INDONESIA</span><small>Susenas • 2025</small></div>
        <div className="map-legend"><span>Rendah</span><i/><i/><i/><i/><span>Tinggi</span></div>
        <button className="map-reset" title="Kembali ke seluruh Indonesia" onClick={() => setView(VIEWS[0])}><RotateCcw size={16}/></button>
      </div>
      <aside className="map-insights"><div className="map-insights-label"><span>URUTAN TERTINGGI</span><Search size={15}/></div><div className="map-insights-title">Lima provinsi teratas</div>
        {mapRows.map((p,i) => <button className={`map-rank ${p.provinsi_id === selected ? 'chosen' : ''}`} key={p.provinsi_id} onClick={() => onSelectProvince(p.provinsi_id)}><b>{String(i+1).padStart(2,'0')}</b><span>{p.provinsi}<small>{formatRupiah(p.pengeluaran_total)} / kapita / bulan</small></span><i style={{background: p.kuadran ? QUADRANTS[p.kuadran] : '#6cbaa9'}}/></button>)}
        <div className="map-selected">{selectedProvince ? <><span>PROVINSI DIPILIH</span><strong>{selectedProvince.provinsi}</strong><p>{selectedProvince.kategori_wilayah} · Q{selectedProvince.kuadran}</p></> : <p>Pilih provinsi di peta atau daftar untuk melihat pola konsumsi.</p>}</div>
        <small className="map-note">Peta menggunakan poligon administratif provinsi. Nilai indikator diturunkan dari CSV yang disediakan.</small>
      </aside>
    </div>
  </section>;
}
