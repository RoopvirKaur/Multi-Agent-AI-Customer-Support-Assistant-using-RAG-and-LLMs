"""
generate_kb_documents.py
Generates 8 realistic PDF documents for TechMart Electronics in knowledge_base/
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "knowledge_base"


def build_pdf(filename: str, title: str, subtitle: str, sections: list):
    """
    Helper to generate a clean, professionally formatted PDF.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = OUTPUT_DIR / filename

    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    header_style = ParagraphStyle(
        "DocHeader",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e1b4b"),
        spaceAfter=4,
    )

    sub_style = ParagraphStyle(
        "DocSubHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#6366f1"),
        spaceAfter=12,
    )

    h2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#312e81"),
        spaceBefore=10,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "DocBullet",
        parent=body_style,
        leftIndent=15,
        bulletIndent=5,
        spaceAfter=4,
    )

    tbl_hdr_style = ParagraphStyle(
        "DocTblHdr",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1e1b4b"),
    )

    tbl_cell_style = ParagraphStyle(
        "DocTblCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.0,
        leading=11,
        textColor=colors.HexColor("#1f2937"),
    )

    story = []

    # Title & Subtitle Banner
    story.append(Paragraph(f"TechMart Electronics — {title}", header_style))
    story.append(Paragraph(f"Official Corporate Policy & Reference Documentation | {subtitle}", sub_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#4f46e5"), spaceAfter=14))

    for sec in sections:
        sec_title = sec.get("title")
        if sec_title:
            story.append(Paragraph(sec_title, h2_style))

        paragraphs = sec.get("paragraphs", [])
        for p in paragraphs:
            story.append(Paragraph(p, body_style))

        bullets = sec.get("bullets", [])
        for b in bullets:
            story.append(Paragraph(f"• &nbsp; {b}", bullet_style))

        table_data = sec.get("table")
        if table_data:
            raw_widths = sec.get("colWidths", [160, 370])
            total_w = sum(raw_widths)
            max_w = 530.0
            col_widths = [w * (max_w / total_w) for w in raw_widths] if total_w > max_w else raw_widths

            processed_table_data = []
            for r_idx, row in enumerate(table_data):
                processed_row = []
                for cell in row:
                    st = tbl_hdr_style if r_idx == 0 else tbl_cell_style
                    cell_str = str(cell).replace("\n", "<br/>")
                    processed_row.append(Paragraph(cell_str, st))
                processed_table_data.append(processed_row)

            tbl = Table(processed_table_data, colWidths=col_widths)
            tbl.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e0e7ff")),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("LEFTPADDING", (0, 0), (-1, -1), 4),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )
            story.append(Spacer(1, 4))
            story.append(tbl)
            story.append(Spacer(1, 6))

        story.append(Spacer(1, 8))

    doc.build(story)
    print(f"Generated: {filepath.name} ({os.path.getsize(filepath):,} bytes)")


def generate_all_documents():
    print("Generating 8 TechMart Electronics Knowledge Base PDFs...")

    # 1. FAQ.pdf
    build_pdf(
        "FAQ.pdf",
        "Frequently Asked Questions (FAQ)",
        "Doc ID: TM-FAQ-2026-V1",
        [
            {
                "title": "1. General & Account Management",
                "paragraphs": [
                    "Welcome to TechMart Electronics. Below are the most common inquiries regarding your account, online orders, and support access.",
                ],
                "bullets": [
                    "How do I reset my password? Navigate to the TechMart login screen, click 'Forgot Password', and enter your registered email. A 6-digit verification code will be sent immediately.",
                    "Can I change my account email? Yes, go to Account Settings > Security > Update Email Address. Email changes require re-authentication.",
                    "What are TechMart customer support hours? Our Multi-Agent AI system is active 24/7/365. Human specialist escalation is available Monday through Friday, 8:00 AM – 8:00 PM EST.",
                    "How do I track my active order? Once your order is processed, a tracking number from FedEx, UPS, or DHL is emailed to you and accessible under My Orders.",
                ],
            },
            {
                "title": "2. Payments, Billing & Subscriptions",
                "bullets": [
                    "What payment methods does TechMart accept? We accept Visa, MasterCard, American Express, PayPal, Apple Pay, Google Pay, and TechMart Store Credit.",
                    "When am I charged for backordered items? You are only charged when your item enters the fulfillment and shipping stage.",
                    "How does the SmartHub Pro Cloud subscription work? The cloud subscription offers unlimited 60-day camera backup and AI scene recognition at $9.99/month or $99/year.",
                    "Can I pause my subscription? Yes, subscriptions can be paused for up to 90 days from the Billing Portal.",
                ],
            },
            {
                "title": "3. Hardware & Smart Device Troubleshooting",
                "bullets": [
                    "What should I do if my SmartHub Pro loses Wi-Fi connection? Ensure your router operates on 2.4 GHz or 5 GHz. Press and hold the Reset button on the rear for 5 seconds until the LED pulses amber.",
                    "Is the SoundWave 500 speaker waterproof? The SoundWave 500 carries an IPX7 water resistance rating, tolerating submersion up to 1 meter for 30 minutes.",
                    "How many devices can pair simultaneously with VisionStream 4K? The VisionStream 4K supports up to 8 Bluetooth remotes and audio output channels simultaneously.",
                    "Where do I download device firmware updates? Firmware updates are delivered automatically Over-The-Air (OTA) when connected to Wi-Fi.",
                ],
            },
            {
                "title": "4. Returns, Exchanges & Warranty Quick Summary",
                "bullets": [
                    "What is the standard return window? Items purchased directly from TechMart can be returned within 30 days of delivery in original condition.",
                    "Are shipping fees refundable? Standard shipping fees are non-refundable unless the return is due to an error by TechMart or a defective product.",
                    "How do I file a warranty claim? Submit your serial number and proof of purchase via the TechMart Support Assistant or at support.techmart.com.",
                ],
            },
        ],
    )

    # 2. RefundPolicy.pdf
    build_pdf(
        "RefundPolicy.pdf",
        "Customer Refund & Return Policy",
        "Doc ID: TM-POL-REFUND-2026",
        [
            {
                "title": "1. 30-Day Return Guarantee",
                "paragraphs": [
                    "At TechMart Electronics, customer satisfaction is our highest priority. If you are not completely satisfied with your purchase, you may return eligible items within 30 calendar days of delivery for a full refund or exchange.",
                ],
                "bullets": [
                    "Items must be in original, undamaged condition with all accessories, cables, documentation, and packaging included.",
                    "Proof of purchase (Order ID or invoice receipt) is mandatory for all return requests.",
                    "Software licenses, downloaded digital media, and gift cards are strictly non-refundable.",
                    "Opened in-ear audio products (such as EarBuds Pro) are subject to health & hygiene return regulations and require inspection before refund clearance.",
                ],
            },
            {
                "title": "2. Refund Processing Timelines",
                "paragraphs": [
                    "Once returned merchandise is received at our fulfillment hub, our inspection team inspects the hardware within 48 to 72 business hours.",
                ],
                "table": [
                    ["Payment Method", "Refund Processing Time after Inspection"],
                    ["Credit / Debit Card (Visa, MC, Amex)", "3 to 5 business days (depends on issuing bank)"],
                    ["PayPal / Apple Pay / Google Pay", "1 to 2 business days"],
                    ["TechMart Store Credit", "Instant (immediately available on account)"],
                    ["Direct Bank Wire / ACH", "5 to 7 business days"],
                ],
            },
            {
                "title": "3. Restocking Fees & Return Shipping Costs",
                "paragraphs": [
                    "TechMart provides prepaid return labels for all items deemed defective on arrival (DOA) or shipped in error. For discretionary returns (e.g., buyer remorse or wrong color chosen):",
                ],
                "bullets": [
                    "A flat return shipping fee of $8.99 will be deducted from your final refund amount.",
                    "A 15% restocking fee applies to opened electronics missing original interior packaging or manuals.",
                    "Refurbished / Open-Box products carry a 14-day return window with no restocking fee.",
                ],
            },
            {
                "title": "4. Step-by-Step Return Instructions",
                "bullets": [
                    "Step 1: Contact TechMart AI Support or sign in to your dashboard under My Orders.",
                    "Step 2: Select the item to return and select the reason code.",
                    "Step 3: Download and print the generated Return Merchandise Authorization (RMA) label.",
                    "Step 4: Pack the device securely and drop off at any authorized FedEx / UPS depot.",
                ],
            },
        ],
    )

    # 3. ShippingPolicy.pdf
    build_pdf(
        "ShippingPolicy.pdf",
        "Shipping, Delivery & Fulfillment Policy",
        "Doc ID: TM-POL-SHIP-2026",
        [
            {
                "title": "1. Domestic Shipping Options (United States & Canada)",
                "paragraphs": [
                    "TechMart Electronics partners with FedEx, UPS, and DHL Express to ensure rapid, reliable delivery of all electronics, audio equipment, and smart home accessories.",
                ],
                "table": [
                    ["Shipping Tier", "Estimated Transit Time", "Cost (Orders < $50)", "Cost (Orders >= $50)"],
                    ["Standard Ground", "3 – 5 business days", "$5.99 flat rate", "FREE ($0.00)"],
                    ["Expedited 2-Day", "2 business days", "$12.99 flat rate", "$8.99 discounted"],
                    ["Priority Overnight", "Next business day by 3 PM", "$24.99 flat rate", "$19.99 flat rate"],
                    ["Saturday Express Delivery", "Saturday delivery", "$29.99 flat rate", "$29.99 flat rate"],
                ],
            },
            {
                "title": "2. Order Cut-Off Times & Order Processing",
                "paragraphs": [
                    "Orders placed before 2:00 PM EST Monday through Friday are processed and dispatched on the same business day. Orders placed after 2:00 PM EST or on weekends/holidays will ship on the following business day.",
                ],
                "bullets": [
                    "Signature Requirement: Orders exceeding $300 in value require an adult signature upon delivery.",
                    "P.O. Boxes & APO/FPO: Standard Ground via USPS is required for all P.O. Box and Military APO/FPO addresses (transit time 5 – 9 business days).",
                ],
            },
            {
                "title": "3. International Shipping Rates & Customs Duties",
                "paragraphs": [
                    "TechMart delivers to over 45 countries worldwide. International shipping rates are calculated at checkout based on package weight and destination country.",
                ],
                "bullets": [
                    "International Express (DHL): 3 to 7 business days worldwide.",
                    "Customs, Tariffs & Import Taxes: For DDP (Delivered Duty Paid) countries, duties are calculated and collected at checkout. For DDU countries, the recipient is responsible for customs clearance fees.",
                ],
            },
            {
                "title": "4. Damaged, Lost, or Stolen Packages",
                "bullets": [
                    "If your tracking states delivered but you cannot locate the parcel, please wait 24 hours (couriers occasionally scan early) and check surrounding entrances.",
                    "Claims for packages damaged in transit must be reported within 48 hours of delivery with photographic evidence.",
                    "All high-value packages include TechMart Transit Insurance at zero additional customer expense.",
                ],
            },
        ],
    )

    # 4. Warranty.pdf
    build_pdf(
        "Warranty.pdf",
        "Limited Hardware Warranty & TechMart Care+",
        "Doc ID: TM-WARR-2026",
        [
            {
                "title": "1. Standard One-Year Limited Manufacturer Warranty",
                "paragraphs": [
                    "TechMart Electronics warrants all brand-new hardware products against defects in materials and workmanship under normal operational use for a period of ONE (1) YEAR from the original retail purchase date.",
                ],
                "bullets": [
                    "Scope of Coverage: Covers internal motherboard failure, defective Wi-Fi/Bluetooth chips, factory display defects, power supply failure, and manufacturing defects.",
                    "Remedy: At TechMart's sole discretion, we will either (a) repair the product using new or refurbished OEM parts, (b) replace the product with an identical or functionally equivalent model, or (c) refund the original purchase price.",
                ],
            },
            {
                "title": "2. What is NOT Covered Under Standard Warranty (Exclusions)",
                "bullets": [
                    "Cosmetic damage including scratches, dents, cracked plastics, or broken ports caused by accidental drops.",
                    "Liquid damage or moisture ingress exceeding the product's certified IP rating.",
                    "Damage resulting from unauthorized repair, disassembly, third-party software rooting, or electrical power surges.",
                    "Consumable parts such as standard batteries, unless failure is attributable to manufacturing defect.",
                    "Products purchased from unauthorized third-party resellers or auction platforms.",
                ],
            },
            {
                "title": "3. TechMart Care+ Extended Protection Plan (Optional 2-Year Plan)",
                "paragraphs": [
                    "Customers can purchase TechMart Care+ within 30 days of hardware purchase for extended protection.",
                ],
                "table": [
                    ["Feature", "Standard 1-Year Warranty", "TechMart Care+ (2-Year Plan)"],
                    ["Hardware Defects Coverage", "1 Year", "2 Full Years"],
                    ["Accidental Damage Protection (Drops/Spills)", "Not Covered", "Covered ($29 incident fee)"],
                    ["Express Priority Replacement", "Standard RMA (7-10 days)", "Advanced Replacement (Next-Day)"],
                    ["Battery Capacity Coverage (< 80%)", "Not Covered", "Free OEM Battery Replacement"],
                    ["24/7 Dedicated Priority Support Line", "Standard Queue", "VIP Priority Routing"],
                ],
            },
            {
                "title": "4. How to File a Warranty Claim",
                "bullets": [
                    "Step 1: Locate your device Serial Number (printed on bottom label or under Settings > About).",
                    "Step 2: Start a conversation with TechMart AI Support or visit support.techmart.com/warranty.",
                    "Step 3: Provide a brief description of the defect and your original order number.",
                    "Step 4: Receive a prepaid shipping label and RMA number for inspection and swift repair/replacement.",
                ],
            },
        ],
    )

    # 5. Pricing.pdf
    build_pdf(
        "Pricing.pdf",
        "Hardware Pricing, Subscriptions & Volume Discounts",
        "Doc ID: TM-CAT-PRICING-2026",
        [
            {
                "title": "1. Hardware Product Lineup & Retail Pricing (2026 Catalog)",
                "paragraphs": [
                    "Official MSRP pricing for all TechMart flagship consumer electronics and smart home devices.",
                ],
                "table": [
                    ["Product Model", "SKU", "Retail Price (MSRP)", "TechMart Care+ Add-on"],
                    ["TechMart SmartHub Pro (Central IoT Controller)", "TM-SHP-01", "$199.99", "$39.99 / 2 yrs"],
                    ["TechMart SoundWave 500 (Hi-Res Audio Speaker)", "TM-SW500-02", "$149.99", "$29.99 / 2 yrs"],
                    ["TechMart VisionStream 4K (Ultra HD Media Box)", "TM-VS4K-03", "$129.99", "$24.99 / 2 yrs"],
                    ["TechMart SmartSensor Trio (Door/Window Pack)", "TM-SST-04", "$59.99", "$14.99 / 2 yrs"],
                    ["TechMart PowerPulse 65W GaN Charger", "TM-PP65-05", "$39.99", "N/A (1-yr standard)"],
                ],
            },
            {
                "title": "2. SmartHub Cloud Intelligence Subscription Tiers",
                "paragraphs": [
                    "Enhance your SmartHub Pro with cloud event storage, multi-camera AI recognition, and remote cellular backup.",
                ],
                "table": [
                    ["Tier", "Monthly Price", "Annual Price (Save 17%)", "Key Features"],
                    ["Basic (Free)", "$0.00", "$0.00", "Live 1080p streaming, local SD card recording, 24h clip buffer"],
                    ["Plus Plan", "$4.99 / mo", "$49.99 / yr", "30-day cloud recording (up to 3 devices), AI motion alerts"],
                    ["Pro Premium", "$9.99 / mo", "$99.99 / yr", "60-day cloud recording (unlimited devices), Person & Pet AI detection, 24/7 cellular backup"],
                ],
            },
            {
                "title": "3. Bundle Packages & Promotional Discounts",
                "bullets": [
                    "Home Security Essentials Bundle: SmartHub Pro + 2 SmartSensor Trios + 1-yr Plus Plan for $279.99 (Save $60).",
                    "Audiophile Home Theater Bundle: VisionStream 4K + 2 SoundWave 500 speakers for $379.99 (Save $50).",
                    "Student & Educator Discount: 10% off all hardware with valid .edu verification through SheerID.",
                    "Trade-In Credit: Upgrade any previous generation SmartHub for a $40 instant credit toward SmartHub Pro.",
                ],
            },
        ],
    )

    # 6. Products.pdf
    build_pdf(
        "Products.pdf",
        "Product Specifications & Technical Catalog",
        "Doc ID: TM-PROD-SPEC-2026",
        [
            {
                "title": "1. TechMart SmartHub Pro (IoT Automation Gateway)",
                "paragraphs": [
                    "The central brain for modern smart homes. Manages Zigbee 3.0, Z-Wave Plus, Thread, Matter, and dual-band Wi-Fi 6 devices with sub-10ms local automation execution.",
                ],
                "bullets": [
                    "Processor: Quad-Core ARM Cortex-A55 @ 2.0 GHz, 2GB LPDDR4 RAM, 16GB eMMC storage.",
                    "Connectivity: Wi-Fi 6 (802.11ax), Bluetooth 5.3 LE, Thread / Matter border router, Gigabit Ethernet.",
                    "Audio/Display: 3.5-inch OLED status display, built-in dual omnidirectional far-field microphones.",
                    "Power: 12V / 2A DC adapter with optional internal 2600mAh battery backup (up to 4 hours runtime).",
                    "Dimensions & Weight: 120mm x 120mm x 35mm, 320 grams.",
                ],
            },
            {
                "title": "2. TechMart SoundWave 500 (Wireless Hi-Res Smart Speaker)",
                "paragraphs": [
                    "Studio-grade acoustic fidelity engineered with dual custom neodymium woofers and high-efficiency silk dome tweeters.",
                ],
                "bullets": [
                    "Acoustic Output: 60W Total RMS output (80W Peak), Frequency Response: 42 Hz – 22 kHz.",
                    "Supported Codecs: LDAC, aptX HD, AAC, SBC, Apple AirPlay 2, Spotify Connect, and TIDAL Connect.",
                    "Battery & Ingress: 5200mAh Li-ion battery (up to 14 hours playback @ 60% volume), IPX7 waterproof.",
                    "Microphones: 4-mic beamforming array with noise cancellation for crystal clear voice commands.",
                ],
            },
            {
                "title": "3. TechMart VisionStream 4K (Cinematic HDR Media Hub)",
                "paragraphs": [
                    "Next-generation 4K HDR streaming device powered by TechMart OS with AV1 hardware decoding and Dolby Atmos passthrough.",
                ],
                "bullets": [
                    "Video Support: 4K UHD @ 60fps, Dolby Vision, HDR10+, HLG, AV1, VP9 Profile 2.",
                    "Audio Passthrough: Dolby Atmos, DTS:X, 7.1 TrueHD surround sound over HDMI 2.1 eARC.",
                    "Memory & Storage: 4GB RAM, 32GB High-Speed Storage for games and offline streaming apps.",
                    "Ports: HDMI 2.1, USB 3.0 Type-A (for external hard drives), USB-C Power, Optical SPDIF.",
                ],
            },
        ],
    )

    # 7. InstallationGuide.pdf
    build_pdf(
        "InstallationGuide.pdf",
        "Hardware Setup & Quick-Start Installation Guide",
        "Doc ID: TM-IG-QUICKSTART-2026",
        [
            {
                "title": "1. TechMart SmartHub Pro Setup Steps",
                "paragraphs": [
                    "Follow these step-by-step instructions to initialize your SmartHub Pro in under 5 minutes.",
                ],
                "bullets": [
                    "Step 1 (Placement): Place the SmartHub Pro in a central, elevated location in your home, at least 3 feet away from large metal objects or microwaves.",
                    "Step 2 (Power): Connect the included 12V power adapter. The OLED display will illuminate and show the TechMart logo.",
                    "Step 3 (App Pairing): Open the TechMart App on iOS/Android. Ensure Bluetooth is enabled on your phone and tap 'Add New Device (+)' in the top right corner.",
                    "Step 4 (Network Selection): Select your 2.4 GHz or 5 GHz Wi-Fi network and enter the passphrase. The front LED will turn Solid Blue when connected.",
                    "Step 5 (Matter/Zigbee Discovery): Put your smart accessories in pairing mode; the SmartHub Pro will automatically detect and bind them.",
                ],
            },
            {
                "title": "2. TechMart SoundWave 500 Bluetooth & Wi-Fi Pairing",
                "bullets": [
                    "Bluetooth Mode: Power on the speaker. Press and hold the Bluetooth button for 3 seconds until the blue LED flashes rapidly. Select 'SoundWave 500' on your mobile device.",
                    "Stereo Pair Mode: To link two SoundWave 500 speakers for true Left/Right stereo audio, double-tap the 'Link' button on both units simultaneously within 10 seconds.",
                    "Auxiliary Input: Plug a 3.5mm audio cable into the AUX port; the speaker switches to Aux mode automatically.",
                ],
            },
            {
                "title": "3. TechMart VisionStream 4K TV Connection",
                "bullets": [
                    "Step 1: Plug the HDMI 2.1 cable into the HDMI 1 / eARC port of your 4K television.",
                    "Step 2: Connect the USB-C power supply directly into a wall outlet (avoid low-power TV USB ports).",
                    "Step 3: Switch TV source to the corresponding HDMI input and follow on-screen remote pairing (hold Home + Back for 5 seconds).",
                ],
            },
        ],
    )

    # 8. UserManual.pdf
    build_pdf(
        "UserManual.pdf",
        "Comprehensive User Manual & Troubleshooting Reference",
        "Doc ID: TM-UM-FULL-2026",
        [
            {
                "title": "1. SmartHub Pro LED Status Light Meanings",
                "paragraphs": [
                    "The multi-color front LED indicator conveys the operational status of your SmartHub Pro gateway.",
                ],
                "table": [
                    ["LED Color & Pattern", "System Status", "Recommended Action"],
                    ["Solid Blue", "Normal Operation", "All systems connected and running smoothly."],
                    ["Pulsing Amber", "Setup / Pairing Mode", "Open TechMart App to complete Wi-Fi setup."],
                    ["Blinking Red (Fast)", "Network Disconnected", "Check router Wi-Fi signal or Ethernet connection."],
                    ["Solid Red", "Hardware Fault / Overheat", "Power cycle device; allow 10 min to cool down."],
                    ["Pulsing Purple", "Firmware Updating (OTA)", "Do NOT disconnect power during update."],
                ],
            },
            {
                "title": "2. Common Error Codes & Troubleshooting Steps",
                "bullets": [
                    "Error E-101 (Authentication Failure): Re-enter your TechMart cloud account password in the mobile app settings.",
                    "Error E-204 (Zigbee Signal Weak): Move distant sensors closer to SmartHub or add a TechMart SmartPlug to serve as a mesh repeater.",
                    "Error E-305 (HDMI Handshake Error on VisionStream): Verify that your TV HDMI port supports HDCP 2.2 / 2.3 and change the HDMI cable if necessary.",
                    "Error E-409 (Bluetooth Audio Stutter on SoundWave): Clear paired devices list by holding Bluetooth + Volume Down for 7 seconds, then re-pair.",
                ],
            },
            {
                "title": "3. Factory Reset Procedures",
                "paragraphs": [
                    "If experiencing persistent operational anomalies, a factory reset returns the hardware to out-of-the-box defaults.",
                ],
                "bullets": [
                    "SmartHub Pro Reset: Locate the recessed pinhole on the rear panel. Insert a paperclip and hold for 10 seconds until the OLED screen displays 'Factory Resetting'.",
                    "SoundWave 500 Reset: While powered ON, press and hold the Power button and Play/Pause button simultaneously for 8 seconds until the chime sounds.",
                    "VisionStream 4K Reset: Navigate to Settings > System > Advanced Options > Factory Reset and confirm with PIN.",
                ],
            },
            {
                "title": "4. Customer Support Contact & Escalation",
                "bullets": [
                    "Live Multi-Agent Chat: Available 24/7 in-app or at https://support.techmart.com",
                    "Toll-Free Phone: 1-800-555-TMART (Mon–Fri, 8 AM – 8 PM EST)",
                    "Email Support: support@techmart-electronics.com",
                    "Corporate Headquarters: TechMart Electronics Inc., 100 Innovation Way, Suite 400, Austin, TX 78701",
                ],
            },
        ],
    )

    print("All 8 PDFs created successfully.")


if __name__ == "__main__":
    generate_all_documents()
