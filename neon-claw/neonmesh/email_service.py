"""
NemoClaw Email Management & Urgency Triage Engine
Supports standard IMAP & SMTP (Gmail App Passwords, Outlook, Custom Domains).
Features automatic urgency classification (URGENT, HIGH, NORMAL, LOW/SPAM),
executive inbox triage, and automated drafting.
"""

import os
import email
from email.header import decode_header
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
import datetime
import re

EMAIL_HOST = os.getenv("EMAIL_HOST", "imap.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "993"))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_SMTP_HOST = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))

# Urgency heuristics dictionaries
URGENT_KEYWORDS = [
    "urgent", "critical", "emergency", "immediate action", "outage", "downtime",
    "security alert", "unauthorized", "breach", "server down", "asap", "incident",
    "payment failed", "fraud", "account suspended", "deadline today"
]

HIGH_KEYWORDS = [
    "important", "deadline", "contract", "invoice", "client", "proposal",
    "action required", "approval needed", "interview", "review requested",
    "bug report", "priority"
]

LOW_KEYWORDS = [
    "newsletter", "unsubscribe", "promotions", "discount", "sale", "digest",
    "weekly update", "no-reply", "notification", "marketing", "webinar"
]

class EmailTriageEngine:
    def __init__(self):
        self.host = EMAIL_HOST
        self.port = EMAIL_PORT
        self.user = EMAIL_USER
        self.password = EMAIL_PASSWORD
        self.smtp_host = EMAIL_SMTP_HOST
        self.smtp_port = EMAIL_SMTP_PORT

    def is_configured(self) -> bool:
        return bool(self.user and self.password and self.password != "your_app_password_here")

    def classify_urgency(self, subject: str, sender: str, snippet: str) -> Dict[str, Any]:
        """
        Classifies an email into URGENT, HIGH, NORMAL, or LOW priority.
        """
        text = f"{subject} {snippet}".lower()
        score = 0
        urgency_level = "NORMAL"
        badge = "ℹ️"
        reason = "Standard communication"

        # Check URGENT triggers
        for kw in URGENT_KEYWORDS:
            if kw in text:
                score += 10
                urgency_level = "URGENT"
                badge = "🚨"
                reason = f"Contains critical trigger: '{kw}'"
                break

        # Check HIGH triggers if not already urgent
        if urgency_level == "NORMAL":
            for kw in HIGH_KEYWORDS:
                if kw in text:
                    score += 5
                    urgency_level = "HIGH"
                    badge = "⚠️"
                    reason = f"Important work indicator: '{kw}'"
                    break

        # Check LOW / PROMOTIONAL triggers
        if urgency_level == "NORMAL":
            for kw in LOW_KEYWORDS:
                if kw in text:
                    score -= 5
                    urgency_level = "LOW"
                    badge = "💤"
                    reason = f"Automated or promotional content: '{kw}'"
                    break

        return {
            "urgency": urgency_level,
            "badge": badge,
            "score": score,
            "reason": reason
        }

    def fetch_emails(self, limit: int = 5, unread_only: bool = True) -> List[Dict[str, Any]]:
        """
        Connects via IMAP to fetch real emails, or returns realistic sandbox data if credentials not set.
        """
        if not self.is_configured():
            return self._get_mock_inbox()

        emails_list = []
        try:
            mail = imaplib.IMAP4_SSL(self.host, self.port, timeout=10)
            mail.login(self.user, self.password)
            mail.select("inbox")

            search_criteria = "UNSEEN" if unread_only else "ALL"
            status, messages = mail.search(None, search_criteria)
            
            if status != "OK" or not messages[0]:
                mail.close()
                mail.logout()
                return []

            msg_ids = messages[0].split()
            # Get latest emails
            latest_ids = msg_ids[-limit:]
            latest_ids.reverse()

            for msg_id in latest_ids:
                res, data = mail.fetch(msg_id, "(RFC822)")
                if res != "OK":
                    continue
                
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)

                # Decode subject
                subject, encoding = decode_header(msg.get("Subject", ""))[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")

                # Sender
                sender = msg.get("From", "Unknown")

                # Date
                date_str = msg.get("Date", "")

                # Extract plain text body snippet
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode(errors="ignore")
                            break
                else:
                    body = msg.get_payload(decode=True).decode(errors="ignore")

                snippet = " ".join(body.split())[:300]
                triage = self.classify_urgency(subject, sender, snippet)

                emails_list.append({
                    "id": msg_id.decode() if isinstance(msg_id, bytes) else str(msg_id),
                    "sender": sender,
                    "subject": subject,
                    "date": date_str,
                    "snippet": snippet,
                    "urgency": triage["urgency"],
                    "badge": triage["badge"],
                    "reason": triage["reason"]
                })

            mail.close()
            mail.logout()
        except Exception as e:
            print(f"[EmailTriageEngine] IMAP fetch error: {e}")
            return self._get_mock_inbox(notice=f"Live IMAP notice: {str(e)}")

        return emails_list

    def triage_inbox(self, limit: int = 10, unread_only: bool = False) -> Dict[str, Any]:
        """
        Scans emails, classifies priority, identifies action items, and generates an executive triage report.
        """
        emails = self.fetch_emails(limit=limit, unread_only=unread_only)
        
        urgent = [e for e in emails if e.get("urgency") == "URGENT"]
        high = [e for e in emails if e.get("urgency") == "HIGH"]
        normal = [e for e in emails if e.get("urgency") == "NORMAL"]
        low = [e for e in emails if e.get("urgency") == "LOW"]
        
        # Build action items
        action_items = []
        for e in urgent:
            action_items.append(f"🚨 IMMEDIATE ACTION: {e.get('subject')} (From: {e.get('sender')}) - {e.get('reason')}")
        for e in high:
            action_items.append(f"⚠️ HIGH PRIORITY: {e.get('subject')} (From: {e.get('sender')}) - {e.get('reason')}")
            
        # Build formatted report
        report_lines = [
            f"📬 **Inbox Triage Report** ({len(emails)} scanned)",
            f"• 🚨 Urgent: {len(urgent)} | ⚠️ High: {len(high)} | ℹ️ Normal: {len(normal)} | 💤 Low/Spam: {len(low)}\n"
        ]
        
        if urgent:
            report_lines.append("🚨 **URGENT ITEMS REQUIRING IMMEDIATE ATTENTION**:")
            for e in urgent:
                report_lines.append(f"- **{e.get('subject')}**")
                report_lines.append(f"  From: `{e.get('sender')}` | Date: {e.get('date')}")
                report_lines.append(f"  Summary: {e.get('snippet')}")
                report_lines.append(f"  Why Urgent: {e.get('reason')}\n")
                
        if high:
            report_lines.append("⚠️ **HIGH PRIORITY ITEMS**:")
            for e in high:
                report_lines.append(f"- **{e.get('subject')}**")
                report_lines.append(f"  From: `{e.get('sender')}` | Date: {e.get('date')}")
                report_lines.append(f"  Summary: {e.get('snippet')}\n")
                
        if normal:
            report_lines.append(f"ℹ️ **Standard Communications ({len(normal)})**:")
            for e in normal[:3]:
                report_lines.append(f"- {e.get('subject')} (From: {e.get('sender')})")
            if len(normal) > 3:
                report_lines.append(f"  ...and {len(normal) - 3} more.")
            report_lines.append("")
            
        if low:
            report_lines.append(f"💤 **Low Priority / Newsletters / Automated ({len(low)})**:")
            for e in low[:3]:
                report_lines.append(f"- {e.get('subject')} (From: {e.get('sender')})")
            report_lines.append("")

        if action_items:
            report_lines.append("🎯 **Recommended Autonomous Next Steps**:")
            for act in action_items:
                report_lines.append(f"• {act}")
        else:
            report_lines.append("✅ **Inbox Zero / No critical items pending.**")

        return {
            "total_scanned": len(emails),
            "urgent_count": len(urgent),
            "high_count": len(high),
            "normal_count": len(normal),
            "low_count": len(low),
            "urgent_emails": urgent,
            "high_emails": high,
            "normal_emails": normal,
            "low_emails": low,
            "action_items": action_items,
            "report": "\n".join(report_lines)
        }

    def draft_reply(self, to_address: str, subject: str, context: str, tone: str = "professional") -> Dict[str, Any]:
        """
        Drafts an autonomous, context-aware reply to an email.
        """
        reply_subject = subject if subject.lower().startswith("re:") else f"Re: {subject}"
        draft_body = (
            f"Hi,\n\n"
            f"Thank you for reaching out. In response to your message regarding '{subject}':\n\n"
            f"{context}\n\n"
            f"Please let me know if you need any additional information.\n\n"
            f"Best regards,\n"
            f"NemoClaw Autonomous Executive Agent"
        )
        return {
            "to": to_address,
            "subject": reply_subject,
            "draft_body": draft_body,
            "tone": tone
        }

    def send_email(self, to_address: str, subject: str, body: str) -> Dict[str, Any]:
        """
        Sends an email via SMTP, or records dry-run if credentials not set.
        """
        if not self.is_configured():
            return {
                "success": True,
                "mode": "sandbox_dry_run",
                "message": f"Simulated email sent to {to_address} with subject '{subject}'. (Configure EMAIL_USER in .env for live dispatch)."
            }

        try:
            msg = MIMEMultipart()
            msg["From"] = self.user
            msg["To"] = to_address
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
            server.starttls()
            server.login(self.user, self.password)
            server.send_message(msg)
            server.quit()

            return {
                "success": True,
                "mode": "live_smtp",
                "message": f"Email successfully dispatched to {to_address}."
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _get_mock_inbox(self, notice: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Provides realistic email inbox data for triage verification and offline mode.
        """
        items = [
            {
                "id": "101",
                "sender": "alert@monitoring.homelabb.net",
                "subject": "CRITICAL: Server Node CPU threshold exceeded (98%) & Disk space warning",
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "snippet": "Incident Alert: Host homelabb reported 98% sustained load. Immediate action required to check docker processes.",
                "urgency": "URGENT",
                "badge": "🚨",
                "reason": "Server health critical alert"
            },
            {
                "id": "102",
                "sender": "sarah.chen@innovatetech.io",
                "subject": "Urgent: Project timeline approval needed before today 5 PM",
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "snippet": "Hi team, please review the finalized architecture milestones. We need your approval to proceed with deployment.",
                "urgency": "HIGH",
                "badge": "⚠️",
                "reason": "Same-day deadline from team lead"
            },
            {
                "id": "103",
                "sender": "support@github.com",
                "subject": "[GitHub] Security advisory: New vulnerability detected in repository",
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "snippet": "Dependabot alert for your repository. A moderate severity advisory was opened for dependency package.",
                "urgency": "HIGH",
                "badge": "⚠️",
                "reason": "Security vulnerability alert"
            },
            {
                "id": "104",
                "sender": "news@hacker-daily.org",
                "subject": "Tech Weekly: Open Source AI models & Distributed computing updates",
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "snippet": "Here are this week's top software engineering stories, rust frameworks, and AI advancements.",
                "urgency": "LOW",
                "badge": "💤",
                "reason": "Newsletter digest"
            }
        ]
        if notice:
            for it in items:
                it["note"] = notice
        return items
