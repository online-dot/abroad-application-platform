from flask_mail import Message
from flask import current_app
from app.extensions import mail

def send_email(subject, recipients, body, html=None):
    """
    Core email sending function
    """
    try:
        msg = Message(
    subject=subject,
    recipients=recipients,
    body=body,
    sender=("Work Abroad Team", "work abroad team ")
)

        if html:
            msg.html = html
        mail.send(msg)
        current_app.logger.info(f"✅ Email sent to {recipients}")
        return True, "Email sent successfully."
    except Exception as e:
        error_msg = f"❌ Failed to send email: {str(e)}"
        current_app.logger.error(error_msg, exc_info=True)
        return False, error_msg

def send_acceptance_email(to_email, user_name, registration_number, is_reminder=False):
    """
    Sends official acceptance letter with EXACT formatting from reference screenshot
    """
    # Subject line
    subject = "CVE NOTIFICATION DEPARTMENT - Acceptance Letter"
    if is_reminder:
        subject = subject.replace("Acceptance", "Reminder")

    # HTML version with pixel-perfect styling
    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: 'Times New Roman', Times, serif;
                line-height: 1.5;
                color: #000000;
                max-width: 650px;
                margin: 0 auto;
                padding: 15px;
                background-color: #ffffff;
            }}
            .header {{
                font-size: 18px;
                font-weight: bold;
                text-align: center;
                margin-bottom: 5px;
                text-transform: uppercase;
            }}
            .title {{
                font-size: 16px;
                font-weight: bold;
                text-align: center;
                margin: 10px 0;
            }}
            .notification {{
                font-size: 14px;
                text-align: center;
                margin-bottom: 20px;
                text-decoration: underline;
            }}
            .content {{
                font-size: 14px;
                margin: 25px 0;
                line-height: 1.6;
            }}
            .applicant-info {{
                margin: 20px 0;
            }}
            .action-button {{
                display: inline-block;
                margin: 15px 0;
                color: #0000EE;
                text-decoration: underline;
                font-weight: bold;
            }}
            .highlight {{
                font-weight: bold;
                margin: 20px 0;
            }}
            .urgent {{
                color: #FF0000;
                font-weight: bold;
            }}
            .footer {{
                margin-top: 30px;
                font-size: 14px;
                line-height: 1.5;
            }}
            .signature {{
                margin-top: 25px;
                line-height: 1.4;
            }}
            .unsubscribe {{
                margin-top: 30px;
                font-size: 12px;
                color: #666666;
            }}
        </style>
    </head>
    <body>
        <div class="header">CVE NOTIFICATION DEPARTMENT</div>
        <div class="title">Acceptance Letter</div>
        <div class="notification">NOTIFICATION</div>
        
        <div class="content">
            <div class="applicant-info">
                Applicant {user_name},<br>
                Registration # {registration_number}, has been approved for Permanent Residency evaluation to Canada.
            </div>
            
            <p>This enables an immigration review for Permanent Residency status in Canada. Complete the online application to check if you meet the criteria for Employment based Express Entry to Canada.</p>
            
            <p>
                Complete your electronic application here: 
                <a href="https://www.canadianvisaexpert.com/application" class="action-button">
                    Click Here>>
                </a>
            </p>
            
            <p class="highlight">➔ Your request for immigration services is confirmed</p>
            
            <p class="urgent">Late submissions will not be enrolled in 2025!</p>
            
            <p>{user_name.split()[0]} - continue to your online application here.</p>
        </div>
        
        <div class="footer">
            <p>CVE will process and relay your application to authorized Canadian immigration consultants who will provide an assessment to apply. Canada will welcome another 395,000 new immigrants in 2025, many through the Express Entry immigration program for working families. An eligibility review is the first step in the application process. CVE provides services in multiple languages.</p>
            
            <div class="signature">
                <p>Secretary of Registry</p>
                <p>Canadian Visa Expert</p>
                <p><a href="https://www.canadianvisaexpert.com/">https://www.canadianvisaexpert.com/</a></p>
            </div>
            
            <div class="unsubscribe">
                <a href="https://www.canadianvisaexpert.com/unsubscribe">Click here to unsubscribe.</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version (fallback)
    body = f"""
CVE NOTIFICATION DEPARTMENT
Acceptance Letter
NOTIFICATION

Applicant {user_name},
Registration # {registration_number}, has been approved for Permanent Residency evaluation to Canada.

This enables an immigration review for Permanent Residency status in Canada. Complete the online application to check if you meet the criteria for Employment based Express Entry to Canada.

Complete your electronic application here: Click Here>> (https://www.canadianvisaexpert.com/application)

➔ Your request for immigration services is confirmed

Late submissions will not be enrolled in 2025!

{user_name.split()[0]} - continue to your online application here.

CVE will process and relay your application to authorized Canadian immigration consultants who will provide an assessment to apply. Canada will welcome another 395,000 new immigrants in 2025, many through the Express Entry immigration program for working families. An eligibility review is the first step in the application process. CVE provides services in multiple languages.

Secretary of Registry
Canadian Visa Expert
https://www.canadianvisaexpert.com/

Click here to unsubscribe: https://www.canadianvisaexpert.com/unsubscribe
"""
    
    return send_email(subject, [to_email], body, html)