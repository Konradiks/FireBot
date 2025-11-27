import json

from django.utils import timezone

from FireBot.models import BlockedAddress


def gen_panos_securityrules_block(host: str, ip_list: list, vsys: str = "vsys1", api_key: str="<YOUR-API-KEY>"):
    '''
    Generate a single curl command that creates multiple deny rules in one request.
    https://pan.dev/scm/api/config/ngfw/security/create-security-rules/
    Args:
        host: firewall IP/hostname
        api_key: PAN-OS API key
        ip_list: list of IPs to block
        vsys: VSYS name (default: vsys1)

    Returns:
        str: curl command
    '''

    entries = []
    for ip in ip_list:
        rule_name = f"FireBot-{ip}"
        entry = {
            "@location": "vsys",
            "@name": rule_name,
            "@vsys": vsys,
            "action": "deny",
            "source": {"member": [ip]},
            "destination": {"member": ["any"]},
            "description": "Regula stworzona przez FireBot"
        }
        entries.append(entry)

    payload = {"entry": entries}

    payload_str = json.dumps(payload, indent=4)

    url = f"{host}/restapi/v11.0/Policies/SecurityRules?location=vsys&vsys={vsys}&name=FireBot-batch"


    cmd_command = "curl -k -X POST \\\n"
    cmd_command += "  '" + url + "' \\\n"
    cmd_command += "  -H 'X-PAN-KEY: " + api_key + "' \\\n"
    # cmd_command += "  -H 'Content-Type: application/json' \\\n"
    cmd_command += "  -d '" + payload_str + "'"

    return cmd_command


def get_command_html(command):

    escaped_command = json.dumps(str(command))

    return f"""
<html>
    <head>
        <title>Wygenerowana komenda</title>
        <style>
            body {{ font-family: monospace; padding: 20px; background: #f5f5f5; }}
            pre {{ background: #222; color: #0f0; padding: 15px; border-radius: 5px; overflow-x: auto; }}
            button {{ margin-top: 10px; padding: 5px 10px; margin-right: 10px; }}
        </style>
    </head>
    <body>

        <div style="display: flex; flex-direction: column">
            <h3>Wygenerowana komenda:</h3>
            <div id="apiSection">
                <label>Wpisz klucz API:</label><br>
                <input id="apiInput" type="text" placeholder="API key" style="width:300px; padding:5px;">
                <button onclick="updateApiKey()">Uzupełnij klucz</button>
            </div>
        </div>

        <pre id="commandBox">{command}</pre>
        <button onclick="copyCommand()">Kopiuj do schowka</button>
        <button onclick="goBack()">Powrót do dashboard</button>

        <script>
            // string, nie obiekt!
            let originalCommand = {escaped_command};

            function updateApiKey() {{
                let apiKey = document.getElementById('apiInput').value;

                if (!apiKey) {{
                    alert("Podaj klucz API!");
                    return;
                }}

                // Podstawiamy <YOUR-API-KEY> w stringu
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





def gen_panos_securityrules_unblock(host: str, ip_list: list, vsys: str = "vsys1", api_key: str = "<YOUR-API-KEY>"):
    """
    Generate a single curl command (or multiline command) that deletes FireBot deny rules for given IPs.

    Args:
        host: firewall IP/hostname
        api_key: PAN-OS API key
        ip_list: list of IPs to unblock
        vsys: VSYS name (default: vsys1)

    Returns:
        str: curl command(s) for deleting rules
    """

    cmd_command = ""

    for ip in ip_list:
        rule_name = f"FireBot-{ip}"
        url = f"{host}/restapi/v11.0/Policies/SecurityRules?location=vsys&vsys={vsys}&name={rule_name}"

        cmd_command += "curl -k -X DELETE \\\n"
        cmd_command += "+  '" + url + "' \\\n"
        cmd_command += "+  -H 'X-PAN-KEY: " + api_key + "' \\\n"
        cmd_command += "+  -H 'Content-Type: application/json'\n\n"

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

