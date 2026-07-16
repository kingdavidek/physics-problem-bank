"""
GCSE Computer Science – Computer Networks
10 foundational · 10 intermediate · 10 difficult · 15 MCQ
Graded practice variants return (question, solution, hint, marks, raw).
Explanation-only variants stay as 4-tuples (Phase 2).
"""
import random
from generators.shared.utils import make_problem
from generators.shared.variant_utils import pick_named_variant


def _net_raw_number(value):
    if isinstance(value, float):
        val = round(value, 2)
        if val == int(val):
            return str(int(val))
        return f'{val:.2f}'.rstrip('0').rstrip('.')
    return str(int(value))


def _net_fields_answer(values, labels):
    return {
        'type': 'number_fields',
        'values': tuple(_net_raw_number(v) for v in values),
        'labels': tuple(labels),
    }


def _net_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict) and raw.get('type') == 'number_fields':
            values = raw.get('values') or ()
            labels = raw.get('labels') or ()
            if values and len(values) == len(labels):
                extra = {
                    'correct_answer_raw': '|'.join(str(v) for v in values),
                    'answer_type': 'number_fields',
                    'answer_labels': list(labels),
                    'answer_format_hint': 'Enter a number in every field',
                }
        elif isinstance(raw, (int, float)):
            extra = {
                'correct_answer_raw': _net_raw_number(raw),
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number',
            }
    return make_problem(
        q, s, hint, difficulty, marks, 'gcse', 'cs', 'computer_networks', **extra
    )


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (10)
# ══════════════════════════════════════════════════════════════════════════════

def _net_f1_lan():
    q = "What is a <strong>LAN</strong> (Local Area Network)?"
    s = (
        "A network covering a <strong>small geographic area</strong> (e.g. one school, "
        "office, or home) with privately owned links."
    )
    return q, s, "LAN = local — usually one building or site.", 1


def _net_f2_wan():
    q = "How does a <strong>WAN</strong> differ from a LAN?"
    s = (
        "A <strong>WAN</strong> (Wide Area Network) covers a <strong>large area</strong> "
        "(cities, countries). The internet is the largest WAN."
    )
    return q, s, "WAN uses public/shared infrastructure over long distances.", 1


def _net_f3_client_server():
    q = "In <strong>client–server</strong>, name the roles of the web browser and the web server."
    s = (
        "The <strong>browser is the client</strong> (requests pages). "
        "The <strong>web server is the server</strong> (stores and sends pages)."
    )
    return q, s, "Client requests; server provides a service.", 2


def _net_f4_p2p():
    q = "Give <strong>one advantage</strong> of peer-to-peer (P2P) networks."
    s = (
        "No dedicated expensive server needed; <strong>easy to set up</strong> for small groups; "
        "files can be shared directly between peers (e.g. local file sharing)."
    )
    return q, s, "P2P: each device can be client and server.", 2


def _net_f5_star_topology():
    q = "In a <strong>star topology</strong>, all devices connect to a central device. Name two examples of that central device."
    s = "<strong>Switch</strong> or <strong>wireless access point (WAP)</strong> / hub at the centre."
    return q, s, "Star = spokes to a hub; common in school networks.", 2


def _net_f6_router_role():
    q = "What is the main job of a <strong>router</strong>?"
    s = (
        "A router <strong>forwards data packets between networks</strong> "
        "(e.g. from your LAN to the internet), choosing the best path."
    )
    return q, s, "Connects LAN to WAN; uses IP addresses.", 2


def _net_f7_http():
    q = "Which protocol is used when you view a web page in a browser?"
    s = "<strong>HTTP</strong> (Hypertext Transfer Protocol) or <strong>HTTPS</strong> if encrypted."
    return q, s, "HTTPS = HTTP + encryption (TLS).", 1


def _net_f8_nic():
    q = "What does a <strong>Network Interface Card (NIC)</strong> do?"
    s = "Connects a device to a network and provides it with a <strong>MAC address</strong>."
    return q, s, "Built into motherboards or WiFi adapters.", 1


