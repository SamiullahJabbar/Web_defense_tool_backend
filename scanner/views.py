from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import socket
import whois
from subscription.utils import is_paid_user
from monitor.models import RequestLog
from .risk_analyzer import analyze_risk  
from django.contrib.auth.models import AnonymousUser

# class WebsiteScannerAPIView(APIView):
#     def post(self, request):
#         url = request.data.get("url")
#         ip = request.META.get('REMOTE_ADDR')

#         # ✅ Free Plan: Limit 20 requests per day per IP (anonymous user)
#         today = timezone.now().date()
#         scan_count = RequestLog.objects.filter(ip_address=ip, timestamp__date=today).count()
        
#         if scan_count >= 20:
#             return Response({
#                 "message": "🚫 Free plan scan limit reached (20 per day per IP). Upgrade to Pro for unlimited scans."
#             }, status=status.HTTP_403_FORBIDDEN)

#         try:
#             # ✅ Extract domain from URL
#             domain = url.replace("http://", "").replace("https://", "").split("/")[0]

#             # ✅ Resolve domain to IP
#             try:
#                 ip_address = socket.gethostbyname(domain)
#             except socket.gaierror:
#                 return Response({"error": "⚠️ Failed to resolve domain. Check the URL and try again."}, status=status.HTTP_400_BAD_REQUEST)

#             # ✅ WHOIS Lookup (Handle errors)
#             try:
#                 domain_info = whois.whois(domain)
#             except Exception:
#                 domain_info = "WHOIS lookup failed or domain is private."

#             # ✅ Port Scanning
#             open_ports = []
#             for port in [21, 22, 80, 443, 8080, 3306]:
#                 try:
#                     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
#                         sock.settimeout(1)
#                         result = sock.connect_ex((ip_address, port))
#                         if result == 0:
#                             open_ports.append(port)
#                 except Exception:
#                     continue

#             # ✅ Risk Analysis
#             risk_report = analyze_risk(domain_info, open_ports)

#             # ✅ Security Suggestions
#             suggestions = [
#                 "Enable a Web Application Firewall (WAF) to protect against common attacks.",
#                 "Regularly scan and monitor website traffic for suspicious patterns.",
#                 "Use SSL/TLS encryption to secure website communications.",
#                 "Ensure all website plugins and software are up-to-date.",
#                 "Use strong authentication and access controls to prevent unauthorized access."
#             ]

#             # ✅ Final Response
#             result = {
#                 "url": url,
#                 "domain": domain,
#                 "ip_address": ip_address,
#                 "open_ports": open_ports,
#                 "domain_info": str(domain_info),
#                 "risk_score": risk_report.get('score', 'N/A'),
#                 "weak_points": risk_report.get('weak_points', []),
#                 "defense_suggestions": suggestions
#             }

#             return Response(result, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"error": f"⚠️ Failed to scan website: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)



class WebsiteScannerAPIView(APIView):
    def post(self, request):
        url = request.data.get("url")
        ip = request.META.get('REMOTE_ADDR')

        try:
            # ✅ Extract domain from URL
            domain = url.replace("http://", "").replace("https://", "").split("/")[0]

            # ✅ Resolve domain to IP
            try:
                ip_address = socket.gethostbyname(domain)
            except socket.gaierror:
                return Response({"error": "⚠️ Failed to resolve domain. Check the URL and try again."}, status=status.HTTP_400_BAD_REQUEST)

            # ✅ WHOIS Lookup (Handle errors)
            try:
                domain_info = whois.whois(domain)
            except Exception:
                domain_info = "WHOIS lookup failed or domain is private."

            # ✅ Port Scanning
            open_ports = []
            for port in [21, 22, 80, 443, 8080, 3306]:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(1)
                        result = sock.connect_ex((ip_address, port))
                        if result == 0:
                            open_ports.append(port)
                except Exception:
                    continue

            # ✅ Risk Analysis
            risk_report = analyze_risk(domain_info, open_ports)

            # ✅ Security Suggestions
            suggestions = [
                "Enable a Web Application Firewall (WAF) to protect against common attacks.",
                "Regularly scan and monitor website traffic for suspicious patterns.",
                "Use SSL/TLS encryption to secure website communications.",
                "Ensure all website plugins and software are up-to-date.",
                "Use strong authentication and access controls to prevent unauthorized access."
            ]

            result = {
                "url": url,
                "domain": domain,
                "ip_address": ip_address,
                "open_ports": open_ports,
                "domain_info": str(domain_info),
                "risk_score": risk_report.get('score', 'N/A'),
                "weak_points": risk_report.get('weak_points', []),
                "defense_suggestions": suggestions
            }

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"⚠️ Failed to scan website: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)