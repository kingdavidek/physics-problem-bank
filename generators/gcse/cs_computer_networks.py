"""
GCSE Computer Science – Computer Networks
10 foundational · 10 intermediate · 10 difficult · 22 MCQ bank
Graded practice variants return (question, solution, hint, marks, raw).
Definition-style variants use MCQ/pick; multipart uses inline number_fields.
"""
import random
from generators.shared.utils import (
    make_problem,
    graded_answer_number_fields,
    problem_extra_from_graded_answer,
    proof_steps_answer,
)
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
        if isinstance(raw, dict) and raw.get('type') == 'mcq':
            return make_problem(
                q, s, hint, difficulty, marks, 'gcse', 'cs', 'computer_networks',
                options=raw['options'],
                correct_answer=raw['correct'],
            )
        if isinstance(raw, dict):
            extra = problem_extra_from_graded_answer(raw)
        elif isinstance(raw, (int, float)):
            extra = {
                'correct_answer_raw': _net_raw_number(raw),
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number',
            }
    return make_problem(
        q, s, hint, difficulty, marks, 'gcse', 'cs', 'computer_networks', **extra
    )


def _net_mcq_payload(correct_variants, distractor_groups):
    """Four-option practice MCQ; picks one phrasing per answer and shuffles."""
    variants = correct_variants if isinstance(correct_variants, (tuple, list)) else (correct_variants,)
    groups = [
        (group,) if isinstance(group, str) else tuple(group)
        for group in distractor_groups[:3]
    ]
    correct_text = random.choice(variants)
    max_distractor_len = max(len(max(g, key=len)) for g in groups) if groups else 0
    if len(correct_text) > max_distractor_len:
        shorter = [v for v in variants if len(v) <= max_distractor_len]
        if shorter:
            correct_text = random.choice(shorter)
    distractors = []
    for group in groups:
        if random.random() < 0.55:
            distractors.append(max(group, key=len))
        else:
            distractors.append(random.choice(group))
    if distractors and len(correct_text) > max(len(d) for d in distractors):
        gi = random.randrange(len(groups))
        distractors[gi] = max(groups[gi], key=len)
    pool = [correct_text] + distractors
    random.shuffle(pool)
    letters = 'ABCD'
    correct_letter = letters[pool.index(correct_text)]
    options = [f'{letters[i]}  {pool[i]}' for i in range(len(pool))]
    return {'type': 'mcq', 'options': options, 'correct': correct_letter}


def _net_mcq_options(correct_variants, distractor_groups):
    payload = _net_mcq_payload(correct_variants, distractor_groups)
    return payload['options'], payload['correct']


def _net_pick_from_bank(correct_texts, distractor_texts, pick_count, *, format_hint=None):
    correct_ids = tuple(f'c{i + 1}' for i in range(len(correct_texts)))
    bank = [{'id': cid, 'text': text} for cid, text in zip(correct_ids, correct_texts)]
    for i, text in enumerate(distractor_texts):
        bank.append({'id': f'd{i + 1}', 'text': text})
    random.shuffle(bank)
    return proof_steps_answer(
        correct_ids,
        bank,
        pick_count=pick_count,
        format_hint=format_hint,
    )


def _net_pick_field(correct_texts, distractor_texts, pick_count):
    correct_ids = tuple(f'c{i + 1}' for i in range(len(correct_texts)))
    bank = [{'id': cid, 'text': text} for cid, text in zip(correct_ids, correct_texts)]
    for i, text in enumerate(distractor_texts):
        bank.append({'id': f'd{i + 1}', 'text': text})
    random.shuffle(bank)
    raw = f"pick|{pick_count}|{'|'.join(correct_ids)}"
    return raw, bank, pick_count


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (10)
# ══════════════════════════════════════════════════════════════════════════════

def _net_f1_lan():
    q = "What is a <strong>LAN</strong> (Local Area Network)? Select one correct answer."
    s = (
        "A network covering a <strong>small geographic area</strong> (e.g. one school, "
        "office, or home) with privately owned links."
    )
    return q, s, "LAN = local — usually one building or site.", 1, _net_mcq_payload(
        (
            'A network covering a small geographic area such as one school or home',
            'A Local Area Network covering a small geographic area with privately owned links',
            'A network covering a small geographic area (e.g. one school, office or home)',
        ),
        (
            ('A network covering countries and continents', 'A Wide Area Network spanning cities and countries'),
            ('A single physical cable with no devices attached', 'One cable with no connected computers or switches'),
            ('Software that encrypts files on a hard drive', 'Utility software that encrypts stored files only'),
        ),
    )


def _net_f2_wan():
    q = "How does a <strong>WAN</strong> differ from a LAN? Select one correct answer."
    s = (
        "A <strong>WAN</strong> (Wide Area Network) covers a <strong>large area</strong> "
        "(cities, countries). The internet is the largest WAN."
    )
    return q, s, "WAN uses public/shared infrastructure over long distances.", 1, _net_mcq_payload(
        (
            'A WAN covers a large geographic area such as cities or countries',
            'A Wide Area Network covers a large geographic area over long distances',
            'A WAN covers a large area (cities, countries); the internet is the largest WAN',
        ),
        (
            ('A WAN only covers one building', 'A WAN covers only one room or building like a LAN'),
            ('A WAN has no routers or switches', 'A WAN connects devices with no routers at all'),
            ('A WAN is always wireless with no cables', 'A WAN uses only Wi-Fi with no wired links'),
        ),
    )


def _net_f3_client_server():
    q = (
        "In <strong>client–server</strong>, what is the role of the web browser? "
        "Select one correct answer."
    )
    s = (
        "The <strong>browser is the client</strong> (requests pages). "
        "The <strong>web server is the server</strong> (stores and sends pages)."
    )
    return q, s, "Client requests; server provides a service.", 2, _net_mcq_payload(
        (
            'The client — it requests pages from the server',
            'The client that sends requests to the web server',
            'The client — the browser requests web pages from the server',
        ),
        (
            ('The server — it stores and sends web pages to clients', 'The server that stores pages and responds to every client on the internet only'),
            ('The router — it forwards packets between networks only', 'The router that connects the LAN to the ISP and nothing else'),
            ('The DNS server — it only translates domain names', 'The DNS server that resolves names but never requests pages'),
        ),
    )