def _net_f9_wifi_wap():
    q = "What does a <strong>Wireless Access Point (WAP)</strong> allow?"
    s = "Allows devices to connect to a wired LAN <strong>wirelessly</strong> (WiFi)."
    return q, s, "WAP bridges WiFi clients to the switch/router.", 1


def _net_f10_packet():
    q = "Why is data split into <strong>packets</strong> for transmission?"
    s = (
        "Packets can take <strong>different routes</strong>, share bandwidth fairly, "
        "and errors only require resending small chunks — not the whole file."
    )
    return q, s, "Packet switching is how the internet works.", 2


def _net_f11_ipv4_groups():
    q = (
        "An <strong>IPv4</strong> address is written as four numbers separated by dots "
        "(e.g. 192.168.0.10). How many numbers (octets) are in one IPv4 address?"
    )
    s = "An IPv4 address has <strong>4</strong> octets (e.g. four groups of 0–255)."
    return q, s, "IPv4 = 32 bits shown as 4 denary octets.", 1, 4


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (10)
# ══════════════════════════════════════════════════════════════════════════════

def _net_i1_topology_compare():
    q = (
        "Give <strong>one advantage</strong> of star topology over bus topology "
        "for a school network."
    )
    s = (
        "If one cable to a classroom fails, <strong>only that device is affected</strong>; "
        "bus failure on the backbone can affect many machines."
    )
    return q, s, "Star: fault isolation; bus: single backbone risk.", 2


def _net_i2_switch_vs_hub():
    q = "How does a <strong>switch</strong> differ from an old <strong>hub</strong>?"
    s = (
        "A switch sends data <strong>only to the intended device</strong> (learns MAC addresses). "
        "A hub <strong>broadcasts</strong> to all ports — wasteful and slower."
    )
    return q, s, "Switches are smarter; hubs are largely obsolete.", 2


def _net_i3_dns():
    q = "What is <strong>DNS</strong> and why is it needed?"
    s = (
        "<strong>Domain Name System</strong> — translates human-friendly names "
        "(e.g. www.bbc.co.uk) into <strong>IP addresses</strong> computers use."
    )
    return q, s, "Like a phone book for the internet.", 2


def _net_i4_ipv4():
    q = (
        "How many <strong>bits</strong> are used to represent one complete "
        "<strong>IPv4</strong> address?"
    )
    s = "Four octets × 8 bits = <strong>32 bits</strong> (shown as four numbers 0–255)."
    return q, s, "IPv4 = 32 bits, shown as 4 denary octets.", 1, 32


def _net_i11_http_port():
    q = (
        "What is the default port number for unencrypted <strong>HTTP</strong> web traffic?"
    )
    s = "Standard HTTP uses port <strong>80</strong>."
    return q, s, "HTTPS typically uses port 443 instead.", 1, 80


def _net_i12_https_port():
    q = (
        "What is the default port number for secure <strong>HTTPS</strong> web traffic?"
    )
    s = "Standard HTTPS uses port <strong>443</strong>."
    return q, s, "HTTPS = HTTP with encryption (TLS).", 1, 443


def _net_i13_mac_bits():
    q = "How many <strong>bits</strong> are in a standard MAC address?"
    s = "A MAC address is <strong>48 bits</strong> (often shown as six hex pairs)."
    return q, s, "MAC addresses are assigned to the NIC hardware.", 2, 48


def _net_i5_mac_vs_ip():
    q = "What is the difference between a <strong>MAC address</strong> and an <strong>IP address</strong>?"
    s = (
        "<strong>MAC</strong> — fixed hardware address on the NIC (local delivery on LAN). "
        "<strong>IP</strong> — logical address for routing across networks (can change)."
    )
    return q, s, "MAC = layer 2; IP = layer 3 (routing).", 3


def _net_i6_tcp_udp():
    q = "When streaming video, would <strong>TCP</strong> or <strong>UDP</strong> often be preferred? Brief reason."
    s = (
        "Often <strong>UDP</strong> — occasional lost packets are acceptable; "
        "TCP’s retransmission can cause lag. (TCP used when every byte must arrive, e.g. web pages.)"
    )
    return q, s, "TCP reliable; UDP faster but no guarantee.", 3


