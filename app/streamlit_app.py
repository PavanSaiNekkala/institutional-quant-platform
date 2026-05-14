if completed % 10 == 0:

    completion_pct = round((completed / total) * 100, 1)

    status_html = f"""
    <div style="
        background: linear-gradient(135deg,#ffffff,#f8fafc);
        border-radius:22px;
        padding:28px;
        box-shadow:0 6px 24px rgba(0,0,0,0.08);
        border:1px solid #E5E7EB;
        margin-top:10px;
    ">

        <!-- HEADER -->

        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            margin-bottom:20px;
        ">

            <div>

                <div style="
                    font-size:34px;
                    font-weight:800;
                    color:#111827;
                ">
                📊 Institutional Processing Engine
                </div>

                <div style="
                    color:#6B7280;
                    font-size:15px;
                    margin-top:4px;
                ">
                Real-Time Institutional Quant Processing
                </div>

            </div>

            <div style="
                background:#EEF2FF;
                color:#2563EB;
                padding:10px 16px;
                border-radius:12px;
                font-weight:700;
                font-size:15px;
            ">
            LIVE
            </div>

        </div>

        <!-- KPI CARDS -->

        <div style="
            display:grid;
            grid-template-columns:repeat(4,1fr);
            gap:18px;
            margin-top:20px;
        ">

            <!-- COMPLETED -->

            <div style="
                background:#ECFDF5;
                border-radius:18px;
                padding:22px;
                border-left:6px solid #10B981;
            ">

                <div style="
                    color:#047857;
                    font-size:15px;
                    font-weight:700;
                ">
                ✅ Completed
                </div>

                <div style="
                    font-size:34px;
                    font-weight:800;
                    color:#065F46;
                    margin-top:8px;
                ">
                {completed}
                </div>

                <div style="
                    margin-top:6px;
                    color:#059669;
                    font-size:14px;
                ">
                out of {total}
                </div>

            </div>

            <!-- FAILED -->

            <div style="
                background:#FEF2F2;
                border-radius:18px;
                padding:22px;
                border-left:6px solid #DC2626;
            ">

                <div style="
                    color:#B91C1C;
                    font-size:15px;
                    font-weight:700;
                ">
                ❌ Failed
                </div>

                <div style="
                    font-size:34px;
                    font-weight:800;
                    color:#991B1B;
                    margin-top:8px;
                ">
                {len(set(failed_stocks))}
                </div>

                <div style="
                    margin-top:6px;
                    color:#DC2626;
                    font-size:14px;
                ">
                download failures
                </div>

            </div>

            <!-- UNIVERSE -->

            <div style="
                background:#EFF6FF;
                border-radius:18px;
                padding:22px;
                border-left:6px solid #2563EB;
            ">

                <div style="
                    color:#1D4ED8;
                    font-size:15px;
                    font-weight:700;
                ">
                🌐 Universe
                </div>

                <div style="
                    font-size:34px;
                    font-weight:800;
                    color:#1E3A8A;
                    margin-top:8px;
                ">
                {total}
                </div>

                <div style="
                    margin-top:6px;
                    color:#2563EB;
                    font-size:14px;
                ">
                NSE listed stocks
                </div>

            </div>

            <!-- ETA -->

            <div style="
                background:#FFF7ED;
                border-radius:18px;
                padding:22px;
                border-left:6px solid #F59E0B;
            ">

                <div style="
                    color:#D97706;
                    font-size:15px;
                    font-weight:700;
                ">
                ⏳ ETA
                </div>

                <div style="
                    font-size:34px;
                    font-weight:800;
                    color:#92400E;
                    margin-top:8px;
                ">
                {remaining_minutes}m
                </div>

                <div style="
                    margin-top:6px;
                    color:#F59E0B;
                    font-size:14px;
                ">
                estimated remaining
                </div>

            </div>

        </div>

        <!-- PROGRESS -->

        <div style="
            margin-top:26px;
        ">

            <div style="
                display:flex;
                justify-content:space-between;
                margin-bottom:8px;
            ">

                <span style="
                    color:#374151;
                    font-weight:700;
                    font-size:15px;
                ">
                Processing Progress
                </span>

                <span style="
                    color:#2563EB;
                    font-weight:800;
                    font-size:15px;
                ">
                {completion_pct}%
                </span>

            </div>

            <div style="
                width:100%;
                background:#E5E7EB;
                height:16px;
                border-radius:999px;
                overflow:hidden;
            ">

                <div style="
                    width:{completion_pct}%;
                    background:linear-gradient(90deg,#2563EB,#10B981);
                    height:100%;
                    border-radius:999px;
                "></div>

            </div>

        </div>

        <!-- CURRENT STOCK -->

        <div style="
            margin-top:26px;
            background:#111827;
            color:white;
            border-radius:16px;
            padding:18px;
            display:flex;
            justify-content:space-between;
            align-items:center;
        ">

            <div>

                <div style="
                    font-size:13px;
                    color:#9CA3AF;
                    margin-bottom:4px;
                ">
                CURRENTLY ANALYZING
                </div>

                <div style="
                    font-size:24px;
                    font-weight:800;
                ">
                {symbol}
                </div>

            </div>

            <div style="
                background:#10B981;
                padding:10px 16px;
                border-radius:12px;
                font-weight:700;
            ">
            ACTIVE
            </div>

        </div>

    </div>
    """

    status_box.markdown(
        status_html,
        unsafe_allow_html=True
    )
