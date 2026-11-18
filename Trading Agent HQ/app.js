import { initializeApp } from "https://gstatic.com";
import { getAuth, RecaptchaVerifier, signInWithPhoneNumber, sendSignInLinkToEmail, isSignInWithEmailLink, signInWithEmailLink, onAuthStateChanged, signOut } from "https://gstatic.com";
import { getFirestore, doc, getDoc, setDoc, updateDoc } from "https://gstatic.com";

// ????? ????? Firebase ?????????? ??????
const firebaseConfig = {
  apiKey: "AIzaSyBEJ-Gdo_nIsQ-0h6kOJZjg3ZxcHMrOJJk",
  authDomain: "trading-agent-hq.firebaseapp.com",
  projectId: "trading-agent-hq",
  storageBucket: "trading-agent-hq.firebasestorage.app",
  messagingSenderId: "707768472343",
  appId: "1:707768472343:web:ccd67513c5f18c09649d52"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const RAZORPAY_KEY = "YOUR_RAZORPAY_KEY_ID";

let authMode = 'phone';
let confirmationResult = null;
let deferredPrompt = null;
let is3DInitialized = false;

window.addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); deferredPrompt = e; });
window.triggerInstall = () => {
  if (deferredPrompt) deferredPrompt.prompt();
  else alert("Browser menu ???? 'Install App' ?? 'Add to Home Screen' ??????? ?????");
};

window.toggleMenu = () => {
  const m = document.getElementById('dropdown-menu');
  m.style.display = m.style.display === 'block' ? 'none' : 'block';
};
window.logoutUser = () => signOut(auth);

window.switchAuthTab = (mode) => {
  authMode = mode;
  document.getElementById('tab-phone').classList.toggle('active', mode === 'phone');
  document.getElementById('tab-email').classList.toggle('active', mode === 'email');
  document.getElementById('phone-box').style.display = mode === 'phone' ? 'block' : 'none';
  document.getElementById('email-box').style.display = mode === 'email' ? 'block' : 'none';
};

if (isSignInWithEmailLink(auth, window.location.href)) {
  let email = window.localStorage.getItem('emailForSignIn') || window.prompt('Confirm your email:');
  signInWithEmailLink(auth, email, window.location.href).then(() => window.localStorage.removeItem('emailForSignIn'));
}

document.getElementById('send-otp-btn').onclick = async () => {
  const msg = document.getElementById('auth-msg');
  if (authMode === 'phone') {
    const phone = document.getElementById('phone-input').value.trim();
    if (!phone) return msg.innerText = "???? ??? ????? ??? (+91 ??)";
    try {
      if (!window.recaptchaVerifier) {
        window.recaptchaVerifier = new RecaptchaVerifier(auth, 'recaptcha-container', { size: 'invisible' });
      }
      confirmationResult = await signInWithPhoneNumber(auth, phone, window.recaptchaVerifier);
      document.getElementById('otp-verify-box').style.display = 'block';
      msg.innerText = "???? OTP ?????? ?????!";
    } catch (e) { msg.innerText = e.message; }
  } else {
    const email = document.getElementById('email-input').value.trim();
    if (!email) return msg.innerText = "???? Email ID ???";
    try {
      await sendSignInLinkToEmail(auth, email, { url: window.location.href, handleCodeInApp: true });
      window.localStorage.setItem('emailForSignIn', email);
      msg.innerText = "????? ?????? ?????????? ???? ?????? ?????!";
    } catch (e) { msg.innerText = e.message; }
  }
};

document.getElementById('verify-otp-btn').onclick = async () => {
  const code = document.getElementById('otp-input').value.trim();
  if (!code || !confirmationResult) return;
  try { await confirmationResult.confirm(code); }
  catch (e) { document.getElementById('auth-msg').innerText = "??? OTP! ???? ?????? ?????"; }
};

onAuthStateChanged(auth, async (user) => {
  if (!user) {
    document.getElementById('login-screen').style.display = 'flex';
    document.getElementById('app-content').style.display = 'none';
    return;
  }
  document.getElementById('login-screen').style.display = 'none';
  checkUserAccess(user);
});

async function checkUserAccess(user) {
  const userRef = doc(db, "users", user.uid);
  const snap = await getDoc(userRef);
  const now = Date.now();
  const DAY_MS = 24 * 60 * 60 * 1000;

  if (!snap.exists()) {
    await setDoc(userRef, { contact: user.phoneNumber || user.email, expiryDate: now + (20 * DAY_MS), hasPaidOnce: false });
    unlockApp();
  } else {
    const data = snap.data();
    if (now <= data.expiryDate) unlockApp();
    else showPaymentLock(user, userRef, data.hasPaidOnce ? 849 : 799);
  }
}

setInterval(() => { if (auth.currentUser) checkUserAccess(auth.currentUser); }, 60000);

function showPaymentLock(user, userRef, amount) {
  document.getElementById('app-content').style.display = 'none';
  document.getElementById('payment-lock-modal').style.display = 'flex';
  document.getElementById('plan-price').innerText = `?${amount}`;

  document.getElementById('pay-now-btn').onclick = () => {
    new Razorpay({
      key: RAZORPAY_KEY,
      amount: amount * 100,
      currency: "INR",
      name: "Trading Agent HQ",
      description: "365 Days Access",
      handler: async function () {
        await updateDoc(userRef, { expiryDate: Date.now() + (365 * 24 * 60 * 60 * 1000), hasPaidOnce: true });
        document.getElementById('payment-lock-modal').style.display = 'none';
        unlockApp();
      }
    }).open();
  };
}

