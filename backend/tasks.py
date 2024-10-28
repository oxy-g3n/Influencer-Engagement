from celery_config import app
from send_email import send_email
from utils import get_db_connection
import json


@app.task
def check_pending_reqs():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query for influencers with open requests
    cursor.execute("""
        SELECT 
            Users.mail,
            Users.full_name,
            '[' || GROUP_CONCAT(
                '{"campaign_id":' || Ad_Requests.campaign_id || 
                ',"requirements":"' || COALESCE(REPLACE(Ad_Requests.requirements, '"', '\"'), '') || 
                '","payout":' || COALESCE(Ad_Requests.payout, 0) || '}'
            ) || ']' as requests_data,
            COUNT(*) as request_count
        FROM Ad_Requests
        JOIN Users ON Ad_Requests.influencer_id = Users.user_id
        WHERE Ad_Requests.status = 'open'
        GROUP BY Users.mail, Users.full_name;
    """)
    influencer_pendings = cursor.fetchall()

    # Query for sponsors with modified or influencer generated requests
    cursor.execute("""
        SELECT 
            Users.mail,
            Users.full_name,
            '[' || GROUP_CONCAT(
                '{"campaign_id":' || Ad_Requests.campaign_id || 
                ',"requirements":"' || COALESCE(REPLACE(Ad_Requests.requirements, '"', '\"'), '') || 
                '","payout":' || COALESCE(Ad_Requests.payout, 0) || 
                ',"new_payout":' || COALESCE(Ad_Requests.new_payout, 0) || 
                ',"status":"' || Ad_Requests.status || '"}'
            ) || ']' as requests_data,
            COUNT(*) as request_count
        FROM Ad_Requests
        JOIN Users ON Ad_Requests.sponsor_id = Users.user_id
        WHERE Ad_Requests.status IN ('modified', 'influencer_generated')
        GROUP BY Users.mail, Users.full_name;
    """)
    sponsor_pendings = cursor.fetchall()

    conn.close()

    # Process influencer emails
    for email, full_name, requests_data, request_count in influencer_pendings:
        try:
            # Print debug information
            print(f"Debug - Influencer data: {requests_data}")

            if not requests_data:
                continue

            requests = json.loads(requests_data)

            requests_table = """
                <tr style="background-color: #f2f2f2;">
                    <th style="padding: 12px; border: 1px solid #ddd;">Campaign ID</th>
                    <th style="padding: 12px; border: 1px solid #ddd;">Requirements</th>
                    <th style="padding: 12px; border: 1px solid #ddd;">Payout</th>
                </tr>
            """

            for req in requests:
                requests_table += f"""
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd;">{req['campaign_id']}</td>
                        <td style="padding: 12px; border: 1px solid #ddd;">{req['requirements']}</td>
                        <td style="padding: 12px; border: 1px solid #ddd;">${req['payout']}</td>
                    </tr>
                """

            html_content = f"""
            <html>
            <body style="text-align: center; font-family: Arial, sans-serif;">
                <h2>🔔 New Campaign Requests Available</h2>
                <p>Dear {full_name},</p>
                <p>You have {request_count} new campaign request{'s' if request_count > 1 else ''} waiting for your review:</p>
                <table style="border-collapse: collapse; width: 80%; margin: 20px auto; text-align: left;">
                    {requests_table}
                </table>
                <p>Please review these requests and respond at your earliest convenience.</p>
                <a href="http://localhost:8080/" style="display: inline-block; padding: 10px 20px; background-color: #007BFF; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0;">Login to Review Requests</a>
                <p>Best regards,<br>Your Campaign Management Team</p>
            </body>
            </html>
            """

            subject = f"You have {request_count} new campaign request{'s' if request_count > 1 else ''}"
            send_email(email, subject, html_content)

        except Exception as e:
            print(f"Error processing influencer {email}: {str(e)}")
            print(f"Requests data: {requests_data}")
            continue

    # Process sponsor emails
    for email, full_name, requests_data, request_count in sponsor_pendings:
        try:
            # Print debug information
            print(f"Debug - Sponsor data: {requests_data}")

            if not requests_data:
                continue

            requests = json.loads(requests_data)

            requests_table = """
                <tr style="background-color: #f2f2f2;">
                    <th style="padding: 12px; border: 1px solid #ddd;">Campaign ID</th>
                    <th style="padding: 12px; border: 1px solid #ddd;">Requirements</th>
                    <th style="padding: 12px; border: 1px solid #ddd;">Payout</th>
                    <th style="padding: 12px; border: 1px solid #ddd;">New Payout</th>
                    <th style="padding: 12px; border: 1px solid #ddd;">Status</th>
                </tr>
            """

            for req in requests:
                new_payout_cell = f"${req['new_payout']}" if req['status'] == 'modified' else "-"
                requests_table += f"""
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd;">{req['campaign_id']}</td>
                        <td style="padding: 12px; border: 1px solid #ddd;">{req['requirements']}</td>
                        <td style="padding: 12px; border: 1px solid #ddd;">${req['payout']}</td>
                        <td style="padding: 12px; border: 1px solid #ddd;">{new_payout_cell}</td>
                        <td style="padding: 12px; border: 1px solid #ddd;">{req['status']}</td>
                    </tr>
                """

            html_content = f"""
            <html>
            <body style="text-align: center; font-family: Arial, sans-serif;">
                <h2>🔔 Campaign Requests Requiring Attention</h2>
                <p>Dear {full_name},</p>
                <p>You have {request_count} campaign request{'s' if request_count > 1 else ''} that require{'s' if request_count == 1 else ''} your attention:</p>
                <table style="border-collapse: collapse; width: 80%; margin: 20px auto; text-align: left;">
                    {requests_table}
                </table>
                <p>Please review these requests and take appropriate action.</p>
                <a href="http://localhost:8080/" style="display: inline-block; padding: 10px 20px; background-color: #007BFF; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0;">Login to Review Requests</a>
                <p>Best regards,<br>Your Campaign Management Team</p>
            </body>
            </html>
            """

            subject = f"You have {request_count} campaign request{'s' if request_count > 1 else ''} requiring attention"
            send_email(email, subject, html_content)

        except Exception as e:
            print(f"Error processing sponsor {email}: {str(e)}")
            print(f"Requests data: {requests_data}")
            continue

    print(
        f"Sent email notifications to {len(influencer_pendings)} influencers and {len(sponsor_pendings)} sponsors about their pending requests.")