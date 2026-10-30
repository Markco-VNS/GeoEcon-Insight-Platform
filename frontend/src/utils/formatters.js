export const formatRupiah = (value) => {
  if (value === null || value === undefined || isNaN(value)) return 'Rp 0';
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0
  }).format(value);
};

export const formatRupiahShort = (value) => {
  if (value === null || value === undefined || isNaN(value)) return 'Rp 0';
  const val = Number(value);
  if (val >= 1_000_000) return `Rp ${(val / 1_000_000).toFixed(2)} jt`;
  if (val >= 1_000) return `Rp ${(val / 1_000).toFixed(0)} rb`;
  return `Rp ${val}`;
};

export const formatPercent = (value, decimals = 2) => {
  if (value === null || value === undefined || isNaN(value)) return '0%';
  return `${Number(value).toFixed(decimals)}%`;
};

const Q_META = {
  I: {
    label: 'Kuadran I',
    title: 'Rentan konsumsi',
    color: '#CE6C54',
    softBg: '#FAECE5',
    border: '#FFE4E6',
    bg: 'bg-rose-50 text-rose-700 border border-rose-200/60',
    badge: 'bg-rose-100/80 text-rose-800'
  },
  II: {
    label: 'Kuadran II',
    title: 'Tekanan pangan tinggi',
    color: '#C8973D',
    softBg: '#F8F0DE',
    border: '#FDE68A',
    bg: 'bg-amber-50 text-amber-800 border border-amber-200/60',
    badge: 'bg-amber-100/80 text-amber-800'
  },
  III: {
    label: 'Kuadran III',
    title: 'Transisi konsumsi',
    color: '#4F9A91',
    softBg: '#E8F3EF',
    border: '#CCFBF1',
    bg: 'bg-teal-50 text-teal-800 border border-teal-200/60',
    badge: 'bg-teal-100/80 text-teal-800'
  },
  IV: {
    label: 'Kuadran IV',
    title: 'Konsumsi non-pangan besar',
    color: '#6F9A70',
    softBg: '#EAF1E5',
    border: '#A7F3D0',
    bg: 'bg-emerald-50 text-emerald-800 border border-emerald-200/60',
    badge: 'bg-emerald-100/80 text-emerald-800'
  },
};

export const getQuadrantMeta = (kuadran) => {
  return Q_META[kuadran] || {
    label: 'Tidak Diketahui',
    title: 'Tidak Terdefinisi',
    color: '#64748B',
    softBg: '#F8FAFC',
    border: '#E2E8F0',
    bg: 'bg-slate-50 text-slate-700 border border-slate-200',
    badge: 'bg-slate-100 text-slate-700'
  };
};
