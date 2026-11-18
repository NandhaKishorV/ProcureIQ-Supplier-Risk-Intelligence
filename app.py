import streamlit as st
import pandas as pd
import numpy as np
import os
import re
import time
import io
import sqlite3
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

try:
    from sqlalchemy import create_engine, text as sql_text, inspect as sql_inspect
    SQLALCHEMY_AVAILABLE = True
except Exception:
    SQLALCHEMY_AVAILABLE = False


st.set_page_config(
    page_title="ProcureIQ | Supplier Risk Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================= PROFESSIONAL UI =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:wght@500;600&display=swap');
:root{
  --bg:#ffffff;
  --surface:#ffffff;
  --surface-soft:#f6f8fb;
  --surface-muted:#f1f4f7;
  --line:#dfe5ec;
  --line-strong:#cfd8e3;
  --text:#17212b;
  --text-2:#4e5b68;
  --muted:#71808f;
  --navy:#102a43;
  --navy-2:#173b5c;
  --accent:#0b6f73;
  --accent-soft:#e8f5f3;
  --danger:#b42318;
  --warning:#9a6700;
}

/* Global enterprise editorial canvas */
html,body,[class*="css"]{
  font-family:'Inter','Segoe UI',Arial,sans-serif!important;
  color:#171717!important;
}
.stApp{background:#ffffff!important;color:#171717!important;}
[data-testid="stAppViewContainer"]{background:#ffffff!important;padding-top:0!important;}
[data-testid="stHeader"]{display:none!important;height:0!important;min-height:0!important;}
[data-testid="stToolbar"], [data-testid="stDecoration"]{display:none!important;}
.block-container{padding:0 2.6rem 3.5rem!important;max-width:1500px!important;}
/* Larger, presentation-grade body typography */
.stApp, .stApp p, .stApp label, .stApp input, .stApp textarea, .stApp button, .stApp [data-baseweb] {font-size:15px!important;}
.stMarkdown p{font-size:15px!important;}

/* Editorial typography */
h1,h2,h3,h4,h5,h6{
  color:#111111!important;
  font-family:'Source Serif 4','Georgia',serif!important;
  letter-spacing:-.035em!important;
}
h1{font-size:48px!important;font-weight:500!important;line-height:1.04!important;}
h2{font-size:36px!important;font-weight:500!important;}
h3{font-size:25px!important;font-weight:500!important;}
p,span,label,div{color:inherit;}
.stMarkdown p{color:#303030!important;line-height:1.65!important;}

/* Slim institutional sidebar */
section[data-testid="stSidebar"]{
  background:#ffffff!important;
  border-right:1px solid #e2ded8!important;
  box-shadow:none!important;
  min-width:280px!important;
  max-width:280px!important;
  width:280px!important;
  transform:translateX(0)!important;
  visibility:visible!important;
}
section[data-testid="stSidebar"] > div:first-child{
  width:280px!important;
}
/* Keep the workspace navigation visible even if Streamlit remembers a collapsed sidebar state. */
[data-testid="stSidebarCollapsedControl"]{display:none!important;}
section[data-testid="stSidebar"] *{color:#161616!important;}
section[data-testid="stSidebar"] .stRadio label{
  color:#454545!important;font-size:13px!important;font-weight:500!important;
  padding:6px 0!important;
}
section[data-testid="stSidebar"] .stRadio label:hover{color:#8a4b2d!important;}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:#666!important;}
.brand{display:flex;align-items:center;gap:12px;padding:10px 4px 28px;}
.brand-mark{
  width:40px;height:40px;border-radius:2px;display:flex;align-items:center;justify-content:center;
  background:#171717;color:#ffffff!important;font-weight:800;font-size:16px;box-shadow:none;
}
.brand-title{font-size:17px;font-weight:700;letter-spacing:-.01em;color:#111!important;}
.brand-sub{font-size:9px;color:#777!important;letter-spacing:.14em;text-transform:uppercase;margin-top:3px;}
section[data-testid="stSidebar"] hr{border-color:#dedad5!important;}
.sidebar-kicker{font-size:10px!important;font-weight:700!important;letter-spacing:.15em!important;color:#0b6f73!important;margin:0 0 10px!important;}
.sidebar-note{font-size:11px!important;line-height:1.9!important;color:#6a6a6a!important;}

/* JPM-inspired editorial hero: white, serif, generous whitespace, restrained brown rule */
.hero{
  position:relative;overflow:hidden;border:0;border-radius:0;padding:46px 0 48px;margin:0 0 6px;
  background:#ffffff;box-shadow:none;
}
.hero:before{content:"";position:absolute;left:0;right:0;top:0;height:4px;background:#0f2742;}
.hero-kicker{color:#0b6f73!important;font-size:11px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;margin-bottom:16px;}
.hero h1{
  font-family:'Source Serif 4','Georgia',serif!important;font-size:52px!important;line-height:1.0;margin:0;
  color:#111111!important;font-weight:500!important;letter-spacing:-.045em!important;max-width:none;white-space:nowrap;
}
.hero p{color:#3f3f3f!important;font-size:17px;max-width:930px;margin:18px 0 0;line-height:1.65!important;}
.badge{display:inline-block;border:1px solid #d8d2ca;background:#fbfaf8;padding:7px 11px;border-radius:0;font-size:9px;color:#444!important;margin:18px 5px 0 0;font-weight:600;letter-spacing:.03em;}

/* Section titles */
.section-title{font-family:'Source Serif 4','Georgia',serif!important;font-size:32px;font-weight:500;margin:24px 0 10px;color:#111!important;}
.small-muted{color:#6b6b6b!important;font-size:11px!important;line-height:1.6!important;}

/* KPI cards: editorial, not dashboard-bubble */
[data-testid="stMetric"]{
  background:#f7f9fb!important;border:0!important;border-top:2px solid #c9d3de!important;border-radius:0!important;
  padding:20px 18px 18px!important;box-shadow:none!important;min-height:112px;
}
[data-testid="stMetric"] [data-testid="stMetricValue"]{overflow:visible!important;white-space:nowrap!important;text-overflow:clip!important;max-width:none!important;width:auto!important;}
[data-testid="stMetric"] [data-testid="stMetricValue"] > div{overflow:visible!important;white-space:nowrap!important;text-overflow:clip!important;max-width:none!important;}
[data-testid="stMetricLabel"]{color:#4b5966!important;font-size:12px!important;font-weight:700!important;text-transform:uppercase!important;letter-spacing:.07em!important;}
[data-testid="stMetricValue"]{color:#102a43!important;font-family:'Source Serif 4','Georgia',serif!important;font-size:34px!important;font-weight:500!important;letter-spacing:-.04em!important;}
[data-testid="stMetricDelta"]{color:#555!important;}

/* Buttons */
.stButton>button{
  border:1px solid #171717!important;background:#102a43!important;color:#ffffff!important;border-radius:0!important;
  font-weight:600!important;min-height:44px;transition:transform .16s ease,background .16s ease!important;
}
.stButton>button:hover{transform:translateY(-1px);background:#0b6f73!important;border-color:#0b6f73!important;box-shadow:none!important;}

/* Upload */
[data-testid="stFileUploader"]{border:1px dashed #b9b0a7!important;border-radius:0!important;background:#faf9f7!important;padding:8px!important;}
[data-testid="stFileUploader"] *{color:#3e3e3e!important;}
[data-testid="stFileUploaderDropzone"]{background:#faf9f7!important;border-radius:0!important;}
[data-testid="stFileUploaderDropzoneInstructions"] div{color:#6a6a6a!important;}
[data-testid="stFileUploaderDropzone"] button{background:#ffffff!important;color:#171717!important;border:1px solid #c9c2ba!important;border-radius:0!important;}

/* Inputs / selects */
div[data-baseweb="select"]>div,div[data-baseweb="input"]>div{background:#ffffff!important;border-color:#c9c2ba!important;border-radius:0!important;color:#171717!important;}
div[data-baseweb="select"] *,div[data-baseweb="input"] *{color:#171717!important;}

/* Tables */
[data-testid="stDataFrame"]{border:1px solid #ddd7d0!important;border-radius:0!important;overflow:hidden;box-shadow:none!important;}

/* Alerts */
.stAlert{border-radius:0!important;border:1px solid #ded8d1!important;background:#faf9f7!important;color:#333!important;}
.stAlert p,.stAlert div{color:#333!important;}
hr{border-color:#ded8d1!important;}
.footer{margin-top:40px;padding:18px 0 6px;color:#8a8179!important;text-align:center;font-size:9px;letter-spacing:.09em;}
[data-testid="stVerticalBlock"]{gap:.65rem;}

/* Source selection / enterprise integration */
.source-card{background:#faf9f7;border-top:1px solid #cfc6bd;padding:18px 20px;margin:10px 0 22px;}
.source-card h3{font-family:'Source Serif 4','Georgia',serif!important;font-size:25px!important;margin:0 0 6px!important;}
.integration-note{font-size:11px!important;color:#666!important;line-height:1.7!important;}
.connection-badge{display:inline-block;border:1px solid #d8d2ca;padding:5px 9px;margin-right:6px;font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:#555!important;background:#fff;}
/* Dark editorial analytics section */
.ai-editorial{
  background:#1e1e1e;padding:30px 34px;margin:24px 0;border-top:4px solid #8a4b2d;
}
.ai-editorial .eyebrow{font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:#b8dff3!important;font-weight:700;}
.ai-editorial h2{color:#ffffff!important;font-size:34px!important;margin:7px 0 4px!important;}
.ai-editorial p{color:#d8d8d8!important;margin:0!important;}

@media (max-width: 900px){
  .hero h1{font-size:42px!important;white-space:normal!important;}
  .block-container{padding:0 1.4rem 2.5rem!important;}
}

/* Restrained motion + section-to-section slide transition */
@keyframes editorialReveal{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
@keyframes pageSlideIn{0%{opacity:0;transform:translateX(28px)}65%{opacity:1;transform:translateX(-2px)}100%{opacity:1;transform:translateX(0)}}
@keyframes softRise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
main .block-container{animation:pageSlideIn .48s cubic-bezier(.22,.61,.36,1) both;}
.hero{animation:pageSlideIn .42s cubic-bezier(.22,.61,.36,1) both;}
[data-testid="stMetric"]{animation:softRise .42s ease both;}
[data-testid="stMetric"]:nth-of-type(2){animation-delay:.04s;}
[data-testid="stMetric"]:nth-of-type(3){animation-delay:.08s;}
[data-testid="stMetric"]:nth-of-type(4){animation-delay:.12s;}
[data-testid="stMetric"]:nth-of-type(5){animation-delay:.16s;}
[data-testid="stMetric"]:nth-of-type(6){animation-delay:.20s;}
.stButton,.ai-editorial{animation:editorialReveal .3s ease both;}
/* Refined ProcureIQ symbol */
.brand-mark{position:relative;overflow:hidden;}
.brand-diamond{width:13px;height:13px;border:2px solid #ffffff;transform:rotate(45deg);display:block;position:absolute;left:12px;top:12px;}
.brand-dot{width:4px;height:4px;border-radius:50%;background:#ffffff;display:block;position:absolute;left:18px;top:18px;}
</style>
""", unsafe_allow_html=True)

DATA_FILE = "procurement_data.csv"

# =========================================================
# COLUMN MAPPING
# =========================================================

ALIASES = {
    "Supplier_ID": [
        "supplier_id", "supplier id", "supplier code", "vendor id",
        "vendor code", "vendor_id", "vendor code"
    ],
    "Supplier_Name": [
        "supplier_name", "supplier name", "vendor name", "vendor_name",
        "supplier", "vendor"
    ],
    "Category": [
        "category", "product category", "material category", "commodity"
    ],
    "Product": [
        "product", "product name", "item", "item name", "material",
        "material name", "sku", "part"
    ],
    "Order_Date": [
        "order_date", "order date", "po date", "po_date",
        "purchase order date", "purchase_date"
    ],
    "Expected_Delivery": [
        "expected_delivery", "expected delivery", "promised delivery date",
        "promised delivery", "expected delivery date", "due date"
    ],
    "Actual_Delivery": [
        "actual_delivery", "actual delivery", "delivery date",
        "actual delivery date", "received date", "receipt date"
    ],
    "Quantity": [
        "quantity", "ordered qty", "ordered quantity", "order quantity",
        "qty", "po quantity", "purchase quantity"
    ],
    "Unit_Price": [
        "unit_price", "unit price", "unit cost", "unit_cost",
        "price per unit", "purchase price", "rate"
    ],
    "Defective_Qty": [
        "defective_qty", "defective qty", "rejected qty", "rejected quantity",
        "defect quantity", "rejection qty", "damaged qty"
    ],
    "Financial_Risk": [
        "financial_risk", "financial risk", "supplier financial risk",
        "financial risk score", "credit risk", "financial score"
    ],
    "Price_Variance": [
        "price_variance", "price variance", "price variance %",
        "price variance percent", "cost variance", "price deviation"
    ]
}

CORE_FIELDS = ["Supplier_Name", "Quantity", "Unit_Price"]
OPTIONAL_FIELDS = [
    "Supplier_ID", "Category", "Product", "Order_Date",
    "Expected_Delivery", "Actual_Delivery", "Defective_Qty",
    "Financial_Risk", "Price_Variance"
]

def clean_name(name):
    return re.sub(r"[^a-z0-9]+", " ", str(name).strip().lower()).strip()

def find_column(columns, aliases):
    cleaned = {clean_name(c): c for c in columns}
    for alias in aliases:
        if clean_name(alias) in cleaned:
            return cleaned[clean_name(alias)]
    return None

def standardize_columns(data):
    data = data.copy()
    mapping = {}
    used = set()

    for standard, aliases in ALIASES.items():
        found = find_column(data.columns, aliases)
        if found and found not in used:
            mapping[standard] = found
            used.add(found)

    rename_map = {original: standard for standard, original in mapping.items()}
    data = data.rename(columns=rename_map)

    return data, mapping

# =========================================================
# RISK ENGINE
# =========================================================

def calculate_risk(row, weights):
    components = []

    if weights["delivery"] > 0 and pd.notna(row["Delivery_Delay_Days"]):
        delay = row["Delivery_Delay_Days"]
        if delay <= 0:
            score = 0
        elif delay <= 2:
            score = 25
        elif delay <= 5:
            score = 50
        elif delay <= 10:
            score = 75
        else:
            score = 100
        components.append(("Delivery", score, weights["delivery"]))

    if weights["quality"] > 0 and pd.notna(row["Defect_Rate"]):
        defect_rate = row["Defect_Rate"]
        if defect_rate <= 1:
            score = 10
        elif defect_rate <= 3:
            score = 30
        elif defect_rate <= 5:
            score = 60
        elif defect_rate <= 10:
            score = 80
        else:
            score = 100
        components.append(("Quality", score, weights["quality"]))

    if weights["financial"] > 0 and pd.notna(row["Financial_Risk"]):
        score = float(np.clip(row["Financial_Risk"], 0, 100))
        components.append(("Financial", score, weights["financial"]))

    if weights["price"] > 0 and pd.notna(row["Price_Variance"]):
        variance = row["Price_Variance"]
        if variance <= 0:
            score = 0
        elif variance <= 5:
            score = 25
        elif variance <= 10:
            score = 50
        elif variance <= 20:
            score = 75
        else:
            score = 100
        components.append(("Price", score, weights["price"]))

    if not components:
        return np.nan, "UNAVAILABLE", np.nan

    total_weight = sum(weight for _, _, weight in components)
    risk_score = sum(score * weight for _, score, weight in components) / total_weight

    if risk_score >= 70:
        level = "HIGH"
    elif risk_score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    probability = min(99, round(risk_score * 0.90, 1))
    return round(risk_score, 1), level, probability

# =========================================================
# AI / ML ENGINE
# =========================================================

AI_FEATURES = [
    "Order_Value", "Delivery_Delay_Days", "Defect_Rate",
    "Financial_Risk", "Price_Variance", "Quantity", "Unit_Price"
]

def run_ai_anomaly_detection(data):
    """Unsupervised ML layer using Isolation Forest.
    This does not require a pre-labelled disruption column, so it can work on
    new procurement spreadsheets immediately. The output is an ML anomaly
    signal, not a claim of future disruption probability.
    """
    model_df = data[AI_FEATURES].copy()
    for col in AI_FEATURES:
        model_df[col] = pd.to_numeric(model_df[col], errors="coerce")
    model_df = model_df.replace([np.inf, -np.inf], np.nan)
    model_df = model_df.fillna(model_df.median(numeric_only=True))
    model_df = model_df.fillna(0)

    if len(model_df) < 10:
        data["AI_Anomaly_Score"] = np.nan
        data["AI_Anomaly_Flag"] = "INSUFFICIENT DATA"
        return data, {"status": "insufficient", "model": "Isolation Forest", "n": len(model_df)}

    scaler = StandardScaler()
    X = scaler.fit_transform(model_df)
    contamination = min(0.12, max(0.03, 5 / len(model_df)))
    model = IsolationForest(
        n_estimators=250,
        contamination=contamination,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X)

    raw_score = -model.score_samples(X)
    # Convert relative anomaly strength into a 0-100 percentile signal.
    ranks = pd.Series(raw_score).rank(pct=True).to_numpy() * 100
    data["AI_Anomaly_Score"] = np.round(ranks, 1)
    threshold = np.quantile(ranks, 0.88)
    data["AI_Anomaly_Flag"] = np.where(
        ranks >= threshold, "ANOMALY", "NORMAL"
    )

    return data, {
        "status": "active",
        "model": "Isolation Forest",
        "features": AI_FEATURES,
        "anomalies": int((data["AI_Anomaly_Flag"] == "ANOMALY").sum()),
        "contamination": contamination
    }


def build_ai_insight(row):
    signals = []
    if pd.notna(row.get("Delivery_Delay_Days")) and row["Delivery_Delay_Days"] > 5:
        signals.append(f"delivery delay {row['Delivery_Delay_Days']:.0f} days")
    if pd.notna(row.get("Defect_Rate")) and row["Defect_Rate"] > 5:
        signals.append(f"defect rate {row['Defect_Rate']:.1f}%")
    if pd.notna(row.get("Financial_Risk")) and row["Financial_Risk"] > 70:
        signals.append(f"financial risk {row['Financial_Risk']:.0f}/100")
    if pd.notna(row.get("Price_Variance")) and row["Price_Variance"] > 10:
        signals.append(f"price variance {row['Price_Variance']:.1f}%")
    if row.get("AI_Anomaly_Flag") == "ANOMALY":
        signals.append("unusual procurement pattern detected by ML")

    if not signals:
        return "Continue routine monitoring; no major AI risk signal detected."

    if row.get("AI_Anomaly_Flag") == "ANOMALY":
        action = "Investigate the supplier and validate recent purchase-order activity before increasing exposure."
    elif pd.notna(row.get("Risk_Score")) and row["Risk_Score"] >= 70:
        action = "Prepare a contingency sourcing plan and review supplier dependency."
    else:
        action = "Monitor the highlighted drivers and review them at the next supplier performance cycle."

    return "Signals: " + "; ".join(signals) + ". " + action

# =========================================================
# PROCESS DATA
# =========================================================

def process_data(raw):
    data, mapping = standardize_columns(raw)

    missing_core = [c for c in CORE_FIELDS if c not in data.columns]
    if missing_core:
        return None, None, missing_core, [], 0

    quality_messages = []

    # Optional fields are created when absent.
    if "Supplier_ID" not in data.columns:
        data["Supplier_ID"] = (
            "SUP-" +
            data["Supplier_Name"].astype(str)
            .str.upper()
            .str.replace(r"[^A-Z0-9]+", "", regex=True)
            .str[:12]
        )
        quality_messages.append(
            "Supplier ID was not provided; IDs were generated from supplier names."
        )

    for col, default in {
        "Category": "Unknown",
        "Product": "Unknown"
    }.items():
        if col not in data.columns:
            data[col] = default
            quality_messages.append(f"{col} was not provided; 'Unknown' was used.")

    for col in ["Order_Date", "Expected_Delivery", "Actual_Delivery"]:
        if col in data.columns:
            data[col] = pd.to_datetime(data[col], errors="coerce")

    for col in ["Quantity", "Unit_Price", "Defective_Qty", "Financial_Risk", "Price_Variance"]:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    # Keep rows where core procurement economics are available.
    before = len(data)
    data = data.dropna(subset=["Supplier_Name", "Quantity", "Unit_Price"])
    removed = before - len(data)
    if removed:
        quality_messages.append(
            f"{removed} rows were excluded because supplier name, quantity, or unit price was missing."
        )

    data["Order_Value"] = data["Quantity"] * data["Unit_Price"]

    # Delivery metric
    has_delivery = (
        "Expected_Delivery" in data.columns and
        "Actual_Delivery" in data.columns and
        data["Expected_Delivery"].notna().any() and
        data["Actual_Delivery"].notna().any()
    )
    if has_delivery:
        data["Delivery_Delay_Days"] = (
            data["Actual_Delivery"] - data["Expected_Delivery"]
        ).dt.days.clip(lower=0)
    else:
        data["Delivery_Delay_Days"] = np.nan
        quality_messages.append(
            "Delivery dates were unavailable; delivery risk was excluded from the risk score."
        )

    # Quality metric
    has_quality = (
        "Defective_Qty" in data.columns and
        data["Defective_Qty"].notna().any()
    )
    if has_quality:
        safe_qty = data["Quantity"].replace(0, np.nan)
        data["Defect_Rate"] = (data["Defective_Qty"] / safe_qty) * 100
    else:
        data["Defect_Rate"] = np.nan
        quality_messages.append(
            "Defect/rejection quantity was unavailable; quality risk was excluded from the risk score."
        )

    has_financial = (
        "Financial_Risk" in data.columns and
        data["Financial_Risk"].notna().any()
    )
    if not has_financial:
        data["Financial_Risk"] = np.nan
        quality_messages.append(
            "Financial risk was unavailable; financial risk was excluded from the risk score."
        )

    has_price = (
        "Price_Variance" in data.columns and
        data["Price_Variance"].notna().any()
    )
    if not has_price:
        data["Price_Variance"] = np.nan
        quality_messages.append(
            "Price variance was unavailable; price risk was excluded from the risk score."
        )

    # Base weights: delivery 30%, quality 25%, financial 20%, price 15%.
    # Missing dimensions are automatically excluded and the available dimensions
    # are normalized so the score remains on a 0-100 scale.
    base_weights = {
        "delivery": 0.30 if has_delivery else 0,
        "quality": 0.25 if has_quality else 0,
        "financial": 0.20 if has_financial else 0,
        "price": 0.15 if has_price else 0
    }

    total_available = sum(base_weights.values())
    if total_available:
        weights = {k: v / total_available for k, v in base_weights.items()}
    else:
        weights = {k: 0 for k in base_weights}

    results = data.apply(lambda row: calculate_risk(row, weights), axis=1)
    risk_df = pd.DataFrame(
        results.tolist(),
        columns=["Risk_Score", "Risk_Level", "Disruption_Probability"],
        index=data.index
    )

    data = pd.concat([data, risk_df], axis=1)

    # Actual ML layer: unsupervised anomaly detection. This is independent of
    # the transparent weighted risk score above and does not require labels.
    data, ai_info = run_ai_anomaly_detection(data)

    # Data quality score: percentage of useful fields populated.
    quality_fields = [
        "Supplier_Name", "Quantity", "Unit_Price",
        "Order_Date", "Expected_Delivery", "Actual_Delivery",
        "Defective_Qty", "Financial_Risk", "Price_Variance"
    ]
    available_quality_fields = [c for c in quality_fields if c in raw.columns or c in data.columns]
    if available_quality_fields:
        completeness = data[available_quality_fields].notna().mean().mean() * 100
        quality_score = round(completeness, 1)
    else:
        quality_score = 0

    return data, weights, [], quality_messages, quality_score, ai_info

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="hero">
  <div class="hero-kicker">PROCUREMENT ANALYTICS · EXECUTIVE INTELLIGENCE</div>
  <h1>Supplier Risk Intelligence</h1>
  <p>Transform procurement data into disciplined supplier decisions — combining transparent risk scoring, machine-learning anomaly detection and actionable procurement intelligence.</p>
  <div style="margin-top:4px">
    <span class="badge">Excel / CSV</span><span class="badge">Automatic Mapping</span><span class="badge">ML Anomaly Detection</span><span class="badge">Adaptive Risk Model</span><span class="badge">Executive Intelligence</span><span class="badge">AI-Assisted Actions</span>
  </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# LOAD SAVED / SESSION DATA
# Keep this before every page so Power BI & SQL can access the
# analyzed dataset even when the user opens that page first.
# =========================================================
if "data" in st.session_state:
    data = st.session_state["data"]
    weights = st.session_state.get("weights", {})
    quality_messages = st.session_state.get("quality_messages", [])
    quality_score = st.session_state.get("quality_score", 0)
    ai_info = st.session_state.get("ai_info", {})
    source_label = st.session_state.get("source_label", "")
elif os.path.exists(DATA_FILE):
    data = pd.read_csv(DATA_FILE)
    weights = {}
    quality_messages = []
    quality_score = 0
    ai_info = {}
    source_label = "Saved analyzed dataset"
else:
    data = pd.DataFrame()
    weights = {}
    quality_messages = []
    quality_score = 0
    ai_info = {}
    source_label = ""

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("""
<div class="brand">
  <div class="brand-mark" aria-label="ProcureIQ logo">
    <span class="brand-diamond"></span><span class="brand-dot"></span>
  </div>
  <div><div class="brand-title">ProcureIQ</div><div class="brand-sub">Supplier Risk Intelligence</div></div>
</div>
""", unsafe_allow_html=True)
page = st.sidebar.radio(
    "WORKSPACE",
    ["Data Intake", "Dashboard", "Supplier Risk", "Recommendations", "Power BI & SQL"],
    key="workspace_navigation"
)
st.sidebar.markdown("---")
st.sidebar.markdown('<div class="sidebar-kicker">INTELLIGENCE ENGINE</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-note">Machine-learning anomaly detection<br>Adaptive supplier risk scoring<br>Automatic data mapping<br>Missing-data resilience</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div style="margin-top:26px;padding-top:14px;border-top:1px solid #e2ded8;color:#8a8a8a;font-size:10px;letter-spacing:.08em;text-transform:uppercase;">Procurement Intelligence Suite</div>', unsafe_allow_html=True)

# =========================================================
# DATA INTAKE — FILE / SQL / POWER BI
# =========================================================

if page == "Data Intake":
    st.header("Data Intake")
    st.write(
        "Connect procurement data from Excel/CSV, SQL databases, or Power BI-ready exports. "
        "ProcureIQ normalizes the source into one analytics model before risk and ML analysis."
    )

    source = st.radio(
        "DATA SOURCE",
        ["Excel / CSV", "SQL Database", "SQL Script (.sql)", "Power BI"],
        horizontal=True
    )

    raw_data = None
    source_label = ""

    if source == "Excel / CSV":
        st.markdown('<div class="source-card"><h3>File-based procurement data</h3><div class="integration-note">Upload an Excel workbook or CSV export from your ERP, procurement system, or Power BI. Column names are mapped automatically.</div></div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload procurement file",
            type=["xlsx", "csv"]
        )
        if uploaded_file:
            try:
                if uploaded_file.name.lower().endswith(".xlsx"):
                    raw_data = pd.read_excel(uploaded_file)
                else:
                    raw_data = pd.read_csv(uploaded_file)
                source_label = f"File: {uploaded_file.name}"
            except Exception as e:
                st.error(f"Could not read the file: {e}")

    elif source == "SQL Database":
        st.markdown('<div class="source-card"><h3>SQL procurement source</h3><div class="integration-note">Connect to a SQLAlchemy-compatible database. Examples: SQL Server, PostgreSQL, MySQL or SQLite. Use a read-only database account for production.</div></div>', unsafe_allow_html=True)
        if not SQLALCHEMY_AVAILABLE:
            st.error("SQL support requires SQLAlchemy. Install it with: python -m pip install sqlalchemy")
        else:
            conn_str = st.text_input(
                "SQLAlchemy connection string",
                placeholder="sqlite:///procurement.db  |  mssql+pyodbc://...  |  postgresql+psycopg2://...",
                type="password"
            )
            query = st.text_area(
                "SQL query",
                value="SELECT * FROM procurement_orders;",
                height=100
            )
            if st.button("Connect & Preview SQL Data", use_container_width=True):
                if not conn_str.strip() or not query.strip():
                    st.warning("Enter both a connection string and SQL query.")
                else:
                    try:
                        engine = create_engine(conn_str, pool_pre_ping=True)
                        with engine.connect() as conn:
                            raw_data = pd.read_sql(sql_text(query), conn)
                        st.session_state["sql_connection_string"] = conn_str
                        st.session_state["sql_query"] = query
                        st.session_state["sql_preview"] = raw_data
                        st.success(f"SQL query returned {len(raw_data):,} records.")
                    except Exception as e:
                        st.error(f"SQL connection/query failed: {e}")
            if "sql_preview" in st.session_state:
                raw_data = st.session_state["sql_preview"]
                source_label = "SQL Database"

    elif source == "SQL Script (.sql)":
        st.markdown('<div class="source-card"><h3>SQL script ingestion</h3><div class="integration-note">Drop a .sql file into the same folder as app.py, or upload one here. ProcureIQ executes the script in a local SQLite staging database, detects the created table, and loads the result into the AI risk engine.</div></div>', unsafe_allow_html=True)

        project_sql_files = sorted(Path.cwd().glob("*.sql"))
        file_options = ["— Choose a SQL file from this project folder —"] + [f.name for f in project_sql_files]
        selected_sql = st.selectbox("SQL file in project folder", file_options)
        uploaded_sql = st.file_uploader("Or upload a .sql file", type=["sql"], key="sql_script_upload")

        sql_bytes = None
        sql_name = None
        if uploaded_sql is not None:
            sql_bytes = uploaded_sql.getvalue()
            sql_name = uploaded_sql.name
        elif selected_sql != file_options[0]:
            sql_path = Path.cwd() / selected_sql
            sql_bytes = sql_path.read_bytes()
            sql_name = selected_sql

        if sql_bytes is not None:
            st.caption(f"Selected SQL script: {sql_name}")
            sql_preview = sql_bytes.decode("utf-8", errors="replace")
            with st.expander("Preview SQL script"):
                st.code(sql_preview[:12000], language="sql")

            if st.button("Load SQL Script into ProcureIQ", use_container_width=True):
                try:
                    # Execute the script in an in-memory SQLite database.
                    # This avoids Windows file-locking errors when Streamlit reruns the app.
                    # The database exists only for this load operation; the uploaded .sql file
                    # remains the source of truth.
                    with sqlite3.connect(":memory:") as conn:
                        conn.executescript(sql_preview)
                        tables = pd.read_sql_query(
                            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name",
                            conn
                        )["name"].tolist()
                        if not tables:
                            raise ValueError("The SQL script ran successfully but did not create any user tables.")

                        # Prefer a procurement-looking table when the script creates multiple tables.
                        preferred = [t for t in tables if any(k in t.lower() for k in ["procurement", "purchase", "supplier", "order"])]
                        table = preferred[0] if preferred else tables[0]
                        raw_data = pd.read_sql_query(f'SELECT * FROM "{table}"', conn)

                    st.session_state["sql_script_preview"] = raw_data
                    st.session_state["sql_script_table"] = table
                    st.session_state["sql_script_name"] = sql_name
                    st.success(f"Loaded {len(raw_data):,} records from SQL table '{table}'.")
                except Exception as e:
                    st.error(f"SQL script could not be loaded: {e}")

        if "sql_script_preview" in st.session_state:
            raw_data = st.session_state["sql_script_preview"]
            source_label = f"SQL Script: {st.session_state.get('sql_script_name', 'file')} → {st.session_state.get('sql_script_table', 'table')}"

    else:
        st.markdown('<div class="source-card"><h3>Power BI data workflow</h3><div class="integration-note">Power BI reports use a semantic model rather than a simple .pbix table file. Export the relevant table/query as CSV from Power BI, then load it here. ProcureIQ also creates a Power BI-ready output after analysis.</div></div>', unsafe_allow_html=True)
        pbi_file = st.file_uploader(
            "Upload Power BI table export",
            type=["csv", "xlsx"],
            key="pbi_upload"
        )
        st.markdown('<span class="connection-badge">Power BI Export</span><span class="connection-badge">Power BI Ready Output</span><span class="connection-badge">Automatic Mapping</span>', unsafe_allow_html=True)
        if pbi_file:
            try:
                if pbi_file.name.lower().endswith(".xlsx"):
                    raw_data = pd.read_excel(pbi_file)
                else:
                    raw_data = pd.read_csv(pbi_file)
                source_label = f"Power BI export: {pbi_file.name}"
            except Exception as e:
                st.error(f"Could not read the Power BI export: {e}")

    if raw_data is not None:
        st.success(f"Loaded {len(raw_data):,} procurement records from {source_label}.")
        st.subheader("Raw Data Preview")
        st.dataframe(raw_data.head(10), use_container_width=True)

        st.subheader("Automatic Column Mapping")
        standardized, mapping = standardize_columns(raw_data)
        mapping_rows = []
        for standard in ALIASES:
            mapping_rows.append({
                "App Field": standard,
                "Uploaded Column": mapping.get(standard, "Not provided"),
                "Status": "Found" if standard in mapping else "Missing"
            })
        st.dataframe(pd.DataFrame(mapping_rows), use_container_width=True)

        missing_core = [c for c in CORE_FIELDS if c not in standardized.columns]
        if missing_core:
            st.error("The dataset is missing the minimum information needed for procurement analysis:")
            st.write(missing_core)
            st.info("Supplier Name, Quantity and Unit Price are the minimum required fields. Other fields are optional.")
            st.stop()

        if st.button("Analyze Entire Dataset", type="primary", use_container_width=True):
            with st.spinner("Building supplier risk intelligence…"):
                time.sleep(0.55)
                analyzed_data, weights, missing, messages, quality_score, ai_info = process_data(raw_data)

            st.session_state["data"] = analyzed_data
            st.session_state["weights"] = weights
            st.session_state["quality_messages"] = messages
            st.session_state["quality_score"] = quality_score
            st.session_state["ai_info"] = ai_info
            st.session_state["source_label"] = source_label
            analyzed_data.to_csv(DATA_FILE, index=False)

            st.success(f"Analysis complete — {len(analyzed_data):,} records processed.")
            st.balloons()

            if messages:
                st.warning("Data Quality Notices")
                for msg in messages:
                    st.write("•", msg)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Records", len(analyzed_data))
            c2.metric("Suppliers", analyzed_data["Supplier_ID"].nunique())
            c3.metric("Procurement Spend", f"₹{analyzed_data['Order_Value'].sum():,.0f}")
            c4.metric("AI Anomalies", int((analyzed_data["AI_Anomaly_Flag"] == "ANOMALY").sum()))

            st.subheader("Data Integration Status")
            st.info(f"Source: {source_label}. Power BI can consume the analyzed output as a flat table, while SQL users can persist the same model directly to a database table.")

            st.subheader("AI & Risk Engine")
            weight_text = " | ".join([
                f"{name.title()} {weights[key]*100:.0f}%"
                for key, name in [("delivery", "Delivery"), ("quality", "Quality"), ("financial", "Financial"), ("price", "Price")]
                if weights[key] > 0
            ])
            st.info(
                f"Transparent risk score: {weight_text or 'No risk dimensions available'}. "
                "Missing dimensions are excluded rather than treated as zero risk. "
                "AI layer: Isolation Forest anomaly detection across procurement behavior."
            )

            st.subheader("Analyzed Data")
            st.dataframe(analyzed_data, use_container_width=True)

# =========================================================
# POWER BI & SQL INTEGRATION
# =========================================================

if page == "Power BI & SQL":
    # Defensive guard: this page must never fail just because no dataset was loaded.
    data = st.session_state.get("data", pd.DataFrame())
    st.header("Power BI & SQL Integration")
    st.write("Use ProcureIQ as the intelligence layer between your operational procurement data and enterprise reporting.")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Power BI")
        st.write("Export the analyzed ProcureIQ table and load it into Power BI as a dataset/model table. This keeps the AI anomaly and supplier-risk fields available for Power BI visuals.")
        if not data.empty:
            csv_bytes = data.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Power BI-ready CSV",
                data=csv_bytes,
                file_name="ProcureIQ_PowerBI_Model.csv",
                mime="text/csv",
                use_container_width=True
            )
            xlsx_buf = io.BytesIO()
            with pd.ExcelWriter(xlsx_buf, engine="openpyxl") as writer:
                data.to_excel(writer, index=False, sheet_name="ProcureIQ_Model")
            st.download_button(
                "Download Power BI-ready Excel",
                data=xlsx_buf.getvalue(),
                file_name="ProcureIQ_PowerBI_Model.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            st.caption("Recommended Power BI model table: ProcureIQ_Model. Refresh the file from your governed data pipeline when new procurement data is available.")
        else:
            st.info("Analyze a dataset first to create the Power BI-ready model.")

    with c2:
        st.subheader("SQL")
        st.write("Persist the analyzed model into a SQL table so Power BI, Excel or other enterprise tools can query the same governed dataset.")
        if not SQLALCHEMY_AVAILABLE:
            st.warning("SQLAlchemy is not installed. Run: python -m pip install sqlalchemy")
        elif data.empty:
            st.info("Analyze a dataset first to enable SQL export.")
        else:
            sql_conn = st.text_input("SQLAlchemy connection string", key="sql_export_conn", placeholder="sqlite:///procureiq.db")
            table_name = st.text_input("Destination table", value="procureiq_supplier_risk")
            if st.button("Write ProcureIQ Model to SQL", use_container_width=True):
                try:
                    engine = create_engine(sql_conn, pool_pre_ping=True)
                    data.to_sql(table_name, engine, if_exists="replace", index=False)
                    st.success(f"Wrote {len(data):,} records to SQL table '{table_name}'.")
                except Exception as e:
                    st.error(f"SQL write failed: {e}")

    st.divider()
    st.subheader("Recommended Enterprise Architecture")
    st.code("ERP / Procurement System  →  SQL Database  →  ProcureIQ AI/ML  →  ProcureIQ Model Table  →  Power BI", language="text")
    st.write("For a production deployment, keep SQL as the governed source of truth and use Power BI for enterprise reporting. ProcureIQ becomes the analytics/ML layer rather than replacing the organization's data platform.")
# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":
    st.header("Executive Procurement Dashboard")
    if source_label:
        st.caption(f"Data source: {source_label}")

    if data.empty:
        st.info("Upload your Excel dataset first.")
        st.stop()

    total_suppliers = data["Supplier_ID"].nunique()
    total_spend = data["Order_Value"].sum()
    high_risk = (data["Risk_Level"] == "HIGH").sum()
    at_risk_spend = data.loc[
        data["Risk_Level"] == "HIGH", "Order_Value"
    ].sum()

    ai_anomalies = int((data["AI_Anomaly_Flag"] == "ANOMALY").sum()) if "AI_Anomaly_Flag" in data.columns else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("Suppliers", f"{total_suppliers:,}")
    c2.metric("Procurement Spend", f"₹{total_spend:,.0f}")
    c3.metric("High Risk Records", f"{high_risk:,}")
    c4, c5, c6 = st.columns(3)
    c4.metric("At-Risk Spend", f"₹{at_risk_spend:,.0f}")
    c5.metric("AI Anomalies", f"{ai_anomalies:,}")
    c6.metric("Data Quality", f"{quality_score:.0f}%")

    if quality_messages:
        with st.expander("⚠️ Data Quality Notices"):
            for msg in quality_messages:
                st.write("•", msg)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Risk Distribution")
        st.bar_chart(data["Risk_Level"].value_counts())

    with col2:
        st.subheader("Procurement Spend by Category")
        category_spend = (
            data.groupby("Category")["Order_Value"]
            .sum()
            .sort_values(ascending=False)
        )
        st.bar_chart(category_spend)

    st.markdown('''<div class="ai-editorial"><div class="eyebrow">AI PROCUREMENT INTELLIGENCE</div><h2>Machine-Learning Signals</h2><p>Unsupervised anomaly detection highlights procurement activity that deserves management attention.</p></div>''', unsafe_allow_html=True)
    if "AI_Anomaly_Score" in data.columns:
        ai_view = data.loc[data["AI_Anomaly_Flag"] == "ANOMALY", [
            "Supplier_Name", "Category", "Order_Value", "Risk_Score", "AI_Anomaly_Score", "AI_Anomaly_Flag"
        ]].sort_values("AI_Anomaly_Score", ascending=False).head(10)
        if not ai_view.empty:
            st.dataframe(ai_view, use_container_width=True)
        else:
            st.success("No unusual procurement patterns were detected by the ML anomaly model.")

    st.subheader("Top 10 Highest-Risk Suppliers")

    supplier_summary = (
        data.groupby(["Supplier_ID", "Supplier_Name"])
        .agg(
            Risk_Score=("Risk_Score", "mean"),
            Procurement_Spend=("Order_Value", "sum"),
            Avg_Delay=("Delivery_Delay_Days", "mean"),
            Avg_Defect_Rate=("Defect_Rate", "mean")
        )
        .reset_index()
        .sort_values("Risk_Score", ascending=False)
        .head(10)
    )

    st.dataframe(supplier_summary, use_container_width=True)

# =========================================================
# SUPPLIER RISK
# =========================================================

if page == "Supplier Risk":
    st.header("Supplier Risk Analysis")

    if data.empty:
        st.info("Upload your Excel dataset first.")
        st.stop()

    supplier_names = (
        data["Supplier_Name"].dropna().unique().tolist()
    )

    selected = st.selectbox("Select Supplier", supplier_names)
    supplier = data[data["Supplier_Name"] == selected]

    risk_score = supplier["Risk_Score"].mean()
    disruption = supplier["Disruption_Probability"].mean()
    spend = supplier["Order_Value"].sum()
    delay = supplier["Delivery_Delay_Days"].mean()
    defects = supplier["Defect_Rate"].mean()

    ai_score = supplier["AI_Anomaly_Score"].mean() if "AI_Anomaly_Score" in supplier.columns else np.nan
    ai_flag = "ANOMALY" if "AI_Anomaly_Flag" in supplier.columns and (supplier["AI_Anomaly_Flag"] == "ANOMALY").any() else "NORMAL"
    c1, c2, c3 = st.columns(3)
    c1.metric("Risk Score", "N/A" if pd.isna(risk_score) else f"{risk_score:.1f}/100")
    c2.metric("Disruption Signal", "N/A" if pd.isna(disruption) else f"{disruption:.1f}%")
    c3.metric("AI Anomaly", ai_flag)
    c4, c5, c6 = st.columns(3)
    c4.metric("Spend", f"₹{spend:,.0f}")
    c5.metric("Avg Delay", "N/A" if pd.isna(delay) else f"{delay:.1f} days")
    c6.metric("Defect Rate", "N/A" if pd.isna(defects) else f"{defects:.2f}%")

    if pd.isna(risk_score):
        st.info("Risk score is unavailable because no risk-factor data was provided.")
    elif risk_score >= 70:
        st.error("🔴 HIGH RISK SUPPLIER")
    elif risk_score >= 40:
        st.warning("🟡 MEDIUM RISK SUPPLIER")
    else:
        st.success("🟢 LOW RISK SUPPLIER")

    st.subheader("AI Assessment")
    supplier_ai_row = supplier.iloc[0].to_dict() if not supplier.empty else {}
    st.info(build_ai_insight(supplier_ai_row))

    st.subheader("Supplier Procurement History")
    st.dataframe(supplier, use_container_width=True)

# =========================================================
# RECOMMENDATIONS
# =========================================================

if page == "Recommendations":
    st.header("Procurement Recommendations")

    if data.empty:
        st.info("Upload your Excel dataset first.")
        st.stop()

    supplier_summary = (
        data.groupby(["Supplier_ID", "Supplier_Name"])
        .agg(
            Risk_Score=("Risk_Score", "mean"),
            Spend=("Order_Value", "sum"),
            Avg_Delay=("Delivery_Delay_Days", "mean"),
            Avg_Defect=("Defect_Rate", "mean"),
            Financial_Risk=("Financial_Risk", "mean"),
            Price_Variance=("Price_Variance", "mean")
        )
        .reset_index()
        .sort_values("Risk_Score", ascending=False)
    )

    for _, row in supplier_summary.head(15).iterrows():
        risk = row["Risk_Score"]

        if pd.isna(risk):
            st.info(f"ℹ️ {row['Supplier_Name']} — insufficient risk data")
        elif risk >= 70:
            st.error(f"🔴 {row['Supplier_Name']} — Risk Score {risk:.1f}/100")
        elif risk >= 40:
            st.warning(f"🟡 {row['Supplier_Name']} — Risk Score {risk:.1f}/100")
        else:
            st.success(f"🟢 {row['Supplier_Name']} — Risk Score {risk:.1f}/100")

        st.write(f"**Procurement Spend:** ₹{row['Spend']:,.0f}")
        st.write("**Recommended Actions:**")

        actions = []

        if pd.notna(row["Avg_Delay"]) and row["Avg_Delay"] > 5:
            actions.append("Evaluate alternate suppliers because of delivery delays.")

        if pd.notna(row["Avg_Defect"]) and row["Avg_Defect"] > 5:
            actions.append("Conduct a supplier quality audit.")

        if pd.notna(row["Financial_Risk"]) and row["Financial_Risk"] > 70:
            actions.append("Reduce dependency because of financial risk.")

        if pd.notna(row["Price_Variance"]) and row["Price_Variance"] > 10:
            actions.append("Renegotiate supplier pricing.")

        if pd.notna(risk) and risk >= 70:
            actions.append("Create a contingency sourcing plan.")

        if not actions:
            actions.append("Continue monitoring supplier performance.")

        ai_supplier = row.to_dict()
        st.info("**AI assessment:** " + build_ai_insight(ai_supplier))

        for action in actions:
            st.write("→", action)

        st.divider()

st.markdown(
    """
    <div class="footer">
    PROCUREIQ • SUPPLIER RISK & PROCUREMENT INTELLIGENCE • BUILT FOR DATA-DRIVEN PROCUREMENT DECISIONS
    </div>
    """,
    unsafe_allow_html=True
)