def _net_i7_email_protocols():
    q = "Which protocol <strong>sends</strong> email from your client to the mail server: SMTP, POP3, or IMAP?"
    s = "<strong>SMTP</strong> (Simple Mail Transfer Protocol) sends outgoing mail."
    return q, s, "POP/IMAP receive mail from server to client.", 2


def _net_i8_https():
    q = "What extra protection does <strong>HTTPS</strong> provide over HTTP?"
    s = (
        "<strong>Encryption</strong> (TLS) — data is scrambled in transit so eavesdroppers "
        "cannot easily read passwords or card details."
    )
    return q, s, "Look for the padlock in the browser.", 2


def _net_i9_cloud():
    q = "Give <strong>two examples</strong> of cloud services a school might use."
    s = "Examples: <strong>Google Classroom / Microsoft 365</strong>, <strong>cloud backup</strong>, <strong>online file storage (OneDrive)</strong>."
    return q, s, "Cloud = services over the internet, not local servers only.", 2


def _net_i10_bus_topology():
    q = "Describe one <strong>disadvantage</strong> of a bus topology."
    s = (
        "The <strong>main cable (backbone)</strong> is a single point of failure — "
        "if it breaks, the whole network can stop."
    )
    return q, s, "Terminator resistors needed at ends; collisions on old Ethernet bus.", 2


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (10)
# ══════════════════════════════════════════════════════════════════════════════

def _net_d1_packet_switching():
    q = (
        "Explain <strong>packet switching</strong> in two or three sentences "
        "(how a large file travels across the internet)."
    )
    s = (
        "File is split into <strong>packets</strong> with headers (source/destination IP). "
        "Routers forward packets along <strong>different paths</strong>; "
        "packets are <strong>reassembled</strong> at the destination. Failed packets can be resent."
    )
    return q, s, "Contrast with circuit switching (dedicated line).", 4


def _net_d2_firewall():
    q = "What does a <strong>firewall</strong> do on a school network?"
    s = (
        "Monitors and <strong>filters traffic</strong> — blocks unauthorised access, "
        "dangerous ports, or sites against school policy."
    )
    return q, s, "Hardware or software barrier between trusted/untrusted networks.", 3


def _net_d3_nat():
    q = (
        "A home router shows public IP <strong>81.99.x.x</strong> but your laptop has "
        "<strong>192.168.0.15</strong>. Explain briefly."
    )
    s = (
        "<strong>192.168.x.x</strong> is a <strong>private</strong> LAN address (NAT). "
        "The router uses <strong>NAT</strong> so many devices share one public IP on the internet."
    )
    return q, s, "Private ranges: 10.x, 172.16–31, 192.168.x.", 3


def _net_d4_mesh_topology():
    q = "Why might a <strong>full mesh</strong> be used for critical links between two city offices?"
    s = (
        "Every node has <strong>multiple paths</strong> — if one link fails, "
        "traffic can reroute; <strong>high reliability</strong> (expensive)."
    )
    return q, s, "Mesh = redundant connections.", 3


def _net_d5_layered():
    q = "Why is networking described in <strong>layers</strong> (e.g. TCP/IP model)?"
    s = (
        "Each layer has a <strong>specific job</strong> (link, internet, transport, application); "
        "manufacturers can update one layer without redesigning everything."
    )
    return q, s, "GCSE: know application + transport + network + link idea.", 3


def _net_d6_four_layer_send():
    q = (
        "You click a link to a website. Name <strong>two protocols</strong> likely used "
        "from application layer and transport layer."
    )
    s = (
        "Application: <strong>HTTP/HTTPS</strong>. Transport: <strong>TCP</strong> "
        "(reliable delivery). Network: IP routes packets."
    )
    return q, s, "Stack: HTTP over TCP over IP over Ethernet/WiFi.", 3


