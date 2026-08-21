"""
regenerate_pdfs.py
Regenerates the 3 problematic PDF files in knowledge_base/ that have table
formatting issues when extracted with PyPDF:
  - Pricing.pdf
  - ShippingPolicy.pdf
  - UserManual.pdf

Uses reportlab with proper Table layout so pdfplumber can extract tables cleanly.
Run from the customer-support-ai/ directory:
    python backend/scripts/regenerate_pdfs.py
"""

import sys
import os
from pathlib import Path

# Safe UTF-8 console output for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
KB_DIR = PROJECT_ROOT / "knowledge_base"

styles = getSampleStyleSheet()
h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=14, spaceAfter=6, spaceBefore=10)
h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=12, spaceAfter=4, spaceBefore=8)
body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=9, spaceAfter=4, leading=13)
small = ParagraphStyle("Small", parent=styles["Normal"], fontSize=8, spaceAfter=2, leading=11)
title_style = ParagraphStyle("Title", parent=styles["Title"], fontSize=16, spaceAfter=4, alignment=TA_CENTER)
subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"], fontSize=10, spaceAfter=2, alignment=TA_CENTER, textColor=colors.grey)

TABLE_HEADER_COLOR = colors.HexColor("#1a3d6e")
TABLE_ROW_COLOR_A = colors.HexColor("#f0f4f8")
TABLE_ROW_COLOR_B = colors.white
TABLE_BORDER = colors.HexColor("#c0c8d4")

def base_table_style(header_rows=1):
    return TableStyle([
        # Header styling
        ("BACKGROUND", (0, 0), (-1, header_rows - 1), TABLE_HEADER_COLOR),
        ("TEXTCOLOR", (0, 0), (-1, header_rows - 1), colors.white),
        ("FONTNAME", (0, 0), (-1, header_rows - 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, header_rows - 1), 9),
        ("ALIGN", (0, 0), (-1, header_rows - 1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, header_rows), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, header_rows), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, header_rows), (-1, -1), [TABLE_ROW_COLOR_A, TABLE_ROW_COLOR_B]),
        ("GRID", (0, 0), (-1, -1), 0.5, TABLE_BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])


tbl_hdr_style = ParagraphStyle(
    "RegenHdrStyle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=8.5,
    leading=11,
    textColor=colors.white,
    alignment=TA_LEFT,
)

tbl_cell_style = ParagraphStyle(
    "RegenCellStyle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.0,
    leading=11,
    textColor=colors.HexColor("#1f2937"),
    alignment=TA_LEFT,
)

def make_wrapped_table(data, col_widths, header_rows=1):
    processed = []
    for r_idx, row in enumerate(data):
        row_out = []
        for cell in row:
            st = tbl_hdr_style if r_idx < header_rows else tbl_cell_style
            cell_str = str(cell).replace("\n", "<br/>")
            row_out.append(Paragraph(cell_str, st))
        processed.append(row_out)

    tbl = Table(processed, colWidths=col_widths)
    tbl.setStyle(base_table_style(header_rows=header_rows))
    return tbl


