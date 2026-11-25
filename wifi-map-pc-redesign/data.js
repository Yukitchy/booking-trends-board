// ワイスピ実データ（本番 wifi-map/spots.js と同一内容・写真ファイル名を付加）
const SPOTS = [
  { name:"猿田彦珈琲 アトレ秋葉原1店", area:"秋葉原", lat:35.698658, lng:139.772821,
    ssid:"SARUTAHIKOCOFFEE", password:"", down:199.0, up:152.2, measured_on:"2026-11-22", power:false,
    note:"アトレ秋葉原1の1F。2026-11-22 実測。下り199／上り152.2Mbps、レイテンシ6ms。電源は未確認", img:"sarutahiko-atre.jpg" },
  { name:"Keys Cafe Akihabara", area:"神田佐久間町一丁目", lat:35.697846, lng:139.77492,
    ssid:"keyscafeAKIHABARA", password:"", down:87, up:50, measured_on:"2026-11-25", power:true,
    note:"", img:"keyscafe-akiba.jpg" },
  { name:"スターバックス コーヒー 秋葉原駅前店", area:"秋葉原", lat:35.697825, lng:139.773721,
    ssid:"at_STARBUCKS_Wi2", password:null, down:null, up:null, measured_on:null, power:false,
    note:"AKIBA・TOLIM 1F。Wi-Fiは1回60分・再接続可。電源は未確認", img:"sbux-akiba-ekimae.jpg" },
  { name:"スターバックス コーヒー アトレ秋葉原1店", area:"秋葉原", lat:35.698658, lng:139.772821,
    ssid:"at_STARBUCKS_Wi2", password:null, down:null, up:null, measured_on:null, power:false,
    note:"アトレ秋葉原1の3F。Wi-Fiは1回60分・再接続可。電源は未確認", img:"sbux-atre-akiba.jpg" },
  { name:"マクドナルド 秋葉原駅前店", area:"秋葉原", lat:35.699306, lng:139.773866,
    ssid:"00_MCD-FREE-WIFI", password:null, down:null, up:null, measured_on:null, power:true,
    note:"24時間営業。2Fカウンター席に電源あり。Wi-Fiは1回60分", img:"mcd-akiba.jpg" },
  { name:"喫茶室ルノアール 秋葉原昭和通り口店", area:"秋葉原", lat:35.697856, lng:139.774716,
    ssid:"Renoir Miyama Wi-Fi", password:null, down:null, up:null, measured_on:null, power:true,
    note:"信交ビル2F。電源12口。Wi-Fiは1日3時間まで", img:"renoir-akiba.jpg" },
  { name:"快活CLUB 秋葉原駅前店", area:"秋葉原", lat:35.699155, lng:139.771633,
    ssid:"", password:null, down:null, up:null, measured_on:null, power:true,
    note:"24時間営業。鍵付完全個室あり・個室に電源。SSIDは現地で確認", img:"kaikatsu-akiba.jpg" },
  { name:"コメダ珈琲店 丸井錦糸町店", area:"錦糸町", lat:35.695031, lng:139.813644,
    ssid:"Komeda_Wi-Fi", password:null, down:null, up:null, measured_on:null, power:false,
    note:"錦糸町マルイ2F。Wi-Fiは1回60分・再接続可。電源は未確認", img:"komeda-kinshicho.jpg" },
  { name:"ドトールコーヒーショップ 錦糸町錦糸公園前店", area:"錦糸町", lat:35.697984, lng:139.814747,
    ssid:"DOUTOR_FREE_Wi-Fi", password:null, down:null, up:null, measured_on:null, power:true,
    note:"公式店舗情報にコンセント表記あり。Wi-Fiは1回60分", img:"doutor-kinshicho.jpg" },
  { name:"タリーズコーヒー 錦糸町テルミナ店", area:"錦糸町", lat:35.696467, lng:139.813981,
    ssid:"tullys_Wi-Fi", password:null, down:null, up:null, measured_on:null, power:true,
    note:"駅直結テルミナ4F。カウンター席に電源あり", img:"tullys-kinshicho.jpg" }
];
const MAXDOWN = 200;
const pct = v => Math.max(2, Math.round(v / MAXDOWN * 100));
const fmt = v => (v % 1 === 0 ? String(v) : v.toFixed(1));
const ssidLabel = s => s.ssid === "" ? "SSID 現地で確認" : s.ssid;
function pinIcon(measured){
  return L.divIcon({ className:"", iconSize:[26,34], iconAnchor:[13,32],
    html:`<svg width="26" height="34" viewBox="0 0 26 34"><path d="M13 33C13 33 1.5 20.5 1.5 12.5C1.5 6.1 6.6 1 13 1C19.4 1 24.5 6.1 24.5 12.5C24.5 20.5 13 33 13 33Z" fill="${measured?'#16c95c':'#ffffff'}" stroke="#101410" stroke-width="2"/><circle cx="13" cy="12.5" r="4.6" fill="${measured?'#ffffff':'#9aa79c'}"/></svg>` });
}
function initMap(el, opts){
  const local = new URLSearchParams(location.search).has("local");
  const dark = opts && opts.dark;
  const url = local
    ? (dark ? "tiles-dark/{z}/{y}/{x}.jpg" : "tiles/{z}/{y}/{x}.jpg")
    : (dark ? "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
            : "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}");
  const map = L.map(el, { zoomControl:false, attributionControl:true });
  L.tileLayer(url, { maxZoom:18, attribution:"Tiles © Esri / © OpenStreetMap contributors" }).addTo(map);
  SPOTS.forEach(s => L.marker([s.lat, s.lng], { icon: pinIcon(s.down !== null) }).addTo(map));
  if (opts && opts.fit) {
    map.fitBounds([[35.6925,139.7675],[35.7025,139.8205]], { padding:[24,24] });
  } else {
    map.setView((opts && opts.center) || [35.6975, 139.794], (opts && opts.zoom) || 14);
  }
  return map;
}