def _net_d7_bandwidth_latency():
    q = (
        "A gamer has high <strong>bandwidth</strong> but high <strong>latency</strong>. "
        "Explain why online games might still lag."
    )
    s = (
        "<strong>Latency</strong> (ping/delay) affects reaction time — packets take long to return "
        "even if bandwidth (capacity) is large."
    )
    return q, s, "Bandwidth ≠ speed of response; latency = delay.", 3


def _net_d8_vlan_scenario():
    q = (
        "A school wants staff WiFi separate from guest WiFi for security. "
        "Name <strong>one network approach</strong> (hardware/config concept)."
    )
    s = (
        "Separate <strong>SSIDs / VLANs</strong> or subnets with firewall rules — "
        "guests cannot access internal file servers."
    )
    return q, s, "Segmentation limits access between groups.", 3


def _net_d9_pop_imap():
    q = "Compare <strong>POP3</strong> and <strong>IMAP</strong> for reading email."
    s = (
        "<strong>POP3</strong> often downloads mail to one device (may delete from server). "
        "<strong>IMAP</strong> keeps mail on server — syncs across phone, laptop, webmail."
    )
    return q, s, "IMAP better for multiple devices.", 3


def _net_d10_traceroute_concept():
    q = "What information does a <strong>traceroute</strong> (tracert) tool show?"
    s = (
        "The <strong>route and routers (hops)</strong> packets take to reach a host, "
        "with <strong>delay at each hop</strong> — useful for diagnosing network problems."
    )
    return q, s, "Each hop is a router along the path.", 2


def _net_d11_wireless_security():
    q = (
        "Why should a home WiFi network use <strong>WPA2/WPA3</strong> with a strong password "
        "instead of an open network?"
    )
    s = (
        "Encryption prevents nearby devices from <strong>reading traffic</strong> or "
        "<strong>joining the LAN</strong> without the key — reduces eavesdropping and unauthorised access."
    )
    return q, s, "Open WiFi = anyone on the same airwaves can intercept unencrypted data.", 3


def _net_d12_http_status():
    q = (
        "A browser shows <strong>404 Not Found</strong> for one page and "
        "<strong>500 Internal Server Error</strong> for another.<br><br>"
        "Explain the difference between these two status codes."
    )
    s = (
        "<strong>404:</strong> client requested a URL/resource that <strong>does not exist</strong> on the server. "
        "<strong>500:</strong> server received the request but <strong>failed while processing</strong> it."
    )
    return q, s, "4xx = client-side problem; 5xx = server-side failure.", 3


def _net_d15_http_not_found_code():
    q = (
        "A student enters a web address that does not exist on the server. "
        "The browser displays an HTTP error. What is the <strong>status code number</strong> "
        "for <strong>Not Found</strong>?"
    )
    s = "The standard code is <strong>404 Not Found</strong>."
    return q, s, "4xx codes indicate a problem with the client request.", 2, 404


def _net_d16_http_server_error_code():
    q = (
        "A web server crashes while handling a valid request. "
        "What is the <strong>status code number</strong> for "
        "<strong>Internal Server Error</strong>?"
    )
    s = "The standard code is <strong>500 Internal Server Error</strong>."
    return q, s, "5xx codes indicate the server failed to process the request.", 2, 500


# ── Multi-part difficult questions (a, b, c) ──────────────────────────────────

def _net_d13_multipart_home_network():
    q = (
        "A family sets up a home network. Devices connect <strong>wirelessly</strong> to a "
        "router, which connects them to the internet.<br><br>"
        "<strong>a)</strong> State whether this home network is a <strong>LAN</strong> or a "
        "<strong>WAN</strong>, and give one reason. [2]<br>"
        "<strong>b)</strong> Give <strong>two</strong> advantages of connecting wirelessly "
        "(Wi-Fi) rather than using wired Ethernet cables. [2]<br>"
        "<strong>c)</strong> Give <strong>two</strong> disadvantages of using Wi-Fi compared "
        "with wired connections. [2]"
    )
    s = (
        "<strong>a)</strong> It is a <strong>LAN (Local Area Network)</strong> because the "
        "devices are connected over a <strong>small geographical area</strong> (one home) "
        "using equipment owned by the family.<br><br>"
        "<strong>b)</strong> Any two: <strong>no cables needed</strong> (less mess, cheaper "
        "to add devices); devices are <strong>portable / can move around</strong>; easy to "
        "connect many devices like phones and tablets.<br><br>"
        "<strong>c)</strong> Any two: signal can be <strong>weaker / unreliable</strong> "
        "through walls and at distance; generally <strong>slower</strong> than wired; "
        "<strong>less secure</strong> as the signal can be intercepted, so encryption is "
        "needed."
    )
    return q, s, "LAN = small area; Wi-Fi trades convenience for speed/security.", 6