# =====================================================================
# Pricing.pdf
# =====================================================================
def build_pricing_pdf():
    out = KB_DIR / "Pricing.pdf"
    doc = SimpleDocTemplate(str(out), pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []

    story.append(Paragraph("TechMart Electronics — Hardware Pricing, Subscriptions & Volume Discounts", title_style))
    story.append(Paragraph("Official Corporate Policy & Reference Documentation | Doc ID: TM-CAT-PRICING-2026", subtitle_style))
    story.append(Spacer(1, 0.4*cm))

    # Section 1: Hardware Product Lineup
    story.append(Paragraph("1. Hardware Product Lineup & Retail Pricing (2026 Catalog)", h1))
    story.append(Paragraph(
        "Official MSRP pricing for all TechMart flagship consumer electronics and smart home devices.",
        body
    ))

    hw_data = [
        ["Product Model", "SKU", "Retail Price (MSRP)", "TechMart Care+ Add-on"],
        ["TechMart SmartHub Pro\n(Central IoT Controller)", "TM-SHP-01", "$199.99", "$39.99 / 2 yrs"],
        ["TechMart SoundWave 500\n(Hi-Res Audio Speaker)", "TM-SW500-02", "$149.99", "$29.99 / 2 yrs"],
        ["TechMart VisionStream 4K\n(Ultra HD Media Box)", "TM-VS4K-03", "$129.99", "$24.99 / 2 yrs"],
        ["TechMart SmartSensor Trio\n(Door/Window Pack)", "TM-SST-04", "$59.99", "$14.99 / 2 yrs"],
        ["TechMart PowerPulse 65W\nGaN Charger", "TM-PP65-05", "$39.99", "N/A (1-yr standard)"],
    ]
    hw_table = make_wrapped_table(hw_data, [5.2*cm, 2.8*cm, 4.3*cm, 4.3*cm])
    story.append(hw_table)
    story.append(Spacer(1, 0.4*cm))

    # Section 2: Subscription Tiers
    story.append(Paragraph("2. SmartHub Cloud Intelligence Subscription Tiers", h1))
    story.append(Paragraph(
        "Enhance your SmartHub Pro with cloud event storage, multi-camera AI recognition, "
        "and remote cellular backup.",
        body
    ))

    sub_data = [
        ["Tier", "Monthly Price", "Annual Price\n(Save 17%)", "Key Features"],
        ["Basic (Free)", "$0.00", "$0.00",
         "Live 1080p streaming, local SD card recording, 24h clip buffer"],
        ["Plus Plan", "$4.99 / mo", "$49.99 / yr",
         "30-day cloud recording (up to 3 devices), AI motion alerts"],
        ["Pro Premium", "$9.99 / mo", "$99.99 / yr",
         "60-day cloud recording (unlimited devices), Person & Pet AI detection, 24/7 cellular backup"],
    ]
    sub_table = make_wrapped_table(sub_data, [3*cm, 3*cm, 3.5*cm, 7.1*cm])
    story.append(sub_table)
    story.append(Spacer(1, 0.4*cm))

    # Section 3: Bundle Packages
    story.append(Paragraph("3. Bundle Packages & Promotional Discounts", h1))
    items = [
        "Home Security Essentials Bundle: SmartHub Pro + 2 SmartSensor Trios + 1-yr Plus Plan for $279.99 (Save $60).",
        "Audiophile Home Theater Bundle: VisionStream 4K + 2 SoundWave 500 units for $369.99 (Save $59.98).",
        "Work From Home Bundle: SmartHub Pro + PowerPulse 65W Charger for $219.99 (Save $19.99).",
    ]
    story.append(ListFlowable([ListItem(Paragraph(i, body)) for i in items], bulletType="bullet"))
    story.append(Spacer(1, 0.4*cm))

    # Section 4: Volume Discount Tiers
    story.append(Paragraph("4. Corporate & Volume Purchase Discount Tiers", h1))
    story.append(Paragraph(
        "Available for business, enterprise, and institutional orders. "
        "A signed purchase order (PO) is required for orders over $5,000.",
        body
    ))

    vol_data = [
        ["Order Quantity (Units)", "Discount Rate", "Eligible SKUs", "Payment Terms"],
        ["5 – 19 units", "5% off MSRP", "All hardware SKUs", "Net-15"],
        ["20 – 49 units", "10% off MSRP", "All hardware SKUs", "Net-30"],
        ["50 – 99 units", "15% off MSRP", "All hardware SKUs", "Net-30"],
        ["100+ units", "20% off MSRP + free shipping", "All hardware SKUs", "Net-45 / PO required"],
    ]
    vol_table = make_wrapped_table(vol_data, [4.2*cm, 3.5*cm, 4.2*cm, 4.7*cm])
    story.append(vol_table)
    story.append(Spacer(1, 0.4*cm))

    # Section 5: Return & Price Match Policy
    story.append(Paragraph("5. Price Adjustment & Price Match Policy", h1))
    story.append(Paragraph(
        "TechMart Electronics offers a 14-day price adjustment guarantee. "
        "If the price of an item you purchased drops within 14 days of your order date, "
        "contact support@techmart.com with your order number to request a price adjustment credit.",
        body
    ))
    story.append(Paragraph(
        "Price match is available against identical SKUs sold by authorized US retailers "
        "(Amazon, Best Buy, B&H Photo). Screenshot or link required. "
        "Price match excludes marketplace sellers, refurbished items, and limited-time flash sales.",
        body
    ))

    doc.build(story)
    print(f"  [OK] {out.name} regenerated ({out.stat().st_size:,} bytes)")


# =====================================================================
# ShippingPolicy.pdf
# =====================================================================
def build_shipping_pdf():
    out = KB_DIR / "ShippingPolicy.pdf"
    doc = SimpleDocTemplate(str(out), pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []

    story.append(Paragraph("TechMart Electronics — Shipping, Delivery & Fulfillment Policy", title_style))
    story.append(Paragraph("Official Corporate Policy & Reference Documentation | Doc ID: TM-POL-SHIP-2026", subtitle_style))
    story.append(Spacer(1, 0.4*cm))

    # Section 1: Domestic Shipping
    story.append(Paragraph("1. Domestic Shipping Options (United States & Canada)", h1))
    story.append(Paragraph(
        "TechMart Electronics partners with FedEx, UPS, and DHL Express to ensure rapid, "
        "reliable delivery of all electronics, audio equipment, and smart home accessories.",
        body
    ))

    ship_data = [
        ["Shipping Tier", "Estimated Transit Time", "Cost (Orders < $50)", "Cost (Orders >= $50)"],
        ["Standard Ground", "3 - 5 business days", "$5.99 flat rate", "FREE ($0.00)"],
        ["Expedited 2-Day", "2 business days", "$12.99 flat rate", "$8.99 discounted"],
        ["Priority Overnight", "Next business day by 3 PM", "$24.99 flat rate", "$19.99 flat rate"],
        ["Saturday Express Delivery", "Saturday delivery", "$29.99 flat rate", "$29.99 flat rate"],
    ]
    ship_table = make_wrapped_table(ship_data, [4.5*cm, 4*cm, 4*cm, 4.1*cm])
    story.append(ship_table)
    story.append(Spacer(1, 0.4*cm))

    # Section 2: Order Processing
    story.append(Paragraph("2. Order Cut-Off Times & Order Processing", h1))
    story.append(Paragraph(
        "Orders placed before 2:00 PM EST Monday through Friday are processed and dispatched "
        "on the same business day. Orders placed after 2:00 PM EST or on weekends/holidays "
        "will ship on the following business day.",
        body
    ))
    notes = [
        "Signature Requirement: Orders exceeding $300 in value require an adult signature upon delivery.",
        "P.O. Boxes & APO/FPO: Standard Ground via USPS is required for all P.O. Box and Military "
        "APO/FPO addresses (transit time 5 - 9 business days).",
    ]
    story.append(ListFlowable([ListItem(Paragraph(n, body)) for n in notes], bulletType="bullet"))
    story.append(Spacer(1, 0.3*cm))

    # Section 3: International Shipping
    story.append(Paragraph("3. International Shipping Rates & Customs Duties", h1))
    story.append(Paragraph(
        "TechMart delivers to over 45 countries worldwide. International shipping rates are "
        "calculated at checkout based on package weight and destination country.",
        body
    ))

    intl_data = [
        ["Region", "Carrier", "Estimated Delivery", "Approx. Starting Cost"],
        ["Canada", "FedEx International", "3 - 5 business days", "$9.99"],
        ["United Kingdom / EU", "DHL Express", "4 - 7 business days", "$19.99"],
        ["Australia / NZ", "DHL Express", "5 - 9 business days", "$24.99"],
        ["Asia Pacific", "FedEx International Priority", "5 - 10 business days", "$29.99"],
        ["Rest of World", "DHL Worldwide", "7 - 14 business days", "$34.99"],
    ]
    intl_table = make_wrapped_table(intl_data, [3.8*cm, 4.5*cm, 4.5*cm, 3.8*cm])
    intl_table.setStyle(base_table_style())
    story.append(intl_table)
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Customs duties, import taxes, and brokerage fees are the sole responsibility of the "
        "recipient and are not included in TechMart's shipping charge. Duties are estimated "
        "at checkout where available.",
        body
    ))

    # Section 4: Tracking
    story.append(Paragraph("4. Shipment Tracking & Delivery Confirmation", h1))
    story.append(Paragraph(
        "A shipment confirmation email with carrier tracking number is sent automatically "
        "within 1 hour of dispatch. Track your order at: orders.techmart.com/track "
        "or directly on the carrier's website.",
        body
    ))
    track_items = [
        "Real-time GPS tracking is available for Priority Overnight and Saturday Express shipments.",
        "Delivery photo confirmation is provided for all FedEx and UPS residential deliveries.",
        "If a package is marked as delivered but not received, contact support@techmart.com "
        "within 72 hours. We will open a carrier claim on your behalf.",
    ]
    story.append(ListFlowable([ListItem(Paragraph(t, body)) for t in track_items], bulletType="bullet"))
    story.append(Spacer(1, 0.3*cm))

    # Section 5: Damaged/Lost Packages
    story.append(Paragraph("5. Damaged or Lost Shipments", h1))
    story.append(Paragraph(
        "All TechMart shipments are fully insured up to their retail value. "
        "If your order arrives damaged or is confirmed lost by the carrier:",
        body
    ))
    dmg_items = [
        "Contact support@techmart.com within 5 business days of the expected delivery date.",
        "Provide your order number, photos of damaged packaging/items (if applicable).",
        "TechMart will ship a free replacement within 2 business days or issue a full refund "
        "(your choice) once the carrier claim is filed.",
    ]
    story.append(ListFlowable([ListItem(Paragraph(d, body)) for d in dmg_items], bulletType="bullet"))

    doc.build(story)
    print(f"  [OK] {out.name} regenerated ({out.stat().st_size:,} bytes)")


