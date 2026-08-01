export interface SlabTakvimDTO {
  slab_id: number;
  sira_no: number;
  kalite_sinifi: string;
  durum: 'depoda' | 'sarj_oluyor' | 'haddelemede' | 'tamamlandi';
}