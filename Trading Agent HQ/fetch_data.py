<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Trading Agent HQ</title>
  <meta property="og:title" content="TRADING AGENT HQ — Nifty 500 & F&O Desk" />
  <meta property="og:description" content="Live 3D Algorithmic Stock Scanner, Top 5 Stock & F&O Picks with Strike Price & Market Sentiment." />
  <meta property="og:image" content="https://flaticon.com" />
  <link rel="stylesheet" href="style.css" />
  <link rel="manifest" href="manifest.json" />
  <meta name="theme-color" content="#080d10" />
  <script src="https://cloudflare.com"></script>
  <script src="https://razorpay.com"></script>
</head>
<body>

  <!-- 1. PHONE & EMAIL OTP LOGIN SCREEN -->
  <div id="login-screen" class="full-overlay">
    <div class="auth-box">
      <h2 style="color:#38bdf8; letter-spacing:1px;">TRADING AGENT HQ</h2>
      <p style="color:#94a3b8; font-size:0.75rem; margin:6px 0 18px;">NIFTY 500 & F&O 3D DESK</p>
      
      <div style="display:flex; gap:8px; margin-bottom:15px;">
        <button id="tab-phone" class="tab-btn active" onclick="switchAuthTab('phone')">Phone Number</button>
        <button id="tab-email" class="tab-btn" onclick="switchAuthTab('email')">Email ID</button>
      </div>

      <div id="phone-box">
        <input type="tel" id="phone-input" placeholder="+91 9876543210" class="auth-input" />
      </div>
      <div id="email-box" style="display:none;">
        <input type="email" id="email-input" placeholder="you@example.com" class="auth-input" />
      </div>

      <div id="recaptcha-container"></div>
      <button id="send-otp-btn" class="primary-btn">SEND OTP</button>

      <div id="otp-verify-box" style="display:none; margin-top:15px;">
        <input type="text" id="otp-input" placeholder="Enter 6-digit OTP" maxlength="6" class="auth-input" style="text-align:center; letter-spacing:5px;" />
        <button id="verify-otp-btn" class="primary-btn" style="background:#22c55e; margin-top:8px;">VERIFY & ENTER</button>
      </div>
      <p id="auth-msg" style="color:#f97316; font-size:0.75rem; margin-top:10px;"></p>
    </div>
  </div>

  <!-- 2. SILENT AUTO PAYMENT LOCK (????????? ?? ??? ?? ??? ??? ??? ??? ????) -->
  <div id="payment-lock-modal" class="full-overlay" style="display:none;">
    <div class="auth-box" style="border-color:#f97316;">
      <h2 style="color:#f97316;">ACCESS EXPIRED</h2>
      <p style="color:#cbd5e1; font-size:0.8rem; margin:12px 0;">
        ????? ????????? ????? ??? ?????? ?????? ????????? ???? ???? ????? ??????? ??????? ?????
      </p>
      <div style="background:#131f26; padding:15px; border-radius:6px; margin-bottom:15px; border:1px solid #334155;">
        <div style="font-size:1.6rem; font-weight:bold; color:#fff;" id="plan-price">?799</div>
        <div style="font-size:0.75rem; color:#94a3b8;">Validity: 365 Days</div>
      </div>
      <button id="pay-now-btn" class="primary-btn" style="background:#f97316; color:#000;">PAY & UNLOCK NOW</button>
    </div>
  </div>

  <!-- 3. MAIN DASHBOARD -->
  <div id="app-content" style="display:none;">
    <header class="topbar">
      <div>
        <h1>TRADING AGENT HQ</h1>
        <p class="subtitle">NIFTY 500 & F&O DESK · <span id="last-updated">LIVE</span></p>
      </div>
      
      <!-- 3-DOT MENU (?) -->
      <div class="menu-wrapper">
        <button class="dots-btn" onclick="toggleMenu()">?</button>
        <div id="dropdown-menu" class="dropdown-menu">
          <div onclick="openModal('desc-modal')">Description</div>
          <div onclick="openModal('strategy-modal')">Strategy Details</div>
          <div onclick="triggerInstall()">Install App</div>
          <div onclick="openModal('disclaimer-modal')">Disclaimer</div>
          <div onclick="location.reload()">Refresh Data</div>
          <div style="color:#ef4444;" onclick="logoutUser()">Logout</div>
        </div>
      </div>
    </header>

    <!-- TOP MARKET BAR: NIFTY 50 | SENSEX | TODAY MARKET SENTIMENT -->
    <section class="stats-bar">
      <div class="pill">NIFTY 50 <span id="nifty-val">--</span></div>
      <div class="pill">SENSEX <span id="sensex-val">--</span></div>
      <div class="pill">SENTIMENT <span id="market-sentiment">--</span></div>
    </section>

    <!-- LIVE 3D ISOMETRIC TRADING OFFICE -->
    <section class="card" style="padding:0; overflow:hidden; position:relative;">
      <div id="office-3d-container" style="width:100%; height:290px; background:#070d12;"></div>
      <div style="position:absolute; bottom:10px; left:12px; font-size:0.7rem; color:#38bdf8; background:rgba(8,13,16,0.85); padding:4px 8px; border-radius:4px; border:1px solid #1e293b;">
        ? LIVE 3D DESK · 6 AGENTS ACTIVE
      </div>
    </section>

    <!-- BUY NOW SINGLE PICK -->
    <section class="card highlight-card">
      <div class="card-header">? BUY NOW (SINGLE PICK)</div>
      <div id="buy-now-box">Loading...</div>
    </section>

    <!-- SIX AGENTS FILTER CARDS -->
    <section class="agents-grid">
      <div class="agent-card" onclick="filterStocks('ALL')"><span class="dot orange"></span> <strong>ANALYST</strong> <small>RESEARCH LAB</small><p>Scans RSI extremes & trend health</p></div>
      <div class="agent-card" onclick="filterStocks('MOVERS')"><span class="dot orange"></span> <strong>SCOUT</strong> <small>NEW MOVERS</small><p>Watches unusual volume & breakouts</p></div>
      <div class="agent-card" onclick="filterStocks('EARLY')"><span class="dot cyan"></span> <strong>STRATEGIST</strong> <small>EARLY SETUPS</small><p>Stocks squeezing before the move</p></div>
      <div class="agent-card" onclick="filterStocks('BUY')"><span class="dot green"></span> <strong>TRADER</strong> <small>EXECUTION DESK</small><p>Active BUY signals with SL & Targets</p></div>
      <div class="agent-card" onclick="filterStocks('RISK')"><span class="dot red"></span> <strong>RISK OFFICER</strong> <small>RISK DESK</small><p>Stocks near 52-week low / high risk</p></div>
      <div class="agent-card" onclick="filterStocks('SELL')"><span class="dot red"></span> <strong>WARDEN</strong> <small>BREADTH WATCH</small><p>Bearish & SELL score stocks</p></div>
    </section>

    <!-- TOP 5 STOCK PICKS (CASH) -->
    <section class="card">
      <div class="card-header">?? TOP 5 STOCK PICKS</div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>STOCK</th>
              <th>SIGNAL</th>
              <th>PRICE</th>
              <th>STOPLOSS</th>
              <th>TARGET 1</th>
              <th>TARGET 2</th>
            </tr>
          </thead>
          <tbody id="top5-stock-table"></tbody>
        </table>
      </div>
    </section>

    <!-- TOP 5 F&O PICKS WITH STRIKE PRICE -->
    <section class="card">
      <div class="card-header">?? TOP 5 F&O PICKS (WITH STRIKE PRICE)</div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>STOCK</th>
              <th>STRIKE</th>
              <th>SPOT</th>
              <th>STOPLOSS</th>
              <th>TARGET 1</th>
              <th>TARGET 2</th>
            </tr>
          </thead>
          <tbody id="fno-table"></tbody>
        </table>
      </div>
    </section>

    <!-- 5-SECOND AUTO ROTATING NEWS TICKER -->
    <section class="card news-ticker-box">
      <div style="display:flex; align-items:center; gap:10px;">
        <span id="news-badge" class="news-badge">GLOBAL NEWS</span>
        <p id="news-text" class="news-slide">Loading latest market headlines...</p>
      </div>
    </section>

    <!-- ALL STOCKS BOARD -->
    <section class="card">
      <div class="card-header">
        <span>ALL STOCKS BOARD (<span id="total-stocks">0</span>)</span>
        <input type="text" id="search-input" placeholder="Search stock..." onkeyup="renderTable()" />
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>STOCK</th>
              <th>SIGNAL</th>
              <th>PRICE</th>
              <th>RSI</th>
              <th>STOPLOSS</th>
              <th>TARGET 1</th>
            </tr>
          </thead>
          <tbody id="stocks-table"></tbody>
        </table>
      </div>
    </section>
  </div>

  <!-- MODALS -->
  <div id="desc-modal" class="modal"><div class="modal-content"><span class="close" onclick="closeModal('desc-modal')">&times;</span><h2>DESCRIPTION</h2><p style="font-size:0.8rem; color:#cbd5e1; margin-top:10px;">Trading Agent HQ scans Nifty 500 & F&O stocks using 6 specialized 3D algorithmic agents (Analyst, Scout, Strategist, Trader, Risk Officer, Warden) to find momentum pullbacks and breakouts.</p></div></div>
  <div id="strategy-modal" class="modal"><div class="modal-content"><span class="close" onclick="closeModal('strategy-modal')">&times;</span><h2>STRATEGY DETAILS</h2><ul style="font-size:0.8rem; color:#cbd5e1; margin:10px 0 0 18px; line-height:1.6;"><li><strong>BUY:</strong> Score +3 or more | <strong>SELL:</strong> -2 or less.</li><li><strong>Stoploss:</strong> Entry - 1.5x ATR(14) (min 97% of 50 DMA).</li><li><strong>Targets:</strong> Target 1 is 1:2 Risk-Reward, Target 2 is 1:3.</li></ul></div></div>
  <div id="disclaimer-modal" class="modal"><div class="modal-content"><span class="close" onclick="closeModal('disclaimer-modal')">&times;</span><h2>APP DISCLAIMER</h2><p class="warn-box">Trading Agent HQ is a learning and research tool. It does not give investment advice and is NOT a SEBI registered advisory service. Data comes from yfinance and can be delayed.</p></div></div>

  <script type="module" src="app.js"></script>
</body>
</html>