def _net_d14_multipart_protocols():
    q = (
        "When a user visits a secure shopping website and logs in, several "
        "<strong>protocols</strong> are involved.<br><br>"
        "<strong>a)</strong> State what a <strong>protocol</strong> is. [1]<br>"
        "<strong>b)</strong> Name the protocol used to view web pages <strong>securely</strong> "
        "and explain what it adds compared with HTTP. [2]<br>"
        "<strong>c)</strong> Explain why data sent over the internet is split into "
        "<strong>packets</strong>, and state two pieces of information a packet header "
        "contains. [3]"
    )
    s = (
        "<strong>a)</strong> A protocol is a <strong>set of rules</strong> that governs how "
        "devices communicate over a network.<br><br>"
        "<strong>b)</strong> <strong>HTTPS</strong>. It adds <strong>encryption</strong> "
        "(using SSL/TLS) so that data such as passwords and card details cannot be read if "
        "intercepted, unlike plain HTTP.<br><br>"
        "<strong>c)</strong> Splitting data into packets lets them travel by "
        "<strong>different routes</strong> and share the network efficiently; if one packet "
        "is lost only that small part is resent. A packet header contains (any two): "
        "<strong>source address</strong>, <strong>destination address</strong>, "
        "<strong>packet/sequence number</strong>."
    )
    return q, s, "Protocol = rules; HTTPS = HTTP + encryption; packets = small routed chunks.", 6


# ══════════════════════════════════════════════════════════════════════════════
# MCQ BANK (17)
# ══════════════════════════════════════════════════════════════════════════════

