def analyze_risk(domain_info, open_ports):
    score = 0
    weak_points = []
    if 8080 in open_ports:
        score += 2
        weak_points.append("Port 8080 is open - Possible test interface or admin panel")
    if 21 in open_ports:
        score += 1
        weak_points.append("FTP port (21) is open - Vulnerable to brute force attacks")
    if 3306 in open_ports:
        score += 2
        weak_points.append("MySQL port open - Database exposure risk")
    dnssec = getattr(domain_info, 'dnssec', 'unsigned')
    if dnssec == 'unsigned':
        score += 2
        weak_points.append("DNSSEC is not enabled - Vulnerable to DNS spoofing")
    if 'REDACTED FOR PRIVACY' in str(domain_info):
        score += 1
        weak_points.append("WHOIS information is privacy-protected - Low transparency")
    if score == 0:
        risk_level = "Low"
    elif score <= 3:
        risk_level = "Medium"
    else:
        risk_level = "High"

    return {
        "score": f"{risk_level} Risk (Score: {score})",
        "weak_points": weak_points
    }