def _net_f4_p2p():
    q = "Give <strong>one advantage</strong> of peer-to-peer (P2P) networks. Select one correct answer."
    s = (
        "No dedicated expensive server needed; <strong>easy to set up</strong> for small groups; "
        "files can be shared directly between peers (e.g. local file sharing)."
    )
    return q, s, "P2P: each device can be client and server.", 2, _net_mcq_payload(
        (
            'No dedicated expensive server is needed',
            'Easy to set up for a small group without a central server',
            'Files can be shared directly between peers without a dedicated server',
        ),
        (
            ('Every device must connect through one expensive central server', 'A dedicated server is required for every peer-to-peer connection'),
            ('Data cannot be shared between devices at all', 'No files or resources can be shared between peers'),
            ('Only one device can ever send data at a time globally', 'Only one device worldwide can transmit data in P2P'),
        ),
    )


def _net_f5_star_topology():
    q = (
        "In a <strong>star topology</strong>, all devices connect to a central device. "
        "Select <strong>two</strong> examples of that central device."
    )
    s = "<strong>Switch</strong> or <strong>wireless access point (WAP)</strong> / hub at the centre."
    return q, s, "Star = spokes to a hub; common in school networks.", 2, _net_pick_from_bank(
        (
            'Switch at the centre of the star',
            'Wireless access point (WAP) at the centre',
            'Hub at the centre of the star',
        ),
        (
            'Printer shared by every device on the WAN',
            'Monitor that displays the desktop for all users',
            'CPU inside each workstation only',
        ),
        2,
        format_hint='Select two central devices in a star topology',
    )


def _net_f6_router_role():
    q = "What is the main job of a <strong>router</strong>? Select one correct answer."
    s = (
        "A router <strong>forwards data packets between networks</strong> "
        "(e.g. from your LAN to the internet), choosing the best path."
    )
    return q, s, "Connects LAN to WAN; uses IP addresses.", 2, _net_mcq_payload(
        (
            'Forwards data packets between networks',
            'Forwards data packets between networks (e.g. LAN and internet)',
            'Forwards data packets between networks, choosing the best path using IP addresses',
        ),
        (
            ('Stores web pages for browsers to download', 'Stores every web page permanently for offline browsing'),
            ('Assigns MAC addresses to every NIC in the world', 'Assigns unique MAC addresses to all network cards globally'),
            ('Compresses files before they are saved to disk', 'Reduces file size using ZIP compression on the hard drive'),
        ),
    )


def _net_f7_http():
    q = "Which protocol is used when you view a web page in a browser? Select one correct answer."
    s = "<strong>HTTP</strong> (Hypertext Transfer Protocol) or <strong>HTTPS</strong> if encrypted."
    return q, s, "HTTPS = HTTP + encryption (TLS).", 1, _net_mcq_payload(
        (
            'HTTP or HTTPS',
            'HTTP (Hypertext Transfer Protocol) or HTTPS if encrypted',
            'HTTP for web pages, or HTTPS when the connection is encrypted',
        ),
        (
            ('SMTP for sending email only', 'SMTP (Simple Mail Transfer Protocol) for sending email'),
            ('FTP for printing documents only', 'FTP used only to send jobs to a network printer'),
            ('DNS for storing files on cloud servers', 'DNS protocol that stores files on remote cloud servers'),
        ),
    )


def _net_f8_nic():
    q = "What does a <strong>Network Interface Card (NIC)</strong> do? Select one correct answer."
    s = "Connects a device to a network and provides it with a <strong>MAC address</strong>."
    return q, s, "Built into motherboards or WiFi adapters.", 1, _net_mcq_payload(
        (
            'Connects a device to a network',
            'Connects a device to a network and provides a MAC address',
            'Connects a device to a network and gives it a hardware MAC address',
        ),
        (
            ('Increases the clock speed of the CPU', 'Overclocks the CPU to run programs faster'),
            ('Encrypts all files stored on the hard drive', 'Encrypts every file on the computer automatically'),
            ('Translates domain names into IP addresses', 'Acts as a DNS server translating names to IP addresses'),
        ),
    )


def _net_f9_wifi_wap():
    q = "What does a <strong>Wireless Access Point (WAP)</strong> allow? Select one correct answer."
    s = "Allows devices to connect to a wired LAN <strong>wirelessly</strong> (WiFi)."
    return q, s, "WAP bridges WiFi clients to the switch/router.", 1, _net_mcq_payload(
        (
            'Devices to connect to a wired LAN wirelessly',
            'Wireless devices to connect to a wired LAN using Wi-Fi',
            'Devices to join a wired LAN without cables using Wi-Fi (wireless access point)',
        ),
        (
            ('Only wired Ethernet connections with no radio signal', 'Only cabled connections — Wi-Fi is disabled entirely'),
            ('Devices to browse the web without any router or switch', 'Direct internet access with no router, switch or LAN'),
            ('The CPU to run programs faster than on a wired PC', 'Faster CPU execution than using Ethernet cables'),
        ),
    )


def _net_f10_packet():
    q = "Why is data split into <strong>packets</strong> for transmission? Select one correct answer."
    s = (
        "Packets can take <strong>different routes</strong>, share bandwidth fairly, "
        "and errors only require resending small chunks — not the whole file."
    )
    return q, s, "Packet switching is how the internet works.", 2, _net_mcq_payload(
        (
            'Packets can take different routes and only lost packets need resending',
            'Data is split so packets can share the network and take different routes',
            'Packets can take different routes; if one is lost only that small part is resent',
        ),
        (
            ('One dedicated phone line must stay open for the whole transfer', 'A single circuit must remain open for the entire file transfer'),
            ('Routers are not used when data is packet switched', 'Packet switching works without any routers on the internet'),
            ('The whole file must be resent if any single bit is corrupted', 'Any error requires resending the entire file from the start'),
        ),
    )


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
        "for a school network. Select one correct answer."
    )
    s = (
        "If one cable to a classroom fails, <strong>only that device is affected</strong>; "
        "bus failure on the backbone can affect many machines."
    )
    return q, s, "Star: fault isolation; bus: single backbone risk.", 2, _net_mcq_payload(
        (
            'If one cable fails, only that device is affected',
            'A fault on one link usually affects only that device, not the whole network',
            'If one cable to a classroom fails, only that device is affected — not every machine',
        ),
        (
            ('If the backbone fails, only one device stops working', 'A bus backbone failure affects only one computer'),
            ('Star topology needs no central switch or hub', 'Star networks do not use a central switch at all'),
            ('Bus topology is always faster than star for every school', 'Bus is always faster than star in all school networks'),
        ),
    )


