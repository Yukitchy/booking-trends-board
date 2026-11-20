// モック用の最小の動き（本番の通信はしない）
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
function toast(t){ let e = $(".toast"); if(!e){ e = document.createElement("div"); e.className = "toast"; document.body.append(e); }
  e.textContent = t; e.classList.add("on"); clearTimeout(e._t); e._t = setTimeout(() => e.classList.remove("on"), 1800); }
function openSheet(id){ $("#" + id).classList.add("on"); }
document.addEventListener("click", e => {
  const s = e.target.closest(".sheet"); if(s && e.target === s) s.classList.remove("on");
  const c = e.target.closest("[data-close]"); if(c) c.closest(".sheet").classList.remove("on");
  const o = e.target.closest("[data-open]"); if(o) openSheet(o.dataset.open);
  const p = e.target.closest(".picks img"); if(p){ $$("img", p.parentNode).forEach(i => i.classList.toggle("on", i === p));
    const t = p.closest(".sheet").dataset.target; if(t) $$(t).forEach(x => x.style.backgroundImage = `url(${p.src})`); }
  const sh = e.target.closest(".shape"); if(sh) $$(".shape", sh.parentNode).forEach(i => i.classList.toggle("on", i === sh));
});
// 写真選びシート（ミカエラのフィード7枚）
function photoSheet(id, target, title = "写真を選ぶ"){
  const imgs = [1,2,3,4,5,6,7].map(i => `<img src="img/ig-0${i}.webp" alt=""${i === 3 ? ' class="on"' : ""}>`).join("");
  document.body.insertAdjacentHTML("beforeend", `<div class="sheet" id="${id}" data-target="${target}"><div>
    <p class="h2" style="margin-bottom:12px">${title}</p><div class="picks">${imgs}</div>
    <p class="muted" style="margin:10px 0 14px">選んだ写真の中で、顔が真ん中に来るよう自動で切り抜きます。</p>
    <button class="btn" data-close>これにする</button></div></div>`);
}
// 文を直すシート
function quoteSheet(id){
  document.body.insertAdjacentHTML("beforeend", `<div class="sheet" id="${id}"><div>
    <p class="h2" style="margin-bottom:6px">載せる文</p>
    <p class="muted" style="margin:0 0 10px">Airbnb ★5 のレビューから、名前の入った文を抜いてあります。</p>
    <textarea>He customized the perfect day for my husband and I in Akibara. We learned so much about the area.</textarea>
    <details style="margin:10px 0 16px"><summary class="muted">元のレビュー全文</summary><p class="muted">We had the BEST day with Yuuki!! He customized the perfect day for my husband and I in Akibara. We learned so much about the area. I can’t recommend this tour enough!!!</p></details>
    <button class="btn" data-close>これにする</button></div></div>`);
}
const QUOTE = "He customized the perfect day for my husband and I in Akibara. We learned so much about the area.";
const rvHTML = (tag = "") => `<div class="rv">${tag ? `<span class="tag">${tag}</span>` : ""}<p class="q">${QUOTE}</p><p class="st"><b>★★★★★</b>　AIRBNB REVIEW</p></div>`;
// 通常ストーリーを直すシート（主役写真・形・立ち寄り先を1枚にまとめる）
function storySheet(id){
  const imgs = [1,2,3,4,5,6,7].map(i => `<img src="img/ig-0${i}.webp" alt=""${i === 7 ? ' class="on"' : ""}>`).join("");
  document.body.insertAdjacentHTML("beforeend", `<div class="sheet" id="${id}"><div>
    <p class="h2" style="margin-bottom:12px">ストーリーを直す</p>
    <p style="font-weight:800;margin:0 0 6px">形</p>
    <div class="shapes">
      <button class="shape on"><span class="ic" style="background:#333 url(img/ig-07.webp) center/cover"><b style="position:absolute;left:6px;top:4px;color:#fff;font-size:15px">11.19</b></span>日付を大きく</button>
      <button class="shape" style="opacity:.45"><span class="ic" style="background:#fff;border:1px solid #ddd"><i style="position:absolute;inset:0 0 45% 0;background:url(img/ig-07.webp) center/cover"></i><i style="position:absolute;left:6px;right:6px;bottom:8px;height:26%;background:repeating-linear-gradient(#ccc 0 5px,#fff 5px 11px)"></i></span>立ち寄り先つき</button>
      <button class="shape"><span class="ic" style="background:#333 url(img/ig-07.webp) center/cover"><i style="position:absolute;left:8px;bottom:10px;background:#E60012;width:60%;height:12px;border-radius:9px"></i></span>ありがとう</button>
    </div>
    <p class="muted" style="margin:6px 0 16px">「立ち寄り先つき」は寄ったお店を2か所以上入れると選べます。</p>
    <p style="font-weight:800;margin:0 0 6px">いちばん大きく出す写真</p>
    <div class="picks">${imgs}</div>
    <p style="font-weight:800;margin:16px 0 6px">寄ったお店（0か所）</p>
    <button class="btn quiet" style="min-height:44px;font-size:14px" onclick="toast('写真から選んで追加（モックでは省略）')">＋ お店を足す</button>
    <div style="height:18px"></div>
    <button class="btn" data-close onclick="toast('作り直しています（約5分）')">この内容で作り直す</button></div></div>`);
}