# =====================================================================
# UserManual.pdf
# =====================================================================
def build_user_manual_pdf():
    out = KB_DIR / "UserManual.pdf"
    doc = SimpleDocTemplate(str(out), pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []

    story.append(Paragraph("TechMart Electronics — Comprehensive User Manual & Troubleshooting Reference", title_style))
    story.append(Paragraph("Official Corporate Policy & Reference Documentation | Doc ID: TM-UM-FULL-2026", subtitle_style))
    story.append(Spacer(1, 0.4*cm))

    # Section 1: LED Status Lights
    story.append(Paragraph("1. SmartHub Pro LED Status Light Meanings", h1))
    story.append(Paragraph(
        "The multi-color front LED indicator conveys the operational status of your SmartHub Pro gateway.",
        body
    ))

    led_data = [
        ["LED Color & Pattern", "System Status", "Recommended Action"],
        ["Solid Blue", "Normal Operation", "All systems connected and running smoothly."],
        ["Pulsing Amber", "Setup / Pairing Mode", "Open TechMart App to complete Wi-Fi setup."],
        ["Blinking Red (Fast)", "Network Disconnected", "Check router Wi-Fi signal or Ethernet connection."],
        ["Solid Red", "Hardware Fault / Overheat", "Power cycle device; allow 10 min to cool down."],
        ["Pulsing Purple", "Firmware Updating (OTA)", "Do NOT disconnect power during update."],
        ["Blinking White", "Bluetooth Pairing Mode", "Open TechMart App and tap 'Add New Device'."],
        ["Off (No Light)", "Device Powered Off / No Power", "Check power adapter connection and outlet."],
    ]
    led_table = make_wrapped_table(led_data, [4.5*cm, 4.5*cm, 7.6*cm])
    story.append(led_table)
    story.append(Spacer(1, 0.4*cm))

    # Section 2: Error Codes
    story.append(Paragraph("2. Common Error Codes & Troubleshooting Steps", h1))

    # 3-column layout: Error Code | Error Name & Cause | Resolution Steps
    # (4 columns overflow on A4; merging Description+Cause gives clean extraction)
    err_data = [
        ["Error Code", "Error Name & Cause", "Resolution Steps"],
        ["E-101",
         "Authentication Failure\nCause: Cloud account credentials mismatch.",
         "Re-enter your TechMart account password in the mobile app Settings > Account."],
        ["E-204",
         "Zigbee Signal Weak\nCause: Sensor too far from SmartHub.",
         "Move sensor within 10m of SmartHub or add a TechMart SmartPlug as a mesh repeater."],
        ["E-305",
         "HDMI Handshake Error (VisionStream)\nCause: HDCP version mismatch.",
         "Verify TV HDMI port supports HDCP 2.2/2.3. Replace HDMI cable. Try a different port."],
        ["E-409",
         "Bluetooth Audio Stutter (SoundWave)\nCause: Bluetooth congestion or stale pairing.",
         "Hold Bluetooth + Volume Down for 7 sec to clear paired list, then re-pair device."],
        ["E-512",
         "SD Card Write Failure\nCause: SD card full or corrupted.",
         "Format SD card (FAT32, max 256GB) in Settings > Storage > Format Card."],
        ["E-615",
         "Firmware Update Failed\nCause: Interrupted OTA update.",
         "Do not unplug during update. If stuck, hold reset button 15 sec to force re-download."],
    ]
    err_table = make_wrapped_table(err_data, [2.2*cm, 5.8*cm, 8.6*cm])
    story.append(err_table)
    story.append(Spacer(1, 0.4*cm))

    # Section 3: Factory Reset
    story.append(Paragraph("3. Factory Reset Procedures", h1))
    story.append(Paragraph(
        "If experiencing persistent operational anomalies, a factory reset returns the hardware "
        "to out-of-the-box defaults. All local settings, paired devices, and stored Wi-Fi "
        "credentials will be erased.",
        body
    ))

    # 3-column layout: Device | Factory Reset Method | Duration & Notes
    reset_data = [
        ["Device", "Factory Reset Method", "Duration & Notes"],
        ["SmartHub Pro",
         "Hold recessed RESET button (pin) for 15 seconds until LED flashes red 3 times.",
         "~90 sec. All paired devices must be re-added in TechMart App."],
        ["SoundWave 500",
         "Hold Volume Up + Power simultaneously for 10 seconds.",
         "~30 sec. All Bluetooth pairings cleared. Wi-Fi config remains if assigned via app."],
        ["VisionStream 4K",
         "Settings > System > Factory Reset in the on-screen menu.",
         "~2 min. Google/Amazon account must be re-signed in after reset."],
        ["SmartSensor Trio",
         "Hold tamper button on back for 5 seconds until LED flashes rapidly.",
         "~10 sec. Re-add sensor to SmartHub Pro after reset."],
    ]
    reset_table = make_wrapped_table(reset_data, [3.2*cm, 7.8*cm, 5.6*cm])
    story.append(reset_table)
    story.append(Spacer(1, 0.4*cm))

    # Section 4: Firmware Updates
    story.append(Paragraph("4. Firmware Updates & App Requirements", h1))
    story.append(Paragraph(
        "All TechMart devices receive automatic Over-The-Air (OTA) firmware updates when connected "
        "to Wi-Fi. Updates are released on the second Tuesday of each month.",
        body
    ))

    fw_data = [
        ["Device", "Current Firmware Version", "Minimum App Version", "Auto-Update"],
        ["SmartHub Pro", "v4.7.2 (2026-07)", "TechMart App v3.2+", "Yes"],
        ["SoundWave 500", "v2.3.1 (2026-06)", "TechMart App v3.0+", "Yes"],
        ["VisionStream 4K", "v6.1.0 (2026-07)", "Android 10+ / iOS 15+", "Yes"],
        ["SmartSensor Trio", "v1.9.4 (2026-05)", "TechMart App v2.8+", "Yes (via SmartHub)"],
        ["PowerPulse 65W", "N/A (no firmware)", "N/A", "N/A"],
    ]
    fw_table = make_wrapped_table(fw_data, [4*cm, 4*cm, 4*cm, 4.6*cm])
    story.append(fw_table)
    story.append(Spacer(1, 0.4*cm))

    # Section 5: Technical Support Channels & Contact Info
    story.append(Paragraph("5. Technical Support Channels & Contact Info", h1))
    sup_data = [
        ["Channel", "Availability", "Contact / Reference"],
        ["Live Chat", "Mon - Fri, 9 AM - 6 PM EST", "techmart.com/support"],
        ["Email Support", "24/7 (response within 24h)", "support@techmart.com"],
        ["Phone Support", "Mon - Fri, 9 AM - 6 PM EST", "1-800-TECHMART"],
        ["Community Forum", "24/7", "community.techmart.com"],
        ["Warranty Claims", "Mon - Fri, 9 AM - 5 PM EST", "warranty@techmart.com"],
    ]
    sup_table = make_wrapped_table(sup_data, [4.5*cm, 5*cm, 7.1*cm])
    story.append(sup_table)

    doc.build(story)
    print(f"  [OK] {out.name} regenerated ({out.stat().st_size:,} bytes)")


# =====================================================================
# Main
# =====================================================================
if __name__ == "__main__":
    KB_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\nRegenerating PDFs in: {KB_DIR}")
    print("-" * 60)
    build_pricing_pdf()
    build_shipping_pdf()
    build_user_manual_pdf()
    print("-" * 60)
    print("[SUCCESS] All 3 PDFs regenerated with proper table structure.")
