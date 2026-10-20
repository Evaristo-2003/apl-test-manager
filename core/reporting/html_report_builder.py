#!/usr/bin/env python3

import base64
import json
from datetime import datetime
from core.state.app_state import app_state
import re
from pathlib import Path

from core.utils.resource_path import resource_path
class HtmlReportBuilder:
    @staticmethod
    def render_pwm_table(
        rows
    ):

        html = """
<div class="subsequence-title">
PWM Configuration
</div>

<div class="subsequence-content">

<table class="detail-table">

<tr>
<th>Command</th>
<th>Result</th>
</tr>
"""

        for row in rows:

            css_result = (
                "pass"
                if row["result"] == "PASS"
                else "fail"
            )

            html += f"""
<tr>

<td>
{row["command"]}
</td>

<td class="{css_result}">
{row["result"]}
</td>

</tr>
"""

        html += """
</table>

</div>

<br>
"""

        return html
    def render_gpio_table(
        rows
    ):

        html = """
<div class="subsequence-title">
GPIO Verification
</div>

<div class="subsequence-content">

<table class="detail-table">

<tr>
<th>Pattern</th>
<th>Expected</th>
<th>Actual</th>
<th>Result</th>
</tr>
"""

        for row in rows:

            css_result = (
                "pass"
                if row["result"] == "PASS"
                else "fail"
            )

            html += f"""
<tr>

<td>
{row["pattern"]}
</td>

<td>
{row["expected"]}
</td>

<td>
{row["actual"]}
</td>

<td class="{css_result}">
{row["result"]}
</td>

</tr>
"""

        html += """
</table>

</div>

<br>
"""

        return html
    def render_i2s_table(
        rows
    ):

        html = (
            HtmlReportBuilder
            .render_subsequence_table(
                "I2S Verification",
                rows
            )
        )

        return html
    def render_spi_table(
        rows
    ):

        html = """
<div class="subsequence-title">
SPI Device Verification
</div>

<div class="subsequence-content">

<table class="detail-table">

<tr>
<th>Device</th>
<th>Expected Device ID</th>
<th>Actual Device ID</th>
<th>Result</th>
</tr>
"""

        for row in rows:

            css_result = (
                "pass"
                if row["result"] == "PASS"
                else "fail"
            )

            html += f"""
<tr>

<td>
{row["device"]}
</td>

<td>
{row["expected"]}
</td>

<td>
{row["actual"]}
</td>

<td class="{css_result}">
{row["result"]}
</td>

</tr>
"""

        html += """
</table>

</div>

<br>
"""

        return html
    
    def render_i2c_table(
        rows
    ):

        html = """
<div class="subsequence-title">
I2C Temperature Sensors
</div>

<div class="subsequence-content">

<table class="detail-table">

<tr>
<th>Sensor</th>
<th>Low Limit</th>
<th>Actual °C</th>
<th>High Limit</th>
<th>Result</th>
</tr>
"""

        for row in rows:

            css_result = (
                "pass"
                if row["result"] == "PASS"
                else "fail"
            )

            html += f"""
<tr>

<td>
{row["sensor"]}
</td>

<td>
{row["low"]}
</td>

<td>
{row["actual"]}
</td>

<td>
{row["high"]}
</td>

<td class="{css_result}">
{row["result"]}
</td>

</tr>
"""

        html += """
</table>

</div>

<br>
"""

        return html
    def render_mmc_info_table(
        title,
        data
    ):

        html = f"""
<div class="subsequence-title">
{title}
</div>


<div class="subsequence-content">

<table class="detail-table">

<tr>
<th>Parameter</th>
<th>Value</th>
</tr>
"""

        for key, value in data.items():

            friendly_name = (
                key
                .replace("_", " ")
                .title()
            )

            html += f"""
<tr>

<td>
{friendly_name}
</td>

<td>
{value}
</td>

</tr>
"""

        html += """
</table>

</div>

<br>
"""

        return html
    def render_cpu_info_table(
        data
    ):

        html = """
<div class="subsequence-title">
CPU Information
</div>

<div class="subsequence-content">

<table class="detail-table">

<tr>
<th>Parameter</th>
<th>Value</th>
</tr>
"""

        for key, value in data.items():

            friendly_name = (
                key
                .replace("_", " ")
                .title()
            )

            html += f"""
<tr>

<td>
{friendly_name}
</td>

<td>
{value}
</td>

</tr>
"""

        html += """
</table>

</div>

<br>
"""

        return html
    def render_expected_actual_table(
        title,
        expected,
        actual,
        result,
        css
    ):

        html = f"""
<div class="subsequence-title">
{title}
</div>

<div class="subsequence-content">

<table class="detail-table">

<tr>
<th>Expected</th>
<th>Actual</th>
<th>Result</th>
</tr>

<tr>

<td>
{expected}
</td>

<td>
{actual}
</td>

<td class="{css}">
{result}
</td>

</tr>

</table>

</div>

<br>
"""

        return html
    def render_measurement_table(
        title,
        rows
    ):

        html = f"""
<div class="subsequence-title">
{title}
</div>

<div class="subsequence-content">

<table class="detail-table">

<tr>
<th>Measurement</th>
<th>Low Limit</th>
<th>Actual</th>
<th>High Limit</th>
<th>Result</th>
</tr>
"""

        for row in rows:

            html += f"""
<tr>

<td>
{row.get("name", "")}
</td>

<td>
{row.get("low", "")}
</td>

<td>
{row.get("actual", "")}
</td>

<td>
{row.get("high", "")}
</td>

<td class="{row.get('css', '')}">
{row.get("result", "")}
</td>

</tr>
"""

        html += """
</table>

</div>

<br>
"""

        return html
    def render_ports(
        ports
    ):

        html = ""

        for port in ports:

            html += HtmlReportBuilder.render_subsequence_table(
                port.get(
                    "port",
                    ""
                ),
                port.get(
                    "rows",
                    []
                )
            )

        return html
    @staticmethod
    @staticmethod
    def get_logo_base64(
        logo_path
    ):

        try:

            with open(
                logo_path,
                "rb"
            ) as f:

                return (
                    base64
                    .b64encode(
                        f.read()
                    )
                    .decode()
                )

        except Exception:

            return ""
    def render_subsequence_table(
        title,
        rows
    ):

        html = f"""
<div class="subsequence-title">
{title}
</div>

<div class="subsequence-content">

<table class="detail-table">

<tr>
<th>Item</th>
<th>Low Limit</th>
<th>Actual</th>
<th>High Limit</th>
<th>Result</th>
</tr>
"""

        for row in rows:

            css_result = (
                "pass"
                if row.get(
                    "result"
                ) == "PASS"
                else
                "fail"
                if row.get(
                    "result"
                ) == "FAIL"
                else
                "skipped"
            )

            html += f"""
<tr>

<td>
{row.get("name", "")}
</td>

<td>
{row.get("low", "")}
</td>

<td>
{row.get("actual", "")}
</td>

<td>
{row.get("high", "")}
</td>

<td class="{css_result}">
{row.get("result", "")}
</td>

</tr>
"""

        html += """
</table>

</div>

<br>
"""

        return html
    @staticmethod
    def begin_subsequence(title):

        return f"""
    <div class="subsequence-title">
    {title}
    </div>

    <div class="subsequence-content">
    """

    @staticmethod
    def end_subsequence():

        return """
    </div>
    """
    @staticmethod
    def build(
        results: dict,
        sfc: str = "",
        operation: str = "",
        project: str = ""
    ) -> str:

        passed = 0
        failed = 0
        skipped = 0

        for result in results.values():

            status = getattr(
                result,
                "status",
                "UNKNOWN"
            )

            verification = (
                result.verification
                if hasattr(
                    result,
                    "verification"
                )
                else {}
            )

            if (
                status == "UNKNOWN"
                and
                "No hay límites definidos"
                in verification.get(
                    "message",
                    ""
                )
            ):
                skipped += 1

            elif status == "PASS":
                passed += 1

            elif status == "FAIL":
                failed += 1

        total = len(results)

        #
        # Logo del proyecto
        #
        logo_name = ""

        if "STELLANTIS" in project.upper():

            logo_name = "stellantis.png"

        elif "GM" in project.upper():

            logo_name = "gm.png"

        logo_html = ""

        if logo_name:

            logo_path = resource_path(
                f"assets/{logo_name}"
            )

            print(
                f"LOGO PATH = {logo_path}"
            )

            print(
                f"EXISTS = {logo_path.exists()}"
            )

            logo_b64 = (
                HtmlReportBuilder
                .get_logo_base64(
                    logo_path
                )
            )

            print(
                f"LOGO B64 LEN = {len(logo_b64)}"
            )

            if logo_b64:

                logo_html = f"""
<img
    src="data:image/png;base64,{logo_b64}"
    style="
        max-width:180px;
        max-height:70px;
    "
>
"""


        html = f"""
<!DOCTYPE html>
<html>

<head>

<meta charset="utf-8">

<title> TEST REPORT</title>

<style>
.subsequence-title {{
    margin-top: 15px;
    margin-left: 20px;

    background: #F4F7F9;

    padding: 6px 10px;

    border-left: 5px solid #5B9BD5;

    font-weight: bold;

    color: #1F2937;
}}
.test-summary {{
    background: #F4F7F9;
    border-left: 5px solid #5B9BD5;
    padding: 8px 12px;
    margin-top: 5px;
    margin-bottom: 10px;
    font-size: 13px;
}}
.subsequence-content {{
    margin-left: 25px;
}}
body {{
    font-family: Segoe UI, Arial, sans-serif;
    margin: 20px;
    background: white;
}}

h1 {{
    border-bottom: 2px solid #404040;
    padding-bottom: 10px;
}}

.summary-table {{
    border-collapse: collapse;
    width: 700px;
}}

.summary-table td,
.summary-table th {{
    border: 1px solid #CFCFCF;
    padding: 8px;
}}

.summary-table th {{
    background: #E9EEF2;
}}

.test-block {{
    margin-top: 25px;
}}

.test-title {{
    background: #BFD5E1;
    padding: 8px;
    font-weight: bold;
    border: 1px solid #A9BEC8;
    font-size: 14px;
}}

.info-table {{
    border-collapse: collapse;
    width: 100%;
}}
.adc-summary {{
    background: #F4F7F9;
    border-left: 5px solid #5B9BD5;
    padding: 8px 12px;
    margin-bottom: 10px;
    font-size: 13px;
}}
.info-table td {{
    border: 1px solid #D0D0D0;
    padding: 6px;
}}

.label {{
    width: 250px;
    font-weight: bold;
    background: #EFEFEF;
}}

.pass {{
    background: #C6EFCE;
    color: #006100;
    font-weight: bold;
}}

.fail {{
    background: #FFC7CE;
    color: #9C0006;
    font-weight: bold;
}}

.skipped {{
    background: #E7E6E6;
    color: #404040;
    font-weight: bold;
}}

.section-title {{
    background: #DDEAF2;
    padding: 6px;
    margin-top: 10px;
    margin-bottom: 4px;
    border: 1px solid #C4D2DA;
    font-weight: bold;
}}

.detail-table {{
    border-collapse: collapse;
    width: 100%;
}}

.detail-table td {{
    border: 1px solid #D0D0D0;
    padding: 6px;
}}
.detail-table th {{
    border: 1px solid #D0D0D0;
    padding: 6px;
    background: #E9EEF2;
    font-weight: bold;
    text-align: center;
}}
.detail-label {{
    width: 250px;
    background: #EFEFEF;
    font-weight: bold;
}}
.header-container {{

    display: flex;

    justify-content: space-between;

    align-items: center;

    margin-bottom: 25px;

    border-bottom: 2px solid #404040;

    padding-bottom: 10px;
}}

.header-info {{

    flex: 1;
}}

.header-title {{

    font-size: 28px;

    font-weight: bold;

    color: #1F2937;

    margin-bottom: 10px;
}}

.header-project {{

    font-size: 18px;

    font-weight: 600;

    color: #404040;

    margin-bottom: 6px;
}}

.header-logo {{

    width: 220px;

    text-align: right;
}}
.raw-box {{
    background: #F7F7F7;
    border: 1px solid #D5D5D5;
    padding: 8px;
    overflow-x: auto;
    white-space: pre-wrap;
    font-family: Consolas;
    font-size: 12px;
}}

</style>

</head>

<body>

<div class="header-container">

    <div class="header-info">

        <div class="header-title">
            TEST MANAGER REPORT
        </div>

        <div class="header-project">
            Project: {project}
        </div>

    </div>

    <div class="header-logo">

        {logo_html}

    </div>

</div>

<table class="summary-table">

<tr>
<th colspan="2">
Traceability
</th>
</tr>

<tr>
<td>SFC</td>
<td>{sfc}</td>
</tr>

<tr>
<td>Operation</td>
<td>{operation}</td>
</tr>

<tr>
<td>Date</td>
<td>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</td>
</tr>

</table>

<br>

<table class="summary-table">

<tr>
<th>Total</th>
<th>PASS</th>
<th>FAIL</th>
<th>SKIPPED</th>
</tr>

<tr>
<td>{total}</td>
<td>{passed}</td>
<td>{failed}</td>
<td>{skipped}</td>
</tr>

</table>
"""

        for name, result in results.items():

            status = getattr(
                result,
                "status",
                "UNKNOWN"
            )

            verification = (
                result.verification
                if hasattr(
                    result,
                    "verification"
                )
                else {}
            )

            parsed_data = (
                result.parsed_data
                if hasattr(
                    result,
                    "parsed_data"
                )
                else {}
            )

            display_status = status
            css = "pass"

            if (
                status == "UNKNOWN"
                and
                "No hay límites definidos"
                in verification.get(
                    "message",
                    ""
                )
            ):
                display_status = "SKIPPED"
                css = "skipped"

            elif status == "FAIL":
                css = "fail"

            elif status == "PASS":
                css = "pass"

            html += f"""

<div class="test-block">

<div class="test-title">
{name}
</div>

<div class="test-summary">

<b>Status:</b> <span class="{css}">{display_status}</span>

&nbsp;&nbsp;|&nbsp;&nbsp;

<b>Board:</b> {getattr(result, "board_type", "")}

&nbsp;&nbsp;|&nbsp;&nbsp;

<b>Duration:</b> {getattr(result, "duration_ms", 0):.0f} ms

</div>
"""
            #
            # Verification
            #

            details = (
                verification.get(
                    "details",
                    {}
                )
                if verification
                else {}
            )

            show_message = True

            if (
                (
                    "temperature" in details
                    and
                    "humidity" in details
                )
                or
                (
                    "voltage" in details
                    and
                    "current" in details
                )
                or
                (
                    "expected" in details
                    and
                    "actual" in details
                    and
                    len(details) == 2
                )
                or
                (
                    "value" in details
                    and
                    "low" in details
                    and
                    "high" in details
                )
                or
                (
                    "temp" in details
                    and
                    "low" in details
                    and
                    "high" in details
                )
                or
                (
                    "score" in details
                    and
                    "low" in details
                    and
                    "high" in details
                )
                or
                (
                    name == "LPC"
                )
                or
                (
                    name in [
                        "PCIe Iperf Test",
                        "USB3_3 Iperf Test",
                        "USB3_2 Iperf Test",
                        "USB2 Iperf Test"
                    ]
                )
                or
                (
                    name in [
                        "PCIe number of port",
                        "USB3_3 number of port",
                        "USB2 number of port",
                        "USB3_2 number of port"
                    ]
                )
                or
                (
                    name == "AB Erase DID"
                )
                or
                (
                    name in [
                        "USB3 to USB2",
                        "USB2 to USB3"
                    ]
                )
                or
                (
                    isinstance(
                        parsed_data,
                        dict
                    )
                    and
                    "bus_width"
                    in parsed_data.get(
                        "data",
                        {}
                    )
                    and
                    "clock"
                    in parsed_data.get(
                        "data",
                        {}
                    )
                )
            ):

                show_message = False

            show_verification_section = False

            if verification:

                has_ports_renderer = (
                    "ports" in details
                )

            show_verification_section = False

            is_iperf_test = (
                name in [
                    "PCIe Iperf Test",
                    "USB3_3 Iperf Test",
                    "USB3_2 Iperf Test",
                    "USB2 Iperf Test"
                ]
            )

            is_configuration_test = (
                name in [
                    "USB3 to USB2",
                    "USB2 to USB3"
                ]
            )

            is_number_of_port_test = (
                name in [
                    "PCIe number of port",
                    "USB3_3 number of port",
                    "USB2 number of port",
                    "USB3_2 number of port"
                ]
            )

            if verification:

                has_ports_renderer = (
                    "ports" in details
                )

                if (
                    not is_iperf_test
                    and
                    not is_number_of_port_test
                    and
                    not has_ports_renderer
                    and
                    (
                        show_message
                        or
                        len(details) > 0
                    )
                ):

                    show_verification_section = True

                html += """
<div class="section-title">
Verification
</div>

<table class="detail-table">
"""

                if show_message:

                    html += f"""
<tr>
<td class="detail-label">
Message
</td>

<td>
{verification.get("message", "")}
</td>
</tr>
"""

                html += """
</table>
"""

                details = verification.get(
                    "details",
                    {}
                )

                #
                # PCB ID Renderer
                #
                if (
                    "expected" in details
                    and
                    "actual" in details
                    and
                    len(details) == 2
                ):

                    html += (
                        HtmlReportBuilder
                        .render_expected_actual_table(
                            "PCB Verification",
                            details.get(
                                "expected",
                                ""
                            ),
                            details.get(
                                "actual",
                                ""
                            ),
                            display_status,
                            css
                        )
                    )
                #
                # Generic Value Renderer
                #
                elif (
                    "value" in details
                    and
                    "low" in details
                    and
                    "high" in details
                ):

                    rows = [

                        {
                            "name": (
                                details.get(
                                    "sapme_key",
                                    "Value"
                                )
                                .replace(
                                    "CHECK ",
                                    ""
                                )
                                .title()
                            ),
                            "low": details.get(
                                "low",
                                ""
                            ),
                            "actual": details.get(
                                "value",
                                ""
                            ),
                            "high": details.get(
                                "high",
                                ""
                            ),
                            "result": display_status,
                            "css": css
                        }

                    ]

                    html += (
                        HtmlReportBuilder
                        .render_measurement_table(
                            "Measurement Verification",
                            rows
                        )
                    )

                #
                # DDR Renderer
                #
                elif (
                    "score" in details
                    and
                    "low" in details
                    and
                    "high" in details
                ):

                    rows = [

                        {
                            "name": details.get(
                                "sapme_key",
                                "DDR VALUE"
                            ),
                            "low": details.get(
                                "low",
                                ""
                            ),
                            "actual": details.get(
                                "score",
                                ""
                            ),
                            "high": details.get(
                                "high",
                                ""
                            ),
                            "result": display_status,
                            "css": css
                        }

                    ]

                    html += (
                        HtmlReportBuilder
                        .render_measurement_table(
                            "DDR Verification",
                            rows
                        )
                    )

                #
                # SMBus Renderer
                #
                elif (
                    "temp" in details
                    and
                    "low" in details
                    and
                    "high" in details
                ):

                    rows = [

                        {
                            "name":
                                "Temperature",

                            "low":
                                details.get(
                                    "low",
                                    ""
                                ),

                            "actual":
                                details.get(
                                    "temp",
                                    ""
                                ),

                            "high":
                                details.get(
                                    "high",
                                    ""
                                ),

                            "result":
                                display_status,

                            "css":
                                css
                        }

                    ]

                    html += (
                        HtmlReportBuilder
                        .render_measurement_table(
                            "SMBus Verification",
                            rows
                        )
                    )
                #
                # CPU INFO Renderer
                #
                elif (
                    isinstance(parsed_data, dict)
                    and
                    "data" in parsed_data
                    and
                    isinstance(
                        parsed_data["data"],
                        dict
                    )
                    and
                    "vendor_id" in parsed_data["data"]
                ):

                    html += (
                        HtmlReportBuilder
                        .render_cpu_info_table(
                            parsed_data["data"]
                        )
                    )
                #
                # SDIO / EMMC Renderer
                #
                elif (
                    isinstance(parsed_data, dict)
                    and
                    "data" in parsed_data
                    and
                    isinstance(
                        parsed_data["data"],
                        dict
                    )
                    and
                    "bus_width"
                    in parsed_data["data"]
                    and
                    "clock"
                    in parsed_data["data"]
                ):

                    mmc_title = (
                        "MMC Information"
                    )

                    if (
                        "SDIO"
                        in
                        name.upper()
                    ):

                        mmc_title = (
                            "SDIO Information"
                        )

                    elif (
                        "EMMC"
                        in
                        name.upper()
                    ):

                        mmc_title = (
                            "EMMC Information"
                        )

                    html += (
                        HtmlReportBuilder
                        .render_mmc_info_table(
                            mmc_title,
                            parsed_data[
                                "data"
                            ]
                        )
                    )


                #
                # Thermal Renderer
                #
                if (
                    "temperature" in details
                    and
                    "humidity" in details
                ):

                    rows = [

                        {
                            "name": "Temperature",
                            "low": "",
                            "actual": f"{details['temperature']} °C",
                            "high": "",
                            "result": display_status,
                            "css": css
                        },

                        {
                            "name": "Humidity",
                            "low": "",
                            "actual": f"{details['humidity']} %",
                            "high": "",
                            "result": display_status,
                            "css": css
                        }

                    ]

                    html += (
                        HtmlReportBuilder
                        .render_measurement_table(
                            "Thermal Measurements",
                            rows
                        )
                    )
                #
                # Current / Voltage Renderer
                #
                elif (
                    "voltage" in details
                    and
                    "current" in details
                ):

                    rows = [

                        {
                            "name": "Voltage",
                            "low": details.get(
                                "voltage_low",
                                ""
                            ),
                            "actual": details.get(
                                "voltage",
                                ""
                            ),
                            "high": details.get(
                                "voltage_high",
                                ""
                            ),
                            "result": display_status,
                            "css": css
                        },

                        {
                            "name": "Current",
                            "low": details.get(
                                "current_low",
                                ""
                            ),
                            "actual": details.get(
                                "current",
                                ""
                            ),
                            "high": details.get(
                                "current_high",
                                ""
                            ),
                            "result": display_status,
                            "css": css
                        }

                    ]

                    html += (
                        HtmlReportBuilder
                        .render_measurement_table(
                            "Current / Voltage Measurements",
                            rows
                        )
                    )
                #
                # Ports Renderer (USB / PCIe)
                #
                ports = details.get(
                    "ports",
                    []
                )

                if ports:

                    html += """
<div class="section-title">
Measured Data
</div>
"""

                    html += (
                        HtmlReportBuilder.render_ports(
                            ports
                        )
                    )

                #
                # Expected / Actual
                #

                show_expected_actual = True

                if (
                    "expected" in details
                    and
                    "actual" in details
                    and
                    len(details) == 2
                ):

                    show_expected_actual = False

                if (
                    show_expected_actual
                    and
                    "expected" in details
                ):

                    html += f"""
<tr>
<td class="detail-label">
Expected
</td>

<td>
{details.get("expected")}
</td>
</tr>
"""

                if (
                    show_expected_actual
                    and
                    "actual" in details
                ):

                    html += f"""
<tr>
<td class="detail-label">
Actual
</td>

<td>
{details.get("actual")}
</td>
</tr>
"""

                #
                # Limits
                #

                show_limits = True

                if (
                    (
                        "value" in details
                        and
                        "low" in details
                        and
                        "high" in details
                    )
                    or
                    (
                        "score" in details
                        and
                        "low" in details
                        and
                        "high" in details
                    )
                    or
                    (
                        "temp" in details
                        and
                        "low" in details
                        and
                        "high" in details
                    )
                ):

                    show_limits = False

                low = details.get(
                    "low"
                )

                high = details.get(
                    "high"
                )

                if (
                    show_limits
                    and
                    (
                        low is not None
                        or
                        high is not None
                    )
                ):

                    html += f"""
<tr>
<td class="detail-label">
Low Limit
</td>

<td>
{low}
</td>
</tr>

<tr>
<td class="detail-label">
High Limit
</td>

<td>
{high}
</td>
</tr>
"""

                #
                # Additional Details
                #

                remaining_details = {}

                for key, value in details.items():

                    if key in (
                        "expected",
                        "actual",
                        "low",
                        "high",
                        "ports",
                        "channels",
                        "adc"
                    ):
                        continue

                    remaining_details[key] = value

                #
                # Thermal y CurrSens
                # Ya tienen renderer dedicado
                #
                if (
                    (
                        "temperature" in details
                        and
                        "humidity" in details
                    )
                    or
                    (
                        "voltage" in details
                        and
                        "current" in details
                    )
                    or
                    (
                        "value" in details
                        and
                        "low" in details
                        and
                        "high" in details
                    )
                    or
                    (
                        "score" in details
                        and
                        "low" in details
                        and
                        "high" in details
                    )
                    or
                    (
                        "temp" in details
                        and
                        "low" in details
                        and
                        "high" in details
                    )
                    or
                    (
                        "sapme_key" in details
                        and
                        "actual" in details
                        and
                        name == "AB Erase DID"
                    )
                ):

                    remaining_details = {}

                if remaining_details:

                    html += """
<tr>
<td class="detail-label">
Additional Details
</td>

<td>
"""

                    for key, value in remaining_details.items():

                        html += (
                            f"<b>{key}</b>: "
                            f"{value}<br>"
                        )

                    html += """
</td>
</tr>
"""

            #
            # Test Results / Data
            #

            show_test_results = True

            if (
                isinstance(
                    parsed_data,
                    dict
                )
            ):

                details = verification.get(
                    "details",
                    {}
                )

                if (
                    (
                        "temperature" in details
                        and
                        "humidity" in details
                    )
                    or
                    (
                        "voltage" in details
                        and
                        "current" in details
                    )
                    or
                    (
                        "expected" in details
                        and
                        "actual" in details
                        and
                        len(details) == 2
                    )
                    or
                    (
                        "vendor_id"
                        in parsed_data.get(
                            "data",
                            {}
                        )
                    )
                    or
                    (
                        "value" in details
                        and
                        "low" in details
                        and
                        "high" in details
                    )
                    or
                    (
                        "score" in details
                        and
                        "low" in details
                        and
                        "high" in details
                    )
                    or
                    (
                        "temp" in details
                        and
                        "low" in details
                        and
                        "high" in details
                    )
                    or
                    (
                        parsed_data.get(
                            "data",
                            {}
                        ).get(
                            "message"
                        )
                        == "COMMAND ACCEPT"
                    )
                    or
                    (
                        name == "LPC"
                    )
                    or
                    (
                        isinstance(
                            details.get(
                                "ports",
                                []
                            ),
                            list
                        )
                        and
                        len(
                            details.get(
                                "ports",
                                []
                            )
                        ) > 0
                    )
                    or
                    (
                        name in [
                            "USB3 to USB2",
                            "USB2 to USB3"
                        ]
                    )
                    or
                    (
                        name == "AB Erase DID"
                    )
                    or
                    (
                        isinstance(
                            parsed_data,
                            dict
                        )
                        and
                        "bus_width"
                        in parsed_data.get(
                            "data",
                            {}
                        )
                        and
                        "clock"
                        in parsed_data.get(
                            "data",
                            {}
                        )
                    )
                ):

                    show_test_results = False

            if (
                parsed_data
                and
                show_test_results
            ):

                html += """
<div class="section-title">
TestResults / Data
</div>
"""
                #
                # SPI Renderer
                #
                if (
                    isinstance(
                        parsed_data,
                        dict
                    )
                    and
                    "steps" in parsed_data
                    and
                    len(
                        parsed_data["steps"]
                    ) > 0
                    and
                    "device_id"
                    in
                    parsed_data["steps"][0]
                    .get(
                        "verification",
                        {}
                    )
                    .get(
                        "details",
                        {}
                    )
                ):

                    spi_limits = (
                        app_state
                        .sapme_limits
                        .get(
                            "SPI",
                            {}
                        )
                    )

                    rows = []

                    for step in parsed_data["steps"]:

                        details = (
                            step
                            .get(
                                "verification",
                                {}
                            )
                            .get(
                                "details",
                                {}
                            )
                        )

                        cmd = step.get(
                            "cmd",
                            ""
                        )

                        device = (
                            cmd.replace(
                                "websocket_test.sh spi ",
                                ""
                            )
                            .strip()
                        )

                        sapme_key = (
                            f"SPI_{device}_ID"
                        )

                        expected = (
                            spi_limits
                            .get(
                                sapme_key,
                                {}
                            )
                            .get(
                                "high",
                                ""
                            )
                        )

                        actual = details.get(
                            "device_id",
                            ""
                        )

                        rows.append({

                            "device":
                                f"SPI {device}",

                            "expected":
                                expected,

                            "actual":
                                actual,

                            "result":
                                step
                                .get(
                                    "verification",
                                    {}
                                )
                                .get(
                                    "status",
                                    ""
                                )
                        })

                    html += (
                        HtmlReportBuilder
                        .render_spi_table(
                            rows
                        )
                    )

                #
                # I2S Renderer
                #
                elif (
                    name == "I2S"
                    and
                    isinstance(
                        parsed_data,
                        dict
                    )
                    and
                    "steps" in parsed_data
                ):

                    i2s_limits = (
                        app_state
                        .sapme_limits
                        .get(
                            "I2S",
                            {}
                        )
                    )

                    rows = []

                    for step in parsed_data["steps"]:

                        details = (
                            step
                            .get(
                                "verification",
                                {}
                            )
                            .get(
                                "details",
                                {}
                            )
                        )

                        #
                        # Ignorar pasos loopback y stop
                        #
                        if (
                            "score"
                            not in details
                        ):
                            continue

                        cmd = step.get(
                            "cmd",
                            ""
                        )

                        match = re.search(
                            r"i2s\s+(\d+)\s+1\s+1",
                            cmd
                        )

                        if not match:
                            continue

                        channel_num = (
                            match.group(1)
                        )

                        sapme_key = (
                            f"CHECKI2S_{channel_num}_VALUE"
                        )

                        limits = (
                            i2s_limits
                            .get(
                                sapme_key,
                                {}
                            )
                        )

                        rows.append({

                            "name":
                                f"I2S {channel_num}",

                            "low":
                                limits.get(
                                    "low",
                                    ""
                                ),

                            "actual":
                                details.get(
                                    "score",
                                    ""
                                ),

                            "high":
                                limits.get(
                                    "high",
                                    ""
                                ),

                            "result":
                                step
                                .get(
                                    "verification",
                                    {}
                                )
                                .get(
                                    "status",
                                    ""
                                )
                        })

                    if rows:

                        html += (
                            HtmlReportBuilder
                            .render_i2s_table(
                                rows
                            )
                        )
                #
                # I2C Renderer
                #
                elif (
                    isinstance(
                        parsed_data,
                        dict
                    )
                    and
                    "steps" in parsed_data
                    and
                    len(parsed_data["steps"]) > 0
                    and
                    "temp"
                    in
                    parsed_data["steps"][0]
                    .get(
                        "verification",
                        {}
                    )
                    .get(
                        "details",
                        {}
                    )
                ):

                    rows = []

                    for step in parsed_data["steps"]:

                        details = (
                            step
                            .get(
                                "verification",
                                {}
                            )
                            .get(
                                "details",
                                {}
                            )
                        )

                        sensor_name = (
                            details.get(
                                "sapme_key",
                                ""
                            )
                            .replace(
                                "12C_TEMPERATURE_",
                                "Sensor "
                            )
                        )

                        rows.append({

                            "sensor":
                                sensor_name,

                            "low":
                                details.get(
                                    "low",
                                    ""
                                ),

                            "actual":
                                details.get(
                                    "temp",
                                    ""
                                ),

                            "high":
                                details.get(
                                    "high",
                                    ""
                                ),

                            "result":
                                step
                                .get(
                                    "verification",
                                    {}
                                )
                                .get(
                                    "status",
                                    ""
                                )
                        })

                    html += (
                        HtmlReportBuilder
                        .render_i2c_table(
                            rows
                        )
                    )
                #
                # GPIO Renderer
                #
                elif (
                    name == "GPIO"
                    and
                    isinstance(
                        parsed_data,
                        dict
                    )
                    and
                    "steps" in parsed_data
                ):

                    patterns = {}

                    for step in parsed_data["steps"]:

                        details = (
                            step
                            .get(
                                "verification",
                                {}
                            )
                            .get(
                                "details",
                                {}
                            )
                        )

                        patterns.update(
                            details.get(
                                "patterns",
                                {}
                            )
                        )

                    rows = []

                    for (
                        pattern_name,
                        pattern_data
                    ) in patterns.items():
                        
                        if not (
                            pattern_name.endswith(
                                "_0-15"
                            )
                            or
                            pattern_name.endswith(
                                "_16-31"
                            )
                            or
                            pattern_name.endswith(
                                "_32-41"
                            )
                        ):
                            continue
                        #
                        # Sólo mostrar
                        # patrones principales
                        #
                        if not (
                            pattern_name.endswith(
                                "_0-15"
                            )
                            or
                            pattern_name.endswith(
                                "_16-31"
                            )
                            or
                            pattern_name.endswith(
                                "_32-41"
                            )
                        ):
                            continue

                        rows.append({

                            "pattern":
                                pattern_name,

                            "expected":
                                pattern_data.get(
                                    "high",
                                    ""
                                ),

                            "actual":
                                pattern_data.get(
                                    "actual",
                                    ""
                                ),

                            "result":
                                pattern_data.get(
                                    "status",
                                    ""
                                )
                        })

                    if rows:

                        html += (
                            HtmlReportBuilder
                            .render_gpio_table(
                                rows
                            )
                        )  
                #
                # PWM Renderer
                #
                elif (
                    name == "PWM"
                    and
                    isinstance(
                        parsed_data,
                        dict
                    )
                    and
                    "steps" in parsed_data
                ):

                    rows = []

                    for step in parsed_data["steps"]:

                        cmd = step.get(
                            "cmd",
                            ""
                        )

                        command_name = (
                            cmd.replace(
                                "websocket_test.sh ",
                                ""
                            )
                        )

                        result = (
                            step
                            .get(
                                "verification",
                                {}
                            )
                            .get(
                                "status",
                                ""
                            )
                        )

                        rows.append({

                            "command":
                                command_name,

                            "result":
                                result
                        })

                    html += (
                        HtmlReportBuilder
                        .render_pwm_table(
                            rows
                        )
                    )                  
                #
                # ADC Special Renderer
                #

                elif (
                    isinstance(parsed_data, dict)
                    and
                    "steps" in parsed_data
                ):

                    for idx, step in enumerate(
                        parsed_data["steps"]
                    ):

                        html += f"""
<table class="detail-table">

<tr>
<td class="detail-label">
ADC Step
</td>

<td>
{idx + 1}
</td>
</tr>

<tr>
<td class="detail-label">
Command
</td>

<td>
{step.get("cmd", "")}
</td>
</tr>

</table>

<br>
"""

                        verification = step.get(
                            "verification",
                            {}
                        )
                        html += f"""
<div class="adc-summary">

<b>Step:</b> {idx + 1}
&nbsp;&nbsp;|&nbsp;&nbsp;
<b>Status:</b> {verification.get("status", "")}
&nbsp;&nbsp;|&nbsp;&nbsp;
{verification.get("message", "")}

</div>

<br>
"""

                        details = verification.get(
                            "details",
                            {}
                        )

                        adc_name = details.get(
                            "adc",
                            ""
                        )

                        channels = details.get(
                            "channels",
                            []
                        )

                        if channels:

                            rows = []

                            for channel in channels:

                                rows.append({

                                    "name": channel.get(
                                        "channel",
                                        ""
                                    ),

                                    "low": channel.get(
                                        "low",
                                        ""
                                    ),

                                    "high": channel.get(
                                        "high",
                                        ""
                                    ),

                                    "actual": channel.get(
                                        "actual",
                                        ""
                                    ),

                                    "result": channel.get(
                                        "result",
                                        ""
                                    )

                                })

                            html += HtmlReportBuilder.render_subsequence_table(
                                adc_name,
                                rows
                            )

                       
                #
                # Generic Data Renderer
                #

                elif (
                    isinstance(parsed_data, dict)
                    and
                    "data" in parsed_data
                    and
                    isinstance(
                        parsed_data["data"],
                        dict
                    )
                ):

                    data_rows = parsed_data["data"]

                    if len(data_rows) <= 20:

                        html += """
<table class="detail-table">
"""

                        for key, value in data_rows.items():

                            html += f"""
<tr>
<td class="detail-label">
{key}
</td>

<td>
{value}
</td>
</tr>
"""

                        html += """
</table>
"""




            html += """
</div>
"""

        html += """
</body>
</html>
"""

        return html