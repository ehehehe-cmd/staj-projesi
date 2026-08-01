import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, interval } from 'rxjs';
import { switchMap, startWith } from 'rxjs/operators';
import { SlabTakvimDTO } from '../models/slab-takvim.model';

@Injectable({ providedIn: 'root' })
export class TakvimlemeService {
  private readonly apiUrl = 'http://localhost:8000/api/takvimleme/aktif';
  private readonly pollIntervalMs = 5000; // 5 saniyede bir çek

  constructor(private http: HttpClient) {}

  getAktifTakvimleme(): Observable<SlabTakvimDTO[]> {
    return this.http.get<SlabTakvimDTO[]>(this.apiUrl);
  }

  pollAktifTakvimleme(): Observable<SlabTakvimDTO[]> {
    return interval(this.pollIntervalMs).pipe(
      startWith(0),
      switchMap(() => this.getAktifTakvimleme())
    );
  }
}