import requests
import urllib3
from bs4 import BeautifulSoup
from pathlib import Path

urllib3.disable_warnings()

USERNAME = "report_user"
PASSWORD = "harman123"

SFC = "420036333048040404062289"

BASE_URL = "https://sapmii-mxqt.harman.com:51501"


class SapMeClient:

    def __init__(self):
        self.session = requests.Session()

    def login(self):

        print("[1] Opening login page...")

        login_page_url = (
            f"{BASE_URL}/XMII/Illuminator?service=Personalization"
        )

        response = self.session.get(
            login_page_url,
            verify=False,
            timeout=30
        )

        print(f"Login Page Status: {response.status_code}")

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        salt_input = soup.find(
            "input",
            {"name": "j_salt"}
        )

        if not salt_input:
            raise Exception(
                "Could not find j_salt field"
            )

        j_salt = salt_input["value"]

        print(f"j_salt = {j_salt}")

        login_url = (
            f"{BASE_URL}/XMII/j_security_check"
            "?service=Personalization"
        )

        payload = {
            "j_salt": j_salt,
            "j_username": USERNAME,
            "j_password": PASSWORD,
            "uidPasswordLogon": "Log On"
        }

        print("[2] Logging in...")

        login_response = self.session.post(
            login_url,
            data=payload,
            verify=False,
            allow_redirects=True,
            timeout=30
        )

        print(
            f"Login Status: {login_response.status_code}"
        )

        print(
            f"Final URL: {login_response.url}"
        )

        print("\nCookies:")

        for cookie in self.session.cookies:
            print(f"  {cookie.name}")

        Path("output").mkdir(
            exist_ok=True
        )

        with open(
            "output/login_response.html",
            "w",
            encoding="utf-8"
        ) as f:
            f.write(login_response.text)

        return login_response

    def get_fct_page(self, sfc):

        print("\n[3] Loading FCT report...")

        url = (
            f"{BASE_URL}"
            "/XMII/CM/REPORTING15/"
            f"dc_non_ws.irpt?"
            f"sfc={sfc}"
            "&op=OP_FUNC_PCBA"
        )

        response = self.session.get(
            url,
            verify=False,
            timeout=30
        )

        print(
            f"FCT Status: {response.status_code}"
        )

        print(
            f"FCT URL: {response.url}"
        )

        with open(
            "output/fct_page.html",
            "w",
            encoding="utf-8"
        ) as f:
            f.write(response.text)

        return response

    def get_report_js(self):

        print("\n[4] Downloading JS...")

        js_url = (
            f"{BASE_URL}"
            "/XMII/CM/REPORTING15/"
            "scripts/dc_non_ws.js"
        )

        response = self.session.get(
            js_url,
            verify=False,
            timeout=30
        )

        print(
            f"JS Status: {response.status_code}"
        )

        with open(
            "output/dc_non_ws.js",
            "w",
            encoding="utf-8"
        ) as f:
            f.write(response.text)

        return response.text

    def get_parametrics(self, sfc):

        print("\n[5] Calling getParametricsBySFC...")

        runner_url = (
            f"{BASE_URL}"
            "/XMII/Runner"
            "?transaction=REPORTING15/lifecycle/getParametricsBySFC"
            f"&in_sfc={sfc}"
            "&in_op=OP_FUNC_PCBA"
            "&OutputParameter=xml_output"
            "&in_user=report_user"
        )

        print("\nURL:")
        print(runner_url)

        response = self.session.get(
            runner_url,
            verify=False,
            timeout=60
        )

        print(
            f"\nParametrics Status: {response.status_code}"
        )

        if response.status_code != 200:
                raise Exception(
                    f"SAPME error: {response.status_code}"
                )

        #print("\nFirst 3000 chars:\n")
        #print(response.text[:3000])

        return response.text

    def search_ajax_calls(self, js_text):

        print("\n[6] Looking for AJAX endpoints...")

        keywords = [
            "$.ajax",
            "$.get",
            "$.post",
            "ajax",
            "url:",
            "dataTable",
            "dcTable",
            "getParametricsBySFC"
        ]

        for key in keywords:

            if key.lower() in js_text.lower():

                print(
                    f"FOUND => {key}"
                )

        print(
            "\nSearch complete."
        )


def main():

    client = SapMeClient()

    client.login()

    fct = client.get_fct_page(
        SFC
    )

    print(
        "\ndcTable Found:",
        "dcTable" in fct.text
    )

    print(
        "WORKING CURRENT Found:",
        "WORKING CURRENT" in fct.text
    )

    print(
        "TEST STEP DESCRIPTION Found:",
        "TEST STEP DESCRIPTION" in fct.text
    )

    js = client.get_report_js()

    client.search_ajax_calls(js)

    client.get_parametrics(
        SFC
    )

    print(
        "\nFiles generated:"
    )

    print(
        "output/login_response.html"
    )

    print(
        "output/fct_page.html"
    )

    print(
        "output/dc_non_ws.js"
    )

    print(
        "output/parametrics.xml"
    )


if __name__ == "__main__":
    main()