function unlockApp() {
  document.getElementById('app-content').style.display = 'block';
  if (!is3DInitialized) { init3DOffice(); is3DInitialized = true; }
  loadMarketData();
}

// 3D ISOMETRIC TRADING OFFICE
function init3DOffice() {
  const container = document.getElementById('office-3d-container');
  if (!container || typeof THREE === 'undefined') return;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x070d12);
  const aspect = container.clientWidth / container.clientHeight;
  const d = 6.5;
  const camera = new THREE.OrthographicCamera(-d * aspect, d * aspect, d, -d, 1, 1000);
  camera.position.set(10, 10, 10);
  camera.lookAt(0, 0, 0);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  container.appendChild(renderer.domElement);

  scene.add(new THREE.AmbientLight(0xffffff, 0.65));
  const dirLight = new THREE.DirectionalLight(0x38bdf8, 0.85);
  dirLight.position.set(5, 12, 8);
  scene.add(dirLight);

  const floor = new THREE.Mesh(new THREE.BoxGeometry(11, 0.3, 11), new THREE.MeshStandardMaterial({ color: 0x0f1922 }));
  floor.position.y = -0.15;
  scene.add(floor);
  scene.add(new THREE.GridHelper(11, 11, 0x1e293b, 0x131f26));

  const positions = [
    { x: -3, z: -2.2, color: 0xf97316 }, { x: 0, z: -2.2, color: 0x38bdf8 }, { x: 3, z: -2.2, color: 0xa855f7 },
    { x: -3, z: 2.2, color: 0x22c55e },  { x: 0, z: 2.2, color: 0xef4444 },  { x: 3, z: 2.2, color: 0xeab308 }
  ];

  const robots = [];
  positions.forEach((pos) => {
    const desk = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.6, 1), new THREE.MeshStandardMaterial({ color: 0x1e293b }));
    desk.position.set(pos.x, 0.3, pos.z);
    scene.add(desk);

    const group = new THREE.Group();
    const body = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.6, 0.4), new THREE.MeshStandardMaterial({ color: pos.color }));
    body.position.y = 0.6;
    const head = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.38, 0.42), new THREE.MeshStandardMaterial({ color: 0xe2e8f0 }));
    head.position.y = 1.15;
    group.add(body, head);
    group.position.set(pos.x, 0, pos.z + 0.8);
    scene.add(group);
    robots.push(group);
  });

  let clock = 0;
  function animate() {
    requestAnimationFrame(animate);
    clock += 0.04;
    robots.forEach((r, i) => {
      r.position.y = Math.abs(Math.sin(clock + i)) * 0.12;
      r.rotation.y = Math.sin(clock * 0.5 + i) * 0.25;
    });
    renderer.render(scene, camera);
  }
  animate();
}

// LOAD DATA, TOP 5 CASH, TOP 5 F&O & 5-SEC NEWS
let allStocks = [];
let currentFilter = 'ALL';

async function loadMarketData() {
  const res = await fetch('data.json?t=' + Date.now());
  const data = await res.json();
  document.getElementById('last-updated').innerText = data.last_updated;
  document.getElementById('nifty-val').innerText = `${data.nifty.price} (${data.nifty.change_pct}%)`;
  document.getElementById('sensex-val').innerText = `${data.sensex.price} (${data.sensex.change_pct}%)`;
  
  const sentEl = document.getElementById('market-sentiment');
  sentEl.innerText = data.sentiment;
  sentEl.style.color = data.sentiment === 'BULLISH' ? '#22c55e' : (data.sentiment === 'BEARISH' ? '#ef4444' : '#f59e0b');
  document.getElementById('total-stocks').innerText = data.stats.total_stocks;

  if (data.buy_now) {
    const b = data.buy_now;
    document.getElementById('buy-now-box').innerHTML = `<strong>${b.symbol}</strong> · Price: ?${b.price} | SL: ?${b.stoploss} (-${b.risk_pct}%) | T1: ?${b.target_1} | T2: ?${b.target_2}`;
  }

  allStocks = data.stocks;
  const top5 = [...allStocks].sort((a, b) => b.buy_now_points - a.buy_now_points).slice(0, 5);

  document.getElementById('top5-stock-table').innerHTML = top5.map(s => `
    <tr>
      <td><strong>${s.symbol}</strong></td>
      <td style="color:${s.signal === 'BUY' ? '#22c55e' : '#f97316'}">${s.signal}</td>
      <td>?${s.price}</td>
      <td>?${s.stoploss}</td>
      <td style="color:#22c55e;">?${s.target_1}</td>
      <td style="color:#38bdf8;">?${s.target_2}</td>
    </tr>
  `).join('');

  document.getElementById('fno-table').innerHTML = top5.map(s => `
    <tr>
      <td><strong>${s.symbol}</strong></td>
      <td style="color:#f97316; font-weight:bold;">${s.strike}</td>
      <td>?${s.price}</td>
      <td>?${s.stoploss}</td>
      <td style="color:#22c55e;">?${s.target_1}</td>
      <td style="color:#38bdf8;">?${s.target_2}</td>
    </tr>
  `).join('');

  if (data.news && data.news.length > 0) {
    let idx = 0;
    const badge = document.getElementById('news-badge');
    const txt = document.getElementById('news-text');
    const rotateNews = () => {