def _net_i2_switch_vs_hub():
    q = "How does a <strong>switch</strong> differ from an old <strong>hub</strong>? Select one correct answer."
    s = (
        "A switch sends data <strong>only to the intended device</strong> (learns MAC addresses). "
        "A hub <strong>broadcasts</strong> to all ports — wasteful and slower."
    )
    return q, s, "Switches are smarter; hubs are largely obsolete.", 2, _net_mcq_payload(
        (
            'A switch sends data only to the intended device',
            'A switch forwards frames to the correct device using a MAC address table',
            'A switch sends data only to the intended device; a hub broadcasts to all ports',
        ),
        (
            ('A hub sends data only to the intended device', 'A hub learns MAC addresses and targets one port only'),
            ('A switch broadcasts every frame to all ports always', 'A switch broadcasts all traffic to every connected port'),
            ('A hub is faster because it uses IP routing', 'A hub routes packets using IP addresses faster than a switch'),
        ),
    )


def _net_i3_dns():
    q = "What is <strong>DNS</strong> and why is it needed? Select one correct answer."
    s = (
        "<strong>Domain Name System</strong> — translates human-friendly names "
        "(e.g. www.bbc.co.uk) into <strong>IP addresses</strong> computers use."
    )
    return q, s, "Like a phone book for the internet.", 2, _net_mcq_payload(
        (
            'Translates domain names into IP addresses',
            'Domain Name System — translates names like www.bbc.co.uk into IP addresses',
            'DNS translates human-friendly domain names into IP addresses computers use to route packets',
        ),
        (
            ('Encrypts web traffic between browser and server', 'Encrypts all HTTP traffic using TLS automatically'),
            ('Assigns MAC addresses when a NIC is manufactured', 'Assigns hardware MAC addresses to every network card'),
            ('Splits files into packets before transmission', 'Divides large files into packets for the internet'),
        ),
    )


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
    q = (
        "Select <strong>two</strong> correct statements comparing "
        "<strong>MAC addresses</strong> and <strong>IP addresses</strong>."
    )
    s = (
        "<strong>MAC</strong> — fixed hardware address on the NIC (local delivery on LAN). "
        "<strong>IP</strong> — logical address for routing across networks (can change)."
    )
    return q, s, "MAC = layer 2; IP = layer 3 (routing).", 3, _net_pick_from_bank(
        (
            'A MAC address is assigned to the NIC hardware',
            'An IP address is a logical address used for routing across networks',
            'An IP address can change; a MAC address is usually fixed to the NIC',
        ),
        (
            'A MAC address is used to route packets across the entire internet',
            'An IP address is burned permanently into the CPU during manufacture',
            'MAC and IP addresses are always identical for every device',
        ),
        2,
        format_hint='Select two correct statements about MAC and IP addresses',
    )


def _net_i6_tcp_udp():
    q = (
        "When streaming video, would <strong>TCP</strong> or <strong>UDP</strong> often be preferred? "
        "Select one correct answer."
    )
    s = (
        "Often <strong>UDP</strong> — occasional lost packets are acceptable; "
        "TCP’s retransmission can cause lag. (TCP used when every byte must arrive, e.g. web pages.)"
    )
    return q, s, "TCP reliable; UDP faster but no guarantee.", 3, _net_mcq_payload(
        (
            'UDP — some packet loss is acceptable and lower delay matters',
            'UDP — occasional lost packets are acceptable; retransmission can cause lag',
            'UDP is often preferred because small delays matter more than perfect delivery for live video',
        ),
        (
            ('TCP — every packet must arrive in order with no loss ever', 'TCP because live video requires every packet with guaranteed order'),
            ('Neither — video always uses HTTP only with no transport protocol', 'Video streaming uses HTTP only with no TCP or UDP layer'),
            ('UDP — it encrypts all video traffic automatically', 'UDP because it encrypts video streams without any other protocol'),
        ),
    )


def _net_i7_email_protocols():
    q = (
        "Which protocol <strong>sends</strong> email from your client to the mail server? "
        "Select one correct answer."
    )
    s = "<strong>SMTP</strong> (Simple Mail Transfer Protocol) sends outgoing mail."
    return q, s, "POP/IMAP receive mail from server to client.", 2, _net_mcq_payload(
        (
            'SMTP',
            'SMTP (Simple Mail Transfer Protocol)',
            'SMTP — Simple Mail Transfer Protocol sends outgoing mail to the mail server',
        ),
        (
            ('POP3', 'POP3 — Post Office Protocol for downloading mail to one device'),
            ('IMAP', 'IMAP — Internet Message Access Protocol for syncing mail on the server'),
            ('HTTP', 'HTTP — Hypertext Transfer Protocol for browsing websites'),
        ),
    )


def _net_i8_https():
    q = "What extra protection does <strong>HTTPS</strong> provide over HTTP? Select one correct answer."
    s = (
        "<strong>Encryption</strong> (TLS) — data is scrambled in transit so eavesdroppers "
        "cannot easily read passwords or card details."
    )
    return q, s, "Look for the padlock in the browser.", 2, _net_mcq_payload(
        (
            'Encryption of data in transit',
            'Encryption (TLS) so data cannot easily be read if intercepted',
            'Encryption using TLS/SSL so passwords and card details are protected in transit',
        ),
        (
            ('Faster download speeds on all web pages', 'Higher bandwidth that makes every page load faster'),
            ('More IP addresses for every website', 'Extra IPv4 addresses assigned to each web server'),
            ('Larger maximum packet size on the network', 'Bigger packets that carry twice as much data per frame'),
        ),
    )