_NET_MCQ_BANK = [
    {"q": "A network covering one school building is usually a:",
     "opts": ["A  WAN", "B  LAN", "C  PAN only", "D  VPN"],
     "ans": "B", "marks": 1,
     "sol": "<strong>LAN</strong> = local area. Answer: B",
     "hint": "Small geographic area."},
    {"q": "In client–server, the server:",
     "opts": ["A  only requests data", "B  provides a service to clients",
              "C  cannot use the internet", "D  is always wireless"],
     "ans": "B", "marks": 1,
     "sol": "Server <strong>provides services</strong>. Answer: B",
     "hint": "Client asks; server responds."},
    {"q": "All devices connect to a central switch in:",
     "opts": ["A  bus topology", "B  star topology", "C  ring only", "D  mesh only"],
     "ans": "B", "marks": 1,
     "sol": "<strong>Star</strong> topology. Answer: B",
     "hint": "Spokes from centre."},
    {"q": "DNS translates domain names into:",
     "opts": ["A  MAC addresses only", "B  IP addresses", "C  HTML code", "D  WiFi passwords"],
     "ans": "B", "marks": 2,
     "sol": "DNS → <strong>IP addresses</strong>. Answer: B",
     "hint": "Name to numeric address."},
    {"q": "Which device forwards packets between your home LAN and the internet?",
     "opts": ["A  Printer", "B  Router", "C  Monitor", "D  Keyboard"],
     "ans": "B", "marks": 1,
     "sol": "<strong>Router</strong> connects networks. Answer: B",
     "hint": "Gateway to ISP."},
    {"q": "HTTPS compared with HTTP adds:",
     "opts": ["A  faster cables", "B  encryption", "C  more IP addresses", "D  larger packets only"],
     "ans": "B", "marks": 2,
     "sol": "<strong>Encryption</strong> in transit. Answer: B",
     "hint": "S = secure."},
    {"q": "SMTP is used mainly to:",
     "opts": ["A  send email", "B  browse websites", "C  resolve DNS", "D  print documents"],
     "ans": "A", "marks": 2,
     "sol": "<strong>Send</strong> mail. Answer: A",
     "hint": "Simple Mail Transfer Protocol."},
    {"q": "A MAC address is:",
     "opts": ["A  assigned by a website", "B  built into the NIC hardware",
              "C  the same as a URL", "D  only used on WANs"],
     "ans": "B", "marks": 2,
     "sol": "MAC is <strong>hardware</strong> address. Answer: B",
     "hint": "48-bit, hex pairs."},
    {"q": "The internet is best described as:",
     "opts": ["A  a single LAN", "B  a WAN of interconnected networks",
              "C  one physical cable", "D  only WiFi"],
     "ans": "B", "marks": 1,
     "sol": "Internet = global <strong>WAN</strong>. Answer: B",
     "hint": "Network of networks."},
    {"q": "Packet switching means:",
     "opts": ["A  one dedicated phone line per call forever",
              "B  data split into packets that may take different routes",
              "C  no routers used", "D  only wireless transmission"],
     "ans": "B", "marks": 2,
     "sol": "Packets <strong>routed independently</strong>. Answer: B",
     "hint": "Reassembled at end."},
    {"q": "A switch improves on a hub because it:",
     "opts": ["A  broadcasts to every port always", "B  sends frames to the correct device",
              "C  replaces the need for IP", "D  only works on WAN"],
     "ans": "B", "marks": 2,
     "sol": "Targeted delivery using MAC table. Answer: B",
     "hint": "Less unnecessary traffic."},
    {"q": "TCP is typically chosen when:",
     "opts": ["A  some packet loss is fine for live video only",
              "B  reliable, ordered delivery is required",
              "C  DNS lookups run", "D  MAC addresses are assigned"],
     "ans": "B", "marks": 2,
     "sol": "TCP = <strong>reliable</strong>. Answer: B",
     "hint": "Retransmits lost packets."},
    {"q": "Cloud storage means files are kept:",
     "opts": ["A  only on one USB stick", "B  on remote servers accessed via the internet",
              "C  in the CPU cache", "D  on a printer"],
     "ans": "B", "marks": 1,
     "sol": "Remote <strong>internet servers</strong>. Answer: B",
     "hint": "Google Drive, OneDrive, etc."},
    {"q": "A valid IPv4 address has:",
     "opts": ["A  eight hex digits only", "B  four numbers 0–255 separated by dots",
              "C  three letters and a slash", "D  six MAC pairs"],
     "ans": "B", "marks": 2,
     "sol": "Four octets, e.g. 10.0.0.1. Answer: B",
     "hint": "Dotted decimal."},
    {"q": "A firewall’s role is to:",
     "opts": ["A  increase screen resolution", "B  filter network traffic for security",
              "C  store emails permanently", "D  assign domain names"],
     "ans": "B", "marks": 2,
     "sol": "<strong>Filter/block</strong> traffic. Answer: B",
     "hint": "Security barrier."},
    {"q": "UDP is often chosen for live video streaming because:",
     "opts": ["A  it guarantees every packet arrives in order",
              "B  it is faster with less overhead and some loss may be acceptable",
              "C  it encrypts all traffic automatically", "D  it replaces IP addresses"],
     "ans": "B", "marks": 2,
     "sol": "UDP is <strong>lightweight</strong>; small delays matter more than perfect delivery. Answer: B",
     "hint": "Contrast with TCP retransmission."},
    {"q": "Bluetooth is typically used for:",
     "opts": ["A  short-range personal area networks", "B  transatlantic fibre cables only",
              "C  assigning domain names", "D  compiling programs"],
     "ans": "A", "marks": 1,
     "sol": "<strong>PAN</strong> — headphones, phones, peripherals. Answer: A",
     "hint": "Low power, short distance."},
    {"q": "In peer-to-peer (P2P) networks:",
     "opts": ["A  only one dedicated server exists", "B  devices can act as both client and server",
              "C  no data is shared", "D  DNS is not used"],
     "ans": "B", "marks": 2,
     "sol": "Peers <strong>share resources directly</strong>. Answer: B",
     "hint": "Contrast with client–server."},
    {"q": "HTTP is mainly used for:",
     "opts": ["A  transferring web pages and resources", "B  sending email only",
              "C  resolving domain names", "D  printing documents"],
     "ans": "A", "marks": 1,
     "sol": "<strong>Web communication</strong> between browser and server. Answer: A",
     "hint": "HyperText Transfer Protocol."},
    {"q": "A Network Interface Card (NIC) provides:",
     "opts": ["A  a connection to a network", "B  extra RAM for the CPU",
              "C  a graphical desktop", "D  antivirus scanning only"],
     "ans": "A", "marks": 2,
     "sol": "NIC links the device to a <strong>network</strong>. Answer: A",
     "hint": "Built-in or add-on; has a MAC address."},
    {"q": "FTP is commonly used to:",
     "opts": ["A  transfer files between computers", "B  browse social media feeds",
              "C  encrypt all web traffic", "D  assign IP addresses automatically"],
     "ans": "A", "marks": 2,
     "sol": "<strong>File transfer</strong> between systems. Answer: A",
     "hint": "File Transfer Protocol."},
    {"q": "In a bus topology, if the main cable fails:",
     "opts": ["A  only one device is affected", "B  the whole network may stop working",
              "C  traffic is automatically encrypted", "D  the network becomes a star"],
     "ans": "B", "marks": 2,
     "sol": "Shared backbone — <strong>single point of failure</strong>. Answer: B",
     "hint": "All devices connect to one central line."},
]


