// MetrOtoM – Kentsel ısı adası (KIA) ölçümü, Google Earth Engine Code Editor
// Kullanım: code.earthengine.google.com > yeni script > bu kodu yapıştır > Run
// Sonra sağdaki "Tasks" sekmesinde "metrotom_isi_adasi" işini RUN ile başlat;
// CSV, Google Drive'ına iner. O CSV'yi Claude'a gönder.
//
// Ne yapıyor: MODIS 1 km yüzey sıcaklığı (MOD11A2, 8 günlük) ile 2024–2025'in her ayı için
// 5 şehirde kentsel pikseller ile benzer yükseklikteki kırsal piksellerin gece/gündüz
// ortalama yüzey sıcaklığını hesaplar. Kent - kırsal farkı = ısı adası şiddeti.

var cities = ee.FeatureCollection([
  ee.Feature(ee.Geometry.Point([27.14, 38.42]), {name: 'Izmir'}),
  ee.Feature(ee.Geometry.Point([27.43, 38.61]), {name: 'Manisa'}),
  ee.Feature(ee.Geometry.Point([27.84, 37.85]), {name: 'Aydin'}),
  ee.Feature(ee.Geometry.Point([29.09, 37.78]), {name: 'Denizli'}),
  ee.Feature(ee.Geometry.Point([27.43, 37.04]), {name: 'Bodrum'})
]);

// Arazi örtüsü: 13 = kentsel; 6–12 ve 14 = çalı, çayır, tarım vb. (kırsal referans); 17 = su (hariç)
var lc = ee.ImageCollection('MODIS/061/MCD12Q1')
  .filterDate('2023-01-01', '2024-01-01').first().select('LC_Type1');
var urban = lc.eq(13);
var rural = lc.gte(6).and(lc.lte(12)).or(lc.eq(14));
var dem = ee.Image('USGS/SRTMGL1_003').select('elevation');

var lst = ee.ImageCollection('MODIS/061/MOD11A2')
  .select(['LST_Day_1km', 'LST_Night_1km'])
  .filterDate('2024-01-01', '2026-01-01');

var start = ee.Date('2024-01-01');
var months = ee.List.sequence(0, 23);

var rows = cities.map(function (c) {
  c = ee.Feature(c);
  var buf = c.geometry().buffer(25000); // şehir merkezi çevresinde 25 km
  var urbElev = ee.Number(dem.updateMask(urban).reduceRegion({
    reducer: ee.Reducer.mean(), geometry: buf, scale: 1000, maxPixels: 1e9
  }).get('elevation'));
  // Kırsal referans: kentle yüksekliği en fazla 150 m farklı pikseller (yükseklik etkisini dışlamak için)
  var ruralMask = rural.and(dem.subtract(urbElev).abs().lt(150));

  return ee.FeatureCollection(months.map(function (i) {
    var d0 = start.advance(ee.Number(i), 'month');
    var d1 = d0.advance(1, 'month');
    var img = lst.filterDate(d0, d1).mean().multiply(0.02).subtract(273.15); // °C
    var u = img.updateMask(urban).reduceRegion({
      reducer: ee.Reducer.mean(), geometry: buf, scale: 1000, maxPixels: 1e9
    });
    var r = img.updateMask(ruralMask).reduceRegion({
      reducer: ee.Reducer.mean(), geometry: buf, scale: 1000, maxPixels: 1e9
    });
    return ee.Feature(null, {
      sehir: c.get('name'),
      ay: d0.format('YYYY-MM'),
      kent_gece_C: u.get('LST_Night_1km'),
      kirsal_gece_C: r.get('LST_Night_1km'),
      kent_gunduz_C: u.get('LST_Day_1km'),
      kirsal_gunduz_C: r.get('LST_Day_1km')
    });
  }));
}).flatten();

print('İlk satırlar (kontrol):', rows.limit(6));

Export.table.toDrive({
  collection: rows,
  description: 'metrotom_isi_adasi',
  fileFormat: 'CSV',
  selectors: ['sehir', 'ay', 'kent_gece_C', 'kirsal_gece_C', 'kent_gunduz_C', 'kirsal_gunduz_C']
});