def _net_i9_cloud():
    q = "Give <strong>two examples</strong> of cloud services a school might use."
    s = "Examples: <strong>Google Classroom / Microsoft 365</strong>, <strong>cloud backup</strong>, <strong>online file storage (OneDrive)</strong>."
    return q, s, "Cloud = services over the internet, not local servers only.", 2, _net_pick_from_bank(
        (
            'Google Classroom or Microsoft 365 online',
            'Cloud backup of school files',
            'Online file storage such as OneDrive or Google Drive',
        ),
        (
            'A spreadsheet saved only on one USB stick in a drawer',
            'Programs installed only on a single offline PC with no internet',
            'Files stored on the CPU cache inside the processor',
        ),
        2,
        format_hint='Select two cloud services a school might use',
    )


def _net_i10_bus_topology():
    q = "Describe one <strong>disadvantage</strong> of a bus topology. Select one correct answer."
    s = (
        "The <strong>main cable (backbone)</strong> is a single point of failure — "
        "if it breaks, the whole network can stop."
    )
    return q, s, "Terminator resistors needed at ends; collisions on old Ethernet bus.", 2, _net_mcq_payload(
        (
            'The main backbone cable is a single point of failure',
            'If the main cable breaks, the whole network can stop working',
            'The shared backbone is a single point of failure — a break affects all devices',
        ),
        (
            ('Every device needs its own fibre link to the internet', 'Each computer requires a separate transatlantic fibre cable'),
            ('Bus topology always uses more cable than a full mesh', 'Bus uses more cabling than a full mesh between every node'),
            ('Only one device can ever be connected to a bus network', 'Bus topology allows exactly one computer and no others'),
        ),
    )


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (10)
# ══════════════════════════════════════════════════════════════════════════════

def _net_d1_packet_switching():
    q = (
        "Select <strong>three</strong> correct statements about "
        "<strong>packet switching</strong> when a large file travels across the internet."
    )
    s = (
        "File is split into <strong>packets</strong> with headers (source/destination IP). "
        "Routers forward packets along <strong>different paths</strong>; "
        "packets are <strong>reassembled</strong> at the destination. Failed packets can be resent."
    )
    return q, s, "Contrast with circuit switching (dedicated line).", 4, _net_pick_from_bank(
        (
            'The file is split into packets with header information',
            'Packets may travel by different routes across the network',
            'Packets are reassembled at the destination',
            'Lost packets can be resent without resending the whole file',
        ),
        (
            'One dedicated circuit must stay open for the entire transfer',
            'All packets must always follow exactly the same fixed path',
            'Packet switching means routers are never used on the internet',
        ),
        3,
        format_hint='Select three correct statements about packet switching',
    )


def _net_d2_firewall():
    q = "What does a <strong>firewall</strong> do on a school network? Select one correct answer."
    s = (
        "Monitors and <strong>filters traffic</strong> — blocks unauthorised access, "
        "dangerous ports, or sites against school policy."
    )
    return q, s, "Hardware or software barrier between trusted/untrusted networks.", 3, _net_mcq_payload(
        (
            'Monitors and filters network traffic for security',
            'Filters traffic — blocks unauthorised access and dangerous ports or sites',
            'Monitors and filters traffic between trusted and untrusted networks for security',
        ),
        (
            ('Assigns IP addresses to every device automatically', 'Runs DHCP to assign IP addresses to all pupils'),
            ('Compresses all files before they are uploaded to the cloud', 'Reduces file size using ZIP before cloud upload'),
            ('Increases Wi-Fi signal strength through walls', 'Boosts wireless signal so it passes through all walls'),
        ),
    )


def _net_d3_nat():
    q = (
        "A home router shows public IP <strong>81.99.x.x</strong> but your laptop has "
        "<strong>192.168.0.15</strong>. Select one correct explanation."
    )
    s = (
        "<strong>192.168.x.x</strong> is a <strong>private</strong> LAN address (NAT). "
        "The router uses <strong>NAT</strong> so many devices share one public IP on the internet."
    )
    return q, s, "Private ranges: 10.x, 172.16–31, 192.168.x.", 3, _net_mcq_payload(
        (
            '192.168.x.x is a private LAN address; the router uses NAT to share one public IP',
            'The laptop has a private address; NAT lets many devices share the router’s public IP',
            '192.168.0.15 is private on the LAN; NAT translates so many devices use one public IP online',
        ),
        (
            ('192.168.0.15 is the public IP seen by every website worldwide', 'The laptop’s address is public on the whole internet'),
            ('81.99.x.x is only used inside the home LAN with no internet access', 'The router’s public IP is never used on the internet'),
            ('NAT means every device gets its own public IP address', 'NAT assigns a separate public IP to every phone and laptop'),
        ),
    )


def _net_d4_mesh_topology():
    q = (
        "Why might a <strong>full mesh</strong> be used for critical links between two city offices? "
        "Select one correct answer."
    )
    s = (
        "Every node has <strong>multiple paths</strong> — if one link fails, "
        "traffic can reroute; <strong>high reliability</strong> (expensive)."
    )
    return q, s, "Mesh = redundant connections.", 3, _net_mcq_payload(
        (
            'Multiple paths give high reliability if one link fails',
            'Redundant links let traffic reroute if one connection fails',
            'Every node has multiple paths — traffic can reroute for high reliability',
        ),
        (
            ('It is the cheapest topology for long-distance links', 'Full mesh is always the lowest-cost option between cities'),
            ('It uses less cable than a single bus backbone', 'Mesh needs fewer cables than one shared bus line'),
            ('It prevents any encryption from being used on the link', 'Mesh links cannot use HTTPS or TLS encryption'),
        ),
    )


