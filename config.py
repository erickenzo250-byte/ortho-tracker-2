"""
🎯 ORTHOTRACK PRO — CONFIGURATION & CONSTANTS
Centralized settings for all modules
"""

# ═══════════════════════════════════════════════════════════════════════════════
# TARGETS & KPIs
# ═══════════════════════════════════════════════════════════════════════════════
TARGETS = {
    # Sales targets
    "rep_efficiency_cases_per_month": 15,
    "monthly_revenue": 50000,
    "average_implant_value": 2500,
    "conversion_rate_target": 0.75,  # 75% of planned → completed
    
    # Operational targets
    "facilities_per_rep": 8,
    "visit_frequency_days": 14,
    "inventory_turnover_days": 30,
    "payment_terms_days": 30,
}

# ═══════════════════════════════════════════════════════════════════════════════
# FACILITIES & REGIONS
# ═══════════════════════════════════════════════════════════════════════════════
FACILITIES = {
    "Moi Teaching & Referral Hospital": {"region": "East Africa", "tier": "A", "priority": 1},
    "Kenyatta National Hospital": {"region": "East Africa", "tier": "A", "priority": 1},
    "Aga Khan Hospital Nairobi": {"region": "East Africa", "tier": "A", "priority": 1},
    "MP Shah Hospital": {"region": "East Africa", "tier": "B", "priority": 2},
    "Nairobi Hospital": {"region": "East Africa", "tier": "B", "priority": 2},
    "AAR Hospital": {"region": "East Africa", "tier": "B", "priority": 2},
    "Coast General Hospital": {"region": "East Africa", "tier": "B", "priority": 2},
    "Eldoret Hospital": {"region": "East Africa", "tier": "C", "priority": 3},
    "Kisumu County Referral": {"region": "East Africa", "tier": "C", "priority": 3},
    "Nakuru Level 5 Hospital": {"region": "East Africa", "tier": "C", "priority": 3},
    "Thika Level 5 Hospital": {"region": "East Africa", "tier": "C", "priority": 3},
    "Mombasa Hospital": {"region": "East Africa", "tier": "C", "priority": 3},
}

# ═══════════════════════════════════════════════════════════════════════════════
# PROCEDURE CATEGORIES & VALUES
# ═══════════════════════════════════════════════════════════════════════════════
PROCEDURE_CATEGORIES = {
    "Hip": {
        "procedures": [
            "Total Hip Replacement",
            "Revision Hip Replacement",
            "Proximal Femur Replacement",
        ],
        "avg_value": 3500,
        "priority": 1,
    },
    "Knee": {
        "procedures": [
            "Total Knee Replacement",
            "Partial Knee Replacement",
            "Revision Knee Replacement",
        ],
        "avg_value": 3000,
        "priority": 2,
    },
    "Spine": {
        "procedures": [
            "Spinal Fusion L4-L5",
            "Spinal Fusion L5-S1",
        ],
        "avg_value": 4000,
        "priority": 1,
    },
    "Trauma": {
        "procedures": [
            "Tibial Nail Fixation",
            "Femoral Nail Fixation",
            "DHS Plate Fixation",
            "Locking Plate Fixation",
            "External Fixator Application",
        ],
        "avg_value": 2000,
        "priority": 3,
    },
    "Other": {
        "procedures": [
            "Shoulder Arthroplasty",
            "ACL Reconstruction",
            "Humeral Nail Fixation",
            "Ankle Replacement",
            "Wrist Arthroplasty",
        ],
        "avg_value": 2500,
        "priority": 4,
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# ALERT THRESHOLDS
# ═══════════════════════════════════════════════════════════════════════════════
ALERTS = {
    # Performance alerts
    "low_case_threshold": 8,  # Cases/month below this triggers alert
    "missed_visit_days": 21,  # No visit in X days = alert
    "payment_overdue_days": 35,
    "low_implant_stock": 3,
    "revenue_dip_percent": 20,  # 20% drop from baseline
    
    # Anomaly detection sensitivity
    "anomaly_zscore": 2.0,  # Z-score threshold for outliers
    "forecast_confidence": 0.75,  # Min confidence for forecast alerts
}

# ═══════════════════════════════════════════════════════════════════════════════
# AI/ML SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════
AI_CONFIG = {
    "forecast_horizon": 30,  # Days to forecast
    "lookback_days": 180,  # Historical data window
    "min_data_points": 10,  # Minimum for forecasting
    "anomaly_method": "zscore",  # Or "isolation_forest"
    "llm_model": "gpt-4-turbo",  # Or "claude-3-sonnet", "ollama"
    "insight_temperature": 0.7,
}

# ═══════════════════════════════════════════════════════════════════════════════
# COLORS & STYLING
# ═══════════════════════════════════════════════════════════════════════════════
COLORS = {
    "primary": "#2563EB",
    "success": "#0D9488",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "info": "#06B6D4",
    "secondary": "#8B5CF6",
    "accent": "#F97316",
}

STATUS_COLORS = {
    "high": "#EF4444",
    "medium": "#F59E0B",
    "low": "#10B981",
    "info": "#2563EB",
}