def computer_networks_mcq():
    item = random.choice(_NET_MCQ_BANK)
    return item["q"], item["sol"], item["hint"], item["marks"], item["opts"], item["ans"]


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS & MAIN ENTRY
# ══════════════════════════════════════════════════════════════════════════════

_FOUNDATIONAL = [
    _net_f1_lan, _net_f2_wan, _net_f3_client_server, _net_f4_p2p,
    _net_f5_star_topology, _net_f6_router_role, _net_f7_http,
    _net_f8_nic, _net_f9_wifi_wap, _net_f10_packet,
    _net_f11_ipv4_groups,
]

_INTERMEDIATE = [
    _net_i1_topology_compare, _net_i2_switch_vs_hub, _net_i3_dns,
    _net_i4_ipv4, _net_i5_mac_vs_ip, _net_i6_tcp_udp,
    _net_i7_email_protocols, _net_i8_https, _net_i9_cloud,
    _net_i10_bus_topology, _net_i11_http_port, _net_i12_https_port,
    _net_i13_mac_bits,
]

_DIFFICULT = [
    _net_d1_packet_switching, _net_d2_firewall, _net_d3_nat,
    _net_d4_mesh_topology, _net_d5_layered, _net_d6_four_layer_send,
    _net_d7_bandwidth_latency, _net_d8_vlan_scenario,
    _net_d9_pop_imap, _net_d10_traceroute_concept,
    _net_d11_wireless_security, _net_d12_http_status,
    _net_d13_multipart_home_network, _net_d14_multipart_protocols,
    _net_d15_http_not_found_code, _net_d16_http_server_error_code,
]


def gcse_computer_networks_variants(difficulty, mode="practice"):
    if mode == "mcq":
        return [computer_networks_mcq] * 10

    pools = {
        "foundational": _FOUNDATIONAL,
        "intermediate": _INTERMEDIATE,
        "difficult": _DIFFICULT,
    }
    if difficulty not in pools:
        return random.sample(_FOUNDATIONAL + _INTERMEDIATE + _DIFFICULT, 10)

    pool = pools[difficulty]
    return random.sample(pool, len(pool))


def gcse_computer_networks(difficulty, mode, variant_name=None):
    if mode == "mcq":
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = computer_networks_mcq()
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            "gcse", "cs", "computer_networks",
            options=opts_mcq, correct_answer=correct_mcq,
        )

    variants = gcse_computer_networks_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)
    return _net_problem_from_output(variant(), difficulty)
