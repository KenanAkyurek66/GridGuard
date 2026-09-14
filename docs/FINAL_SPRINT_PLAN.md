# GridGuard — Final Sprint Planı

Hedef bitiş: 18 Eylül 2026 Cuma akşamı  
Yarışma son tarihi: 20 Eylül 2026

## Kapsam kilidi

Bu noktadan sonra ürün kapsamı şu başlıklarla sınırlandırılmıştır:

1. Virtual Edge Lab
2. Frontend görsel iyileştirme
3. Digital Panel Twin polish
4. Panel Detail final tasarımı
5. Panels / Alarms görsel bütünlüğü
6. Türkçe / İngilizce dil desteği
7. Final dokümantasyon güncellemeleri
8. Regression testleri ve sabit demo akışı
9. Türkçe jüri sunumu ve soru-cevap hazırlığı

Son tarihe kadar yeni AI modeli, yeni risk motoru, fiziksel donanım üretimi, 3D motor, kullanıcı sistemi, cloud geçişi veya alakasız yeni özellik eklenmeyecektir.

---

## 14 Eylül Pazartesi akşamı

Amaç: Edge Lab tasarım temelini oluşturmak.

- `EdgeLab.jsx` oluştur
- `EdgeLab.css` oluştur
- Görsel dili sabitle:
  - endüstriyel HMI
  - elektrik blueprint / teknik grid
  - GridGuard cyan kimliği
  - kontrollü glow ve telemetry pulse
  - Normal / Warning / High / Critical görsel hiyerarşisi
- Beş jüri senaryosunu sabitle:
  - Normal
  - Aşırı Isınma
  - Ark Olayı
  - Bozuk Sensör
  - Recovery
- Bu akşam backend'e dokunma.

Çıktı:
Yerel senaryo önizlemesi olan tam bir görsel Edge Lab bileşeni.

---

## 15 Eylül Salı

Amaç: Edge Lab'i gerçek sisteme bağlamak.

- Edge Lab'i ana navigasyona ekle.
- Gerçek `/telemetry` endpoint'ine bağla.
- Yerel önizlemeyi gerçek backend cevabıyla değiştir.
- Deterministic risk sonucunu göster.
- AI advisory sonucunu göster.
- Data-quality sonucunu göster.
- Alarm durumunu göster.
- Normal / overheating / arc / bad sensor / recovery akışlarını doğrula.
- Sağlanan teknik belgelere göre kompakt Modbus mapping görünümü ekle.
- Pano ve sensör metinlerini verilen teknik belgelerle doğrula.

Çıktı:
Gerçek GridGuard backend'ini kullanan çalışan yazılım tabanlı saha/edge emülatörü.

---

## 16 Eylül Çarşamba

Amaç: ürünün genel görsel kalitesini yükseltmek.

- Edge Lab animasyon ve yerleşim polish.
- Overview ilk izlenimini güçlendir.
- Panel View / Digital Twin'i Edge Lab ile görsel olarak uyumlu hale getir.
- Panel Detail'i temiz ve analitik tut.
- Panels ve Alarms ekranlarını aynı tasarım ailesine getir.
- Durum geçişlerini net göster:
  - Normal
  - AI early warning
  - Warning
  - High
  - Critical
  - Recovery

Çıktı:
Ayrı dashboard ekranları yerine tek bir ürün hissi veren GridGuard.

---

## 17 Eylül Perşembe

Amaç: iki dilli final uygulama.

- TR / EN dil sistemi ekle.
- Sunum varsayılan dili: Türkçe.
- Şunları çevir:
  - navigasyon
  - Overview
  - Edge Lab
  - Digital Twin
  - Panel Detail
  - Alarms
  - Panels
  - sistem durumları ve açıklamalar
- Backend ve API enum'larını değiştirme.
- Uygun teknik isimleri koru:
  - GridGuard
  - EDGE-01
  - MQTT
  - Modbus
  - Digital Twin

Çıktı:
Tam Türkçe / İngilizce frontend.

---

## 18 Eylül Cuma

Amaç: ürünü dondurmak.

- Frontend build
- Uygunsa lint
- Core risk-engine testleri
- `/health`
- telemetry ingestion
- duplicate / out-of-order / timestamp conflict
- GOOD / DEGRADED / BAD quality policy
- alarm OPEN / RESOLVED lifecycle
- AI status ve prediction
- Digital Twin
- Edge Lab
- TR / EN
- Final dokümantasyon:
  - README
  - Architecture
  - Hardware Concept
  - Demo Guide
- Temiz Git durumu

Bu noktadan sonra yeni özellik yok.

---

## 19 Eylül Cumartesi

Amaç: yalnızca sunum ve prova.

Sabit jüri demo hikâyesi:

1. GridGuard problemi ve tek cümlelik çözüm
2. Overview — 100 sağlıklı panel
3. Edge Lab — saha verisi GridGuard'a nasıl giriyor
4. Normal durum
5. AI early-warning advisory
6. Deterministic Warning
7. High
8. Critical
9. Alarm / bildirim
10. Digital Panel Twin
11. Panel Detail açıklaması
12. Recovery / alarm resolved
13. İsteğe bağlı: Bad Sensor veya Arc fail-safe
14. Limitasyonlar ve gerçek saha uygulama yolu

Türkçe sunum ve jüri soru-cevap provası hazırlanacak.

---

## Sunum öncesi demo baseline

- 100 connected panel
- 100 NORMAL
- 0 active alarm
- backend online
- frontend online
- Edge Lab çalışıyor
- Digital Twin çalışıyor
- dil Türkçe

---

## Konumlandırma

GridGuard:

> Açıklanabilir elektrik panosu anomali izleme ve erken uyarı için geliştirilmiş; yazılım tabanlı saha/edge emülatörü ve kavramsal saha donanım mimarisiyle desteklenen bir yazılım prototipidir.

GridGuard şu değildir:

- sertifikalı koruma rölesi
- otonom anahtarlama sistemi
- saha doğrulaması tamamlanmış üretim cihazı
- fiziksel olarak üretilmiş sensör modülü

AI advisory katmanıdır. Deterministic kritik güvenlik kanıtı AI tarafından düşürülemez.
