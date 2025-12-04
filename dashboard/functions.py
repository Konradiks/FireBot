import json

from django.utils import timezone
import html
from FireBot.models import BlockedAddress


def gen_panos_securityrules_block(host: str, ip_list: list, vsys: str = "vsys1", api_key: str="<YOUR-API-KEY>"):
    '''
    Generate multiple curl commands (one per IP) that create deny rules.
    Using the REST API endpoint:
    POST /restapi/v11.0/Policies/SecurityRules
    '''

    full_cmd = ""

    for ip in ip_list:
        rule_name = f"FireBot-{ip}"

        entry = {
            "entry": [
                {
                    "@name": rule_name,
                    "@location": "vsys",
                    "@vsys": vsys,
                    "action": "deny",
                    "application": {"member": ["any"]},
                    "category": {"member": ["any"]},
                    "destination": {"member": ["any"]},
                    "from": {"member": ["any"]},
                    "to": {"member": ["any"]},
                    "service": {"member": ["any"]},
                    "source": {"member": [ip]},
                    "source-user": {"member": ["any"]},
                    "source-hip": {"member": ["any"]},
                    "destination-hip": {"member": ["any"]},
                }
            ]
        }

        payload_str = json.dumps(entry, indent=4)

        # każdy POST musi mieć własne name=FireBot-ip
        url = (
            f"{host}/restapi/v11.0/Policies/SecurityRules"
            f"?location=vsys&vsys={vsys}&name={rule_name}"
        )

        cmd = (
            "curl -k -X POST \\\n"
            f"  '{url}' \\\n"
            f"  -H 'X-PAN-KEY: {api_key}' \\\n"
            f"  -d '{payload_str}'\n\n"
        )

        full_cmd += cmd

    return full_cmd


# def gen_panos_securityrules_unblock(host: str, ip_list: list, vsys: str = "vsys1", api_key: str = "<YOUR-API-KEY>"):
#     """
#     Generate a single curl command (or multiline command) that deletes FireBot deny rules for given IPs.
#
#     Args:
#         host: firewall IP/hostname
#         api_key: PAN-OS API key
#         ip_list: list of IPs to unblock
#         vsys: VSYS name (default: vsys1)
#
#     Returns:
#         str: curl command(s) for deleting rules
#     """
#
#     cmd_command = ""
#
#     for ip in ip_list:
#         rule_name = f"FireBot-{ip}"
#         url = f"{host}/restapi/v11.0/Policies/SecurityRules?location=vsys&vsys={vsys}&name={rule_name}"
#
#         cmd_command += "curl -k -X DELETE \\\n"
#         cmd_command += "+  '" + url + "' \\\n"
#         cmd_command += "+  -H 'X-PAN-KEY: " + api_key + "' \\\n"
#         cmd_command += "+  -H 'Content-Type: application/json'\n\n"
#
#     return cmd_command

def gen_panos_securityrules_unblock(host: str, ip_list: list, vsys: str = "vsys1", api_key: str = "<YOUR-API-KEY>"):
    """
    Generate curl DELETE commands that remove REST API security rules for given IPs.
    """

    cmd = ""

    for ip in ip_list:
        rule_name = f"FireBot-{ip}"

        cmd += (
            "curl -k -X DELETE \\\n"
            f"  '{host}/restapi/v11.0/Policies/SecurityRules?location=vsys&vsys={vsys}&name={rule_name}' \\\n"
            f"  -H 'X-PAN-KEY: {api_key}'\n\n"
        )

    return cmd


def get_commit_command(host: str, vsys: str = "vsys1", api_key: str="<YOUR-API-KEY>"):

    cmd_xml = "<commit></commit>"
    cmd_escaped = html.escape(cmd_xml)  # &lt;commit&gt;&lt;/commit&gt;

    url = f"{host}/api/?type=commit&key={api_key}&cmd={cmd_escaped}"

    cmd_command = "curl -k -X POST \\\n"
    cmd_command += "  '" + url

    return cmd_command


def db_mark_block_ip_addresses(ip_list: list):
    for ip in ip_list:
        ob = BlockedAddress.objects.filter(
            address=ip

        ).first()
        ob.is_blocked=True
        ob.save(update_fields=["is_blocked"])

def db_mark_unblock_ip_addresses(ip_list: list):
    for ip in ip_list:
        ob = BlockedAddress.objects.filter(
            address=ip

        ).first()
        ob.is_blocked=False
        ob.requires_unblock=False
        ob.was_unblocked=True
        ob.end_time=timezone.now()
        ob.save(update_fields=["is_blocked", "requires_unblock", "was_unblocked", "end_time"])


def get_command_html(command):

    escaped_command = json.dumps(str(command))

    return f"""
<html>
    <head>
        <title>Wygenerowana komenda</title>
        <style>
            body {{ font-family: monospace; padding: 20px; background: #f5f5f5; }}

            .scroll-box {{
                background: #222;
                color: #0f0;
                padding: 15px;
                border-radius: 5px;
                width: 90vw;
                max-height: 67vh; 
                overflow: auto;      /* scroll vertical + horizontal */
                white-space: pre;     /* zachowuje formatowanie */
                margin-top: 20px;
                margin-bottom: 10px;
            }}

            button {{ 
                margin-top: 10px; 
                padding: 5px 10px; 
                margin-right: 10px; 
            }}
        </style>
    </head>
    <body>

        <div style="display: flex; flex-direction: column; width:800px;">
            <h3>Wygenerowana komenda:</h3>
            <div style="display: flex; align-items: end;">
                <div id="apiSection">
                    <label>Wpisz klucz API:</label><br>
                    <input id="apiInput" type="text" placeholder="API key" style="width:300px; padding:5px;">
                    <button onclick="updateApiKey()">Uzupełnij klucz</button>
                </div>
                <a href="https://docs.paloaltonetworks.com/pan-os/11-0/pan-os-panorama-api/get-started-with-the-pan-os-xml-api/get-your-api-key" target="_blank">Jak pozyskać klucz api</a>
            </div>
        </div>

        <div id="commandBox" class="scroll-box">{command}</div>

        <button onclick="copyCommand()">Kopiuj do schowka</button>
        <button onclick="goBack()">Powrót do dashboard</button>

        <script>
            let originalCommand = {escaped_command};

            function updateApiKey() {{
                let apiKey = document.getElementById('apiInput').value;

                if (!apiKey) {{
                    alert("Podaj klucz API!");
                    return;
                }}

                let updated = originalCommand.replace(/<YOUR-API-KEY>/g, apiKey);
                document.getElementById('commandBox').innerText = updated;
            }}

            function copyCommand() {{
                const content = document.getElementById('commandBox').innerText;
                navigator.clipboard.writeText(content);
            }}

            function goBack() {{
                window.location.href = '/dashboard/mode/';
            }}
        </script>
    </body>
</html>
"""
