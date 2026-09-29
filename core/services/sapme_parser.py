#!/usr/bin/env python3

import re
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup


def convert_value(value):

    if value is None:
        return None

    value = value.strip()

    gpio_patterns = (
        "111111",
        "000000"
    )

    for pattern in gpio_patterns:

        if value.startswith(pattern):
            return value

    if "VER:" in value.upper():
        return value

    try:
        return float(
            value.replace(",", ".")
        )

    except Exception:
        return value


def get_group(test_name):

    name = test_name.upper()

    if name.startswith("ADC0_") or name.startswith("ADC1_"):
        return "ADC"

    if name.startswith("ADC PORT"):
        return "ADC_DUPLICATE"

    if "PCIE" in name:
        return "PCIE"

    if "USB3_3" in name:
        return "USB3_3"

    if "USB3_2" in name:
        return "USB3_2"

    if "USB2" in name:
        return "USB2"

    if "CURSENS" in name:
        return "POWER"

    if "WORKING CURRENT" in name:
        return "POWER"

    if "TEMPERATURE" in name:
        return "THERMAL"

    if "HUMIDITY" in name:
        return "THERMAL"

    if "CB_BOARD_TEMP" in name:
        return "THERMAL"

    if "CPU" in name:
        return "CPU"

    if "KERNEL" in name:
        return "CPU"

    if "MODEL" in name:
        return "SYSTEM"

    if "VENDOR_ID" in name:
        return "SYSTEM"

    if "CACHE" in name:
        return "SYSTEM"

    if "BOGOMIPS" in name:
        return "SYSTEM"

    if "GROUP1_" in name:
        return "GPIO"

    if "GROUP2_" in name:
        return "GPIO"

    if "GROUP3_" in name:
        return "GPIO"

    if "SPI" in name:
        return "SPI"

    if "I2S" in name:
        return "I2S"

    if "URAT" in name or "UART" in name:
        return "UART"

    if "EMMC" in name:
        return "EMMC"

    if "CSI" in name:
        return "CSI"

    if "VERSION" in name:
        return "VERSION"

    if "VER:" in name:
        return "VERSION"

    return "MISC"


def normalize_pcie(group):

    result = {}

    for name, data in group.items():

        for port in range(4):

            if f"PCIE_{port}" in name:

                port_name = f"PORT_{port}"

                if port_name not in result:
                    result[port_name] = {}

                if "PING" in name:
                    result[port_name]["PING"] = data

                elif "TX" in name:
                    result[port_name]["TX"] = data

                elif "RX" in name:
                    result[port_name]["RX"] = data

    return result


def normalize_usb(group):

    result = {}

    for name, data in group.items():

        match = re.search(
            r'_(\d+)_(PING|TX|RX)',
            name
        )

        if not match:
            continue

        port = match.group(1)

        io_type = match.group(2)

        port_name = f"PORT_{port}"

        if port_name not in result:
            result[port_name] = {}

        result[port_name][io_type] = data

    return result


def is_version_field(test_name):

    test_name = test_name.upper()

    version_keywords = [
        "VERSION",
        "VER:",
        "FW_VERSION",
        "SW_VERSION",
        "KERNEL VERSION"
    ]

    return any(
        keyword in test_name
        for keyword in version_keywords
    )


def parse_parametrics(
    xml_text: str
):

    root = ET.fromstring(
        xml_text
    )

    data_node = root.find(
        "data"
    )

    if data_node is None:
        raise Exception(
            "No data node found"
        )

    html = data_node.text

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    table = soup.find(
        "table",
        {"id": "dcTable"}
    )

    if table is None:
        raise Exception(
            "dcTable not found"
        )

    tbody = table.find(
        "tbody"
    )

    if tbody is None:
        raise Exception(
            "tbody not found"
        )

    grouped = {}

    rows = tbody.find_all(
        "tr"
    )

    for row in rows:

        cols = [
            td.get_text(strip=True)
            for td in row.find_all("td")
        ]

        if len(cols) < 13:
            continue

        test_step = cols[5]
        description = cols[6]
        status = cols[8]
        high_limit = cols[10]
        low_limit = cols[11]
        actual = cols[12]

        group = get_group(
            description
        )

        if group not in grouped:
            grouped[group] = {}

        if is_version_field(
            description
        ):

            high = str(
                high_limit
            ).strip()

            low = str(
                low_limit
            ).strip()

            actual_value = str(
                actual
            ).strip()

        else:

            high = convert_value(
                high_limit
            )

            low = convert_value(
                low_limit
            )

            actual_value = convert_value(
                actual
            )

        grouped[group][description] = {
            "test_step": test_step,
            "status": status,
            "high": high,
            "low": low,
            "actual": actual_value
        }

    #
    # Eliminar ADC duplicados
    #
    if "ADC_DUPLICATE" in grouped:
        del grouped["ADC_DUPLICATE"]

    #
    # Reorganizar PCIE
    #
    if "PCIE" in grouped:

        grouped["PCIE"] = normalize_pcie(
            grouped["PCIE"]
        )

    #
    # Reorganizar USB
    #
    if "USB2" in grouped:

        grouped["USB2"] = normalize_usb(
            grouped["USB2"]
        )

    if "USB3_2" in grouped:

        grouped["USB3_2"] = normalize_usb(
            grouped["USB3_2"]
        )

    if "USB3_3" in grouped:

        grouped["USB3_3"] = normalize_usb(
            grouped["USB3_3"]
        )

    return grouped