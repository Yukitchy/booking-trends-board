// 実測Wi-Fiマップ スポットデータ
// 速度は実測したときだけ down / up / measured_on を入れる。未計測は null のまま。
// 1件追加するときは、この配列に1レコード足すだけでよい。
const SPOTS = [
  {
    name: "スターバックス コーヒー 秋葉原駅前店",
    area: "秋葉原",
    lat: 35.697825, lng: 139.773721,
    ssid: "at_STARBUCKS_Wi2",
    down: null, up: null, measured_on: null,
    power: false,
    note: "AKIBA・TOLIM 1F。Wi-Fiは1回60分・再接続可。電源は未確認",
    gmap: "https://www.google.com/maps/search/?api=1&query=%E3%82%B9%E3%82%BF%E3%83%BC%E3%83%90%E3%83%83%E3%82%AF%E3%82%B9%20%E3%82%B3%E3%83%BC%E3%83%92%E3%83%BC%20%E7%A7%8B%E8%91%89%E5%8E%9F%E9%A7%85%E5%89%8D%E5%BA%97"
  },
  {
    name: "スターバックス コーヒー アトレ秋葉原1店",
    area: "秋葉原",
    lat: 35.698658, lng: 139.772821,
    ssid: "at_STARBUCKS_Wi2",
    down: null, up: null, measured_on: null,
    power: false,
    note: "アトレ秋葉原1の3F。Wi-Fiは1回60分・再接続可。電源は未確認",
    gmap: "https://www.google.com/maps/search/?api=1&query=%E3%82%B9%E3%82%BF%E3%83%BC%E3%83%90%E3%83%83%E3%82%AF%E3%82%B9%20%E3%82%B3%E3%83%BC%E3%83%92%E3%83%BC%20%E3%82%A2%E3%83%88%E3%83%AC%E7%A7%8B%E8%91%89%E5%8E%9F1%E5%BA%97"
  },
  {
    name: "マクドナルド 秋葉原駅前店",
    area: "秋葉原",
    lat: 35.699306, lng: 139.773866,
    ssid: "00_MCD-FREE-WIFI",
    down: null, up: null, measured_on: null,
    power: true,
    note: "24時間営業（火曜深夜はメンテナンス休業）。2Fカウンター席に電源あり。Wi-Fiは1回60分",
    gmap: "https://www.google.com/maps/search/?api=1&query=%E3%83%9E%E3%82%AF%E3%83%89%E3%83%8A%E3%83%AB%E3%83%89%20%E7%A7%8B%E8%91%89%E5%8E%9F%E9%A7%85%E5%89%8D%E5%BA%97"
  },
  {
    name: "喫茶室ルノアール 秋葉原昭和通り口店",
    area: "秋葉原",
    lat: 35.697856, lng: 139.774716,
    ssid: "Renoir Miyama Wi-Fi",
    down: null, up: null, measured_on: null,
    power: true,
    note: "信交ビル2F。電源12口。Wi-Fiは1日3時間まで。落ち着いて作業しやすい",
    gmap: "https://www.google.com/maps/search/?api=1&query=%E5%96%AB%E8%8C%B6%E5%AE%A4%E3%83%AB%E3%83%8E%E3%82%A2%E3%83%BC%E3%83%AB%20%E7%A7%8B%E8%91%89%E5%8E%9F%E6%98%AD%E5%92%8C%E9%80%9A%E3%82%8A%E5%8F%A3%E5%BA%97"
  },
  {
    name: "快活CLUB 秋葉原駅前店",
    area: "秋葉原",
    lat: 35.699155, lng: 139.771633,
    ssid: "",
    down: null, up: null, measured_on: null,
    power: true,
    note: "24時間営業。鍵付完全個室あり・個室に電源。SSIDは現地で確認",
    gmap: "https://www.google.com/maps/search/?api=1&query=%E5%BF%AB%E6%B4%BBCLUB%20%E7%A7%8B%E8%91%89%E5%8E%9F%E9%A7%85%E5%89%8D%E5%BA%97"
  },
  {
    name: "コメダ珈琲店 丸井錦糸町店",
    area: "錦糸町",
    lat: 35.695031, lng: 139.813644,
    ssid: "Komeda_Wi-Fi",
    down: null, up: null, measured_on: null,
    power: false,
    note: "錦糸町マルイ2F。Wi-Fiは1回60分・再接続可。電源は未確認",
    gmap: "https://www.google.com/maps/search/?api=1&query=%E3%82%B3%E3%83%A1%E3%83%80%E7%8F%88%E7%90%B2%E5%BA%97%20%E4%B8%B8%E4%BA%95%E9%8C%A6%E7%B3%B8%E7%94%BA%E5%BA%97"
  },
  {
    name: "ドトールコーヒーショップ 錦糸町錦糸公園前店",
    area: "錦糸町",
    lat: 35.697984, lng: 139.814747,
    ssid: "DOUTOR_FREE_Wi-Fi",
    down: null, up: null, measured_on: null,
    power: true,
    note: "公式店舗情報にコンセント表記あり。Wi-Fiは1回60分",
    gmap: "https://www.google.com/maps/search/?api=1&query=%E3%83%89%E3%83%88%E3%83%BC%E3%83%AB%E3%82%B3%E3%83%BC%E3%83%92%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%83%E3%83%97%20%E9%8C%A6%E7%B3%B8%E7%94%BA%E9%8C%A6%E7%B3%B8%E5%85%AC%E5%9C%92%E5%89%8D%E5%BA%97"
  },
  {
    name: "タリーズコーヒー 錦糸町テルミナ店",
    area: "錦糸町",
    lat: 35.696467, lng: 139.813981,
    ssid: "tullys_Wi-Fi",
    down: null, up: null, measured_on: null,
    power: true,
    note: "駅直結テルミナ4F。カウンター席に電源あり",
    gmap: "https://www.google.com/maps/search/?api=1&query=%E3%82%BF%E3%83%AA%E3%83%BC%E3%82%BA%E3%82%B3%E3%83%BC%E3%83%92%E3%83%BC%20%E9%8C%A6%E7%B3%B8%E7%94%BA%E3%83%86%E3%83%AB%E3%83%9F%E3%83%8A%E5%BA%97"
  }
];