def _net_d5_layered():
    q = "Why is networking described in <strong>layers</strong> (e.g. TCP/IP model)? Select one correct answer."
    s = (
        "Each layer has a <strong>specific job</strong> (link, internet, transport, application); "
        "manufacturers can update one layer without redesigning everything."
    )
    return q, s, "GCSE: know application + transport + network + link idea.", 3, _net_mcq_payload(
        (
            'Each layer has a specific job; one layer can be updated independently',
            'Layers divide tasks so hardware and software can change one layer without redesigning all',
            'Each layer has a specific role; manufacturers can update one layer without changing everything',
        ),
        (
            ('Layers mean only one protocol can ever be used on the internet', 'The layered model allows only HTTP and no other protocols'),
            ('Layers remove the need for IP addresses on every packet', 'Layering means routers do not use IP addresses'),
            ('Layers are only used for wireless networks, not wired Ethernet', 'The TCP/IP model applies to Wi-Fi only, not cabled LANs'),
        ),
    )


def _net_d6_four_layer_send():
    q = (
        "You click a link to a website. Select <strong>two</strong> protocols likely used "
        "— one from the <strong>application layer</strong> and one from the <strong>transport layer</strong>."
    )
    s = (
        "Application: <strong>HTTP/HTTPS</strong>. Transport: <strong>TCP</strong> "
        "(reliable delivery). Network: IP routes packets."
    )
    return q, s, "Stack: HTTP over TCP over IP over Ethernet/WiFi.", 3, _net_pick_from_bank(
        (
            'HTTP or HTTPS (application layer)',
            'TCP (transport layer)',
        ),
        (
            'DNS is the transport layer protocol for every web page',
            'MAC address assignment is the application layer for browsing',
            'FTP is the only protocol used when clicking any hyperlink',
            'UDP is always used instead of TCP for reliable web page delivery',
        ),
        2,
        format_hint='Select one application-layer and one transport-layer protocol',
    )


def _net_d7_bandwidth_latency():
    q = (
        "A gamer has high <strong>bandwidth</strong> but high <strong>latency</strong>. "
        "Select one correct explanation of why online games might still lag."
    )
    s = (
        "<strong>Latency</strong> (ping/delay) affects reaction time — packets take long to return "
        "even if bandwidth (capacity) is large."
    )
    return q, s, "Bandwidth ≠ speed of response; latency = delay.", 3, _net_mcq_payload(
        (
            'High latency means long delay even if bandwidth is large',
            'Latency (ping delay) affects response time — packets take long to return',
            'High latency causes lag because packets take a long time to make the round trip',
        ),
        (
            ('High bandwidth always removes all lag in every online game', 'Large bandwidth guarantees zero ping in all games'),
            ('Latency only affects download speed, not real-time games', 'Ping delay matters for files but not for live multiplayer'),
            ('Games use only UDP so latency and bandwidth are identical', 'Bandwidth and latency mean exactly the same thing for games'),
        ),
    )


def _net_d8_vlan_scenario():
    q = (
        "A school wants staff WiFi separate from guest WiFi for security. "
        "Select one correct network approach."
    )
    s = (
        "Separate <strong>SSIDs / VLANs</strong> or subnets with firewall rules — "
        "guests cannot access internal file servers."
    )
    return q, s, "Segmentation limits access between groups.", 3, _net_mcq_payload(
        (
            'Separate SSIDs or VLANs with firewall rules between them',
            'Use separate SSIDs/VLANs or subnets so guests cannot reach internal servers',
            'Segment the network with VLANs or SSIDs and firewall rules between staff and guest Wi-Fi',
        ),
        (
            ('Use one open Wi-Fi network with no password for everyone', 'Share one open SSID with no encryption for staff and guests'),
            ('Remove all routers so only wired PCs can access the internet', 'Disable Wi-Fi entirely and remove every wireless access point'),
            ('Assign the same admin password to every pupil laptop', 'Give every student the staff administrator password'),
        ),
    )


def _net_d9_pop_imap():
    q = "Compare <strong>POP3</strong> and <strong>IMAP</strong> for reading email. Select one correct answer."
    s = (
        "<strong>POP3</strong> often downloads mail to one device (may delete from server). "
        "<strong>IMAP</strong> keeps mail on server — syncs across phone, laptop, webmail."
    )
    return q, s, "IMAP better for multiple devices.", 3, _net_mcq_payload(
        (
            'IMAP keeps mail on the server and syncs across devices',
            'IMAP syncs mail on the server across phone, laptop and webmail',
            'IMAP leaves mail on the server so multiple devices stay in sync; POP3 often downloads to one device',
        ),
        (
            ('POP3 syncs mail across every device from the server', 'POP3 keeps all messages synced on the server for all devices'),
            ('IMAP deletes every message from the server immediately', 'IMAP always removes mail from the server after one download'),
            ('Both POP3 and IMAP send outgoing mail to other servers', 'POP3 and IMAP are protocols for sending email with SMTP'),
        ),
    )


def _net_d10_traceroute_concept():
    q = "What information does a <strong>traceroute</strong> (tracert) tool show? Select one correct answer."
    s = (
        "The <strong>route and routers (hops)</strong> packets take to reach a host, "
        "with <strong>delay at each hop</strong> — useful for diagnosing network problems."
    )
    return q, s, "Each hop is a router along the path.", 2, _net_mcq_payload(
        (
            'The route and delay at each router hop to the destination',
            'The routers (hops) packets pass through and delay at each hop',
            'The path packets take to a host, listing each router hop and the delay at each step',
        ),
        (
            ('The MAC address of every website on the internet', 'A list of MAC addresses for all web servers globally'),
            ('The amount of free disk space on the remote server', 'How much storage is free on the destination computer'),
            ('The encryption key used for HTTPS on that website', 'The TLS private key used to encrypt the web page'),
        ),
    )


def _net_d11_wireless_security():
    q = (
        "Select <strong>two</strong> reasons a home WiFi network should use "
        "<strong>WPA2/WPA3</strong> with a strong password instead of an open network."
    )
    s = (
        "Encryption prevents nearby devices from <strong>reading traffic</strong> or "
        "<strong>joining the LAN</strong> without the key — reduces eavesdropping and unauthorised access."
    )
    return q, s, "Open WiFi = anyone on the same airwaves can intercept unencrypted data.", 3, _net_pick_from_bank(
        (
            'Encryption prevents nearby devices reading your traffic',
            'A password stops unauthorised devices joining your LAN',
            'Reduces eavesdropping on data sent over the wireless link',
        ),
        (
            'Open WiFi is always faster than encrypted WiFi for every device',
            'WPA2 removes the need for any router or access point hardware',
            'Encryption means you never need to update router firmware',
        ),
        2,
        format_hint='Select two reasons to use WPA2/WPA3 instead of open WiFi',
    )


def _net_d12_http_status():
    q = (
        "A browser shows <strong>404 Not Found</strong> for one page and "
        "<strong>500 Internal Server Error</strong> for another.<br><br>"
        "Select <strong>two</strong> correct statements explaining the difference."
    )
    s = (
        "<strong>404:</strong> client requested a URL/resource that <strong>does not exist</strong> on the server. "
        "<strong>500:</strong> server received the request but <strong>failed while processing</strong> it."
    )
    return q, s, "4xx = client-side problem; 5xx = server-side failure.", 3, _net_pick_from_bank(
        (
            '404 means the requested resource does not exist on the server',
            '500 means the server failed while processing a valid request',
            '404 is a client error; 500 is a server error',
        ),
        (
            '404 means the server crashed while processing the page',
            '500 means the user typed the URL incorrectly in every case',
            'Both codes mean the internet connection is completely offline',
        ),
        2,
        format_hint='Select two correct statements about 404 and 500 status codes',
    )


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
    lan_raw, lan_bank, lan_pick = _net_pick_field(
        (
            'LAN — devices are connected over a small geographical area (one home)',
        ),
        (
            'WAN — because the router connects to the internet',
            'WAN — because Wi-Fi is used instead of Ethernet cables',
            'LAN — because it covers several countries through the ISP',
        ),
        1,
    )
    wifi_adv_raw, wifi_adv_bank, wifi_adv_pick = _net_pick_field(
        (
            'No cables needed — less mess and cheaper to add devices',
            'Devices are portable and can move around the home',
            'Easy to connect phones, tablets and many wireless devices',
        ),
        (
            'Always faster than wired Ethernet in every room',
            'Impossible for anyone to intercept the wireless signal',
            'Requires no router or access point hardware at all',
        ),
        2,
    )
    wifi_dis_raw, wifi_dis_bank, wifi_dis_pick = _net_pick_field(
        (
            'Signal can be weaker or unreliable through walls and at distance',
            'Generally slower than a wired Ethernet connection',
            'Less secure — the signal can be intercepted so encryption is needed',
        ),
        (
            'Wi-Fi always uses more cables than wired Ethernet',
            'Wireless connections cannot work with more than one device',
            'Wi-Fi removes the need for a password on the router',
        ),
        2,
    )
    return q, s, "LAN = small area; Wi-Fi trades convenience for speed/security.", 6, graded_answer_number_fields(
        (lan_raw, wifi_adv_raw, wifi_dis_raw),
        ('LAN or WAN', 'Two Wi-Fi advantages', 'Two Wi-Fi disadvantages'),
        field_types=('pick', 'pick', 'pick'),
        field_options=(lan_bank, wifi_adv_bank, wifi_dis_bank),
        field_pick_counts=(lan_pick, wifi_adv_pick, wifi_dis_pick),
        row_sizes=(1, 1, 1),
        group_labels=('(a)', '(b)', '(c)'),
        inline_sections=True,
    )


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
    proto_raw, proto_bank, proto_pick = _net_pick_field(
        (
            'A set of rules governing how devices communicate over a network',
        ),
        (
            'A type of cable used only in bus topology networks',
            'The physical MAC address printed on every monitor',
            'A program that compresses files into ZIP archives',
        ),
        1,
    )
    https_raw, https_bank, https_pick = _net_pick_field(
        (
            'HTTPS — it adds encryption (TLS/SSL) so intercepted data cannot easily be read',
        ),
        (
            'HTTP — it adds encryption automatically on every web page',
            'FTP — it encrypts passwords using DNS lookups only',
            'SMTP — it sends web pages securely without any browser',
        ),
        1,
    )
    header_raw, header_bank, header_pick = _net_pick_field(
        (
            'Source address',
            'Destination address',
            'Packet or sequence number',
            'Packets can take different routes; only lost packets need resending',
        ),
        (
            'Screen resolution of the user\'s monitor',
            'The colour of icons on the desktop',
            'The price of the laptop used to browse the web',
        ),
        3,
    )
    return q, s, "Protocol = rules; HTTPS = HTTP + encryption; packets = small routed chunks.", 6, graded_answer_number_fields(
        (proto_raw, https_raw, header_raw),
        ('Protocol definition', 'Secure web protocol', 'Packets and headers'),
        field_types=('pick', 'pick', 'pick'),
        field_options=(proto_bank, https_bank, header_bank),
        field_pick_counts=(proto_pick, https_pick, header_pick),
        row_sizes=(1, 1, 1),
        group_labels=('(a)', '(b)', '(c)'),
        inline_sections=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# MCQ BANK (22)
# ══════════════════════════════════════════════════════════════════════════════

_NET_MCQ_BANK = [
    {"q": "A network covering one school building is usually a:",
     "correct": (
         "LAN",
         "A Local Area Network (LAN)",
         "A Local Area Network covering a small geographic area such as one school building",
     ),
     "wrong": (
         ("WAN", "A Wide Area Network spanning cities and countries"),
         ("PAN only", "A Personal Area Network only, never used for a whole building"),
         ("VPN", "A Virtual Private Network tunnel, not a physical local network type"),
     ),
     "marks": 1,
     "sol": "<strong>LAN</strong> = local area.",
     "hint": "Small geographic area."},
    {"q": "In client–server, the server:",
     "correct": (
         "Provides a service to clients",
         "The server provides a service to clients",
         "The server provides a service or resource that clients request over the network",
     ),
     "wrong": (
         ("Only requests data", "Only requests data from other devices and never responds"),
         ("Cannot use the internet", "Cannot connect to or use the internet at all"),
         ("Is always wireless", "Must always be a wireless device with no wired connection"),
     ),
     "marks": 1,
     "sol": "Server <strong>provides services</strong>.",
     "hint": "Client asks; server responds."},
    {"q": "All devices connect to a central switch in:",
     "correct": (
         "Star topology",
         "A star topology with a central switch",
         "Star topology where every device connects to a central switch or hub",
     ),
     "wrong": (
         ("Bus topology", "Bus topology with all devices on one shared backbone cable"),
         ("Ring only", "Ring topology only, with devices linked in a closed loop"),
         ("Mesh only", "Full mesh topology only, with every device linked to every other"),
     ),
     "marks": 1,
     "sol": "<strong>Star</strong> topology.",
     "hint": "Spokes from centre."},
    {"q": "DNS translates domain names into:",
     "correct": (
         "IP addresses",
         "Domain names into IP addresses",
         "Human-readable domain names into numeric IP addresses for routing",
     ),
     "wrong": (
         ("MAC addresses only", "Domain names into MAC addresses only, never IP addresses"),
         ("HTML code", "Domain names into HTML source code for web pages"),
         ("WiFi passwords", "Domain names into WiFi network passwords for authentication"),
     ),
     "marks": 2,
     "sol": "DNS → <strong>IP addresses</strong>.",
     "hint": "Name to numeric address."},
    {"q": "Which device forwards packets between your home LAN and the internet?",
     "correct": (
         "Router",
         "A router",
         "A router that forwards packets between your home LAN and the internet",
     ),
     "wrong": (
         ("Printer", "A printer that outputs documents on paper only"),
         ("Monitor", "A monitor that displays output to the user only"),
         ("Keyboard", "A keyboard that accepts typed input from the user only"),
     ),
     "marks": 1,
     "sol": "<strong>Router</strong> connects networks.",
     "hint": "Gateway to ISP."},
    {"q": "HTTPS compared with HTTP adds:",
     "correct": (
         "Encryption",
         "Encryption of data in transit",
         "Encryption (TLS) so data is protected in transit between browser and server",
     ),
     "wrong": (
         ("Faster cables", "Physically faster network cables between client and server"),
         ("More IP addresses", "Additional IP addresses assigned to every web page"),
         ("Larger packets only", "Larger packet sizes only, with no security change"),
     ),
     "marks": 2,
     "sol": "<strong>Encryption</strong> in transit.",
     "hint": "S = secure."},
    {"q": "SMTP is used mainly to:",
     "correct": (
         "Send email",
         "Send email from a client to a mail server",
         "Send email messages from a client to a mail server (Simple Mail Transfer Protocol)",
     ),
     "wrong": (
         ("Browse websites", "Browse websites and load HTML pages in a web browser"),
         ("Resolve DNS", "Resolve domain names to IP addresses using DNS lookups"),
         ("Print documents", "Send documents to a printer for physical output"),
     ),
     "marks": 2,
     "sol": "<strong>Send</strong> mail.",
     "hint": "Simple Mail Transfer Protocol."},
    {"q": "A MAC address is:",
     "correct": (
         "Built into the NIC hardware",
         "A hardware address built into the NIC",
         "A hardware address built into the Network Interface Card (NIC), usually fixed at manufacture",
     ),
     "wrong": (
         ("Assigned by a website", "Assigned dynamically by a website when you visit it"),
         ("The same as a URL", "The same as a URL used to locate a web page"),
         ("Only used on WANs", "Only used on Wide Area Networks, never on local LANs"),
     ),
     "marks": 2,
     "sol": "MAC is a <strong>hardware</strong> address.",
     "hint": "48-bit, hex pairs."},
    {"q": "The internet is best described as:",
     "correct": (
         "A WAN of interconnected networks",
         "A wide area network of interconnected networks",
         "A global WAN of interconnected networks using shared public infrastructure",
     ),
     "wrong": (
         ("A single LAN", "A single Local Area Network in one building only"),
         ("One physical cable", "One physical cable connecting every device directly"),
         ("Only WiFi", "A wireless-only network with no wired links anywhere"),
     ),
     "marks": 1,
     "sol": "Internet = global <strong>WAN</strong>.",
     "hint": "Network of networks."},
    {"q": "Packet switching means:",
     "correct": (
         "Data split into packets that may take different routes",
         "Messages split into packets routed independently",
         "Data is split into packets that may take different routes and are reassembled at the destination",
     ),
     "wrong": (
         ("One dedicated line per call forever", "One dedicated phone line reserved for the entire call duration"),
         ("No routers used", "Data travels with no routers or forwarding devices involved"),
         ("Only wireless transmission", "Data sent only by wireless radio with no wired links"),
     ),
     "marks": 2,
     "sol": "Packets <strong>routed independently</strong>.",
     "hint": "Reassembled at end."},
    {"q": "A switch improves on a hub because it:",
     "correct": (
         "Sends frames to the correct device",
         "Forwards frames only to the intended device",
         "Uses a MAC address table to send frames to the correct device instead of broadcasting to all ports",
     ),
     "wrong": (
         ("Broadcasts to every port always", "Broadcasts every frame to every port on the network always"),
         ("Replaces the need for IP", "Replaces IP addresses so devices need no network layer addressing"),
         ("Only works on WAN", "Only operates on Wide Area Networks, not local LANs"),
     ),
     "marks": 2,
     "sol": "Targeted delivery using MAC table.",
     "hint": "Less unnecessary traffic."},
    {"q": "TCP is typically chosen when:",
     "correct": (
         "Reliable, ordered delivery is required",
         "Reliable ordered delivery of data is needed",
         "Reliable, ordered delivery is required with retransmission of lost packets",
     ),
     "wrong": (
         ("Some packet loss is fine for live video only", "Some packet loss is acceptable only for live video streams"),
         ("DNS lookups run", "DNS domain name lookups are performed on the network"),
         ("MAC addresses are assigned", "MAC addresses are assigned to network interface cards"),
     ),
     "marks": 2,
     "sol": "TCP = <strong>reliable</strong>.",
     "hint": "Retransmits lost packets."},
    {"q": "Cloud storage means files are kept:",
     "correct": (
         "On remote servers accessed via the internet",
         "Files stored on remote internet servers",
         "Files kept on remote servers accessed over the internet (e.g. Google Drive, OneDrive)",
     ),
     "wrong": (
         ("Only on one USB stick", "Only on one USB stick with no network access at all"),
         ("In the CPU cache", "In the CPU cache memory inside the processor chip"),
         ("On a printer", "On a printer's internal storage with no remote access"),
     ),
     "marks": 1,
     "sol": "Remote <strong>internet servers</strong>.",
     "hint": "Google Drive, OneDrive, etc."},
    {"q": "A valid IPv4 address has:",
     "correct": (
         "Four numbers 0–255 separated by dots",
         "Four octets (0–255) in dotted decimal",
         "Four numbers from 0 to 255 separated by dots (dotted decimal, e.g. 192.168.1.1)",
     ),
     "wrong": (
         ("Eight hex digits only", "Exactly eight hexadecimal digits with no dot separators"),
         ("Three letters and a slash", "Three letters followed by a slash character only"),
         ("Six MAC pairs", "Six pairs of hexadecimal digits like a MAC address"),
     ),
     "marks": 2,
     "sol": "Four octets, e.g. 10.0.0.1.",
     "hint": "Dotted decimal."},
    {"q": "A firewall’s role is to:",
     "correct": (
         "Filter network traffic for security",
         "Filter or block network traffic based on rules",
         "Filter network traffic between trusted and untrusted networks for security",
     ),
     "wrong": (
         ("Increase screen resolution", "Increase the screen resolution of the monitor display"),
         ("Store emails permanently", "Store email messages permanently on the local disk"),
         ("Assign domain names", "Assign human-readable domain names to IP addresses"),
     ),
     "marks": 2,
     "sol": "<strong>Filter/block</strong> traffic.",
     "hint": "Security barrier."},
    {"q": "UDP is often chosen for live video streaming because:",
     "correct": (
         "It is faster with less overhead and some loss may be acceptable",
         "Lower overhead; some packet loss may be acceptable",
         "It is faster with less overhead and occasional packet loss may be acceptable for live video",
     ),
     "wrong": (
         ("It guarantees every packet arrives in order", "It guarantees every packet arrives in the correct order"),
         ("It encrypts all traffic automatically", "It automatically encrypts all network traffic without TLS"),
         ("It replaces IP addresses", "It replaces IP addresses with MAC addresses for routing"),
     ),
     "marks": 2,
     "sol": "UDP is <strong>lightweight</strong>; small delays matter more than perfect delivery.",
     "hint": "Contrast with TCP retransmission."},
    {"q": "Bluetooth is typically used for:",
     "correct": (
         "Short-range personal area networks",
         "Short-range PAN connections between devices",
         "Short-range personal area networks (PAN) such as headphones, phones and peripherals",
     ),
     "wrong": (
         ("Transatlantic fibre cables only", "Transatlantic undersea fibre optic cables only"),
         ("Assigning domain names", "Assigning domain names to IP addresses on the internet"),
         ("Compiling programs", "Compiling source code into executable machine code"),
     ),
     "marks": 1,
     "sol": "<strong>PAN</strong> — headphones, phones, peripherals.",
     "hint": "Low power, short distance."},
    {"q": "In peer-to-peer (P2P) networks:",
     "correct": (
         "Devices can act as both client and server",
         "Peers can be both client and server",
         "Devices can act as both client and server, sharing resources directly with other peers",
     ),
     "wrong": (
         ("Only one dedicated server exists", "Only one dedicated central server exists for all devices"),
         ("No data is shared", "No data or files are ever shared between connected devices"),
         ("DNS is not used", "DNS is never used to resolve names in peer-to-peer networks"),
     ),
     "marks": 2,
     "sol": "Peers <strong>share resources directly</strong>.",
     "hint": "Contrast with client–server."},
    {"q": "HTTP is mainly used for:",
     "correct": (
         "Transferring web pages and resources",
         "Requesting and transferring web pages",
         "Transferring web pages and resources between a browser and a web server",
     ),
     "wrong": (
         ("Sending email only", "Sending email messages between mail servers only"),
         ("Resolving domain names", "Resolving domain names to IP addresses using DNS"),
         ("Printing documents", "Sending documents to a printer for physical output"),
     ),
     "marks": 1,
     "sol": "<strong>Web communication</strong> between browser and server.",
     "hint": "HyperText Transfer Protocol."},
    {"q": "A Network Interface Card (NIC) provides:",
     "correct": (
         "A connection to a network",
         "A hardware connection to a network",
         "A hardware connection to a network, with a unique MAC address for the device",
     ),
     "wrong": (
         ("Extra RAM for the CPU", "Extra RAM memory installed directly for the CPU to use"),
         ("A graphical desktop", "A graphical desktop environment for the user interface"),
         ("Antivirus scanning only", "Antivirus scanning of files with no network capability"),
     ),
     "marks": 2,
     "sol": "NIC links the device to a <strong>network</strong>.",
     "hint": "Built-in or add-on; has a MAC address."},
    {"q": "FTP is commonly used to:",
     "correct": (
         "Transfer files between computers",
         "Transfer files between systems over a network",
         "Transfer files between computers over a network (File Transfer Protocol)",
     ),
     "wrong": (
         ("Browse social media feeds", "Browse social media feeds and scroll through posts"),
         ("Encrypt all web traffic", "Encrypt all web traffic between browser and server"),
         ("Assign IP addresses automatically", "Assign IP addresses automatically to devices on a LAN"),
     ),
     "marks": 2,
     "sol": "<strong>File transfer</strong> between systems.",
     "hint": "File Transfer Protocol."},
    {"q": "In a bus topology, if the main cable fails:",
     "correct": (
         "The whole network may stop working",
         "The entire network may fail",
         "The whole network may stop working because all devices share one backbone cable",
     ),
     "wrong": (
         ("Only one device is affected", "Only one device is affected while all others keep working"),
         ("Traffic is automatically encrypted", "All network traffic is automatically encrypted for security"),
         ("The network becomes a star", "The network automatically reconfigures into a star topology"),
     ),
     "marks": 2,
     "sol": "Shared backbone — <strong>single point of failure</strong>.",
     "hint": "All devices connect to one central line."},
]


def computer_networks_mcq():
    item = random.choice(_NET_MCQ_BANK)
    opts, ans = _net_mcq_options(item["correct"], item["wrong"])
    return item["q"], item["sol"], item["hint"], item["marks"], opts, ans


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
