import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", 'ddrporders@gmail.com')
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", 'mrvy eaas crfx qbpi')

def send_order_confirmation_email(to_emails: List[str], order_id: str, product: str, quantity: int):
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        raise ValueError("SMTP_USERNAME and SMTP_PASSWORD must be set in environment variables.")

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .order-details {{ border: 1px solid #ddd; border-collapse: collapse; width: 100%; }}
            .order-details th, .order-details td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            .footer {{ background-color: #f8f9fa; padding: 10px; text-align: center; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Thank you for your order!</h2>
            <p>Order #{order_id} has been placed successfully.</p>
        </div>
        <div class="content">
            <h3>Order Details:</h3>
            <table class="order-details">
                <tr>
                    <th>Product</th>
                    <td>{product}</td>
                </tr>
                <tr>
                    <th>Quantity</th>
                    <td>{quantity}</td>
                </tr>
                <tr>
                    <th>Status</th>
                    <td>Pending</td>
                </tr>
            </table>
        </div>
        <div class="footer">
            <p>Made-to-Order Rubber Spares<br>
            We will keep you updated on your order status.</p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart('alternative')
    msg['From'] = SMTP_USERNAME
    msg['To'] = ', '.join(to_emails)
    msg['Subject'] = f"Order Confirmation - Order #{order_id}"

    # Attach both plain text and HTML versions
    plain_text = f"Thank you for your order! Order #{order_id} has been placed.\n\nProduct: {product}\nQuantity: {quantity}\nStatus: Pending"
    msg.attach(MIMEText(plain_text, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, to_emails, text)
        server.quit()
        print(f"Order confirmation email sent successfully to {to_emails}")
    except Exception as e:
        print(f"Failed to send order confirmation email: {e}")
        raise

def send_order_status_email(to_emails: List[str], order_id: str, status: str):
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        raise ValueError("SMTP_USERNAME and SMTP_PASSWORD must be set in environment variables.")

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .status-box {{ background-color: #e9ecef; border-left: 4px solid #007bff; padding: 15px; margin: 20px 0; }}
            .footer {{ background-color: #f8f9fa; padding: 10px; text-align: center; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Order Status Update</h2>
            <p>Order #{order_id} has been updated.</p>
        </div>
        <div class="content">
            <div class="status-box">
                <h3>New Status: {status}</h3>
                <p>Your order is now in the <strong>{status}</strong> stage.</p>
            </div>
            <p>We will continue to keep you updated on your order progress.</p>
        </div>
        <div class="footer">
            <p>Made-to-Order Rubber Spares<br>
            If you have any questions, please contact us.</p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart('alternative')
    msg['From'] = SMTP_USERNAME
    msg['To'] = ', '.join(to_emails)
    msg['Subject'] = f"Order #{order_id} Status Update"

    # Attach both plain text and HTML versions
    plain_text = f"Your order #{order_id} status has been updated to: {status}"
    msg.attach(MIMEText(plain_text, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, to_emails, text)
        server.quit()
        print(f"Status update email sent successfully to {to_emails}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise

def send_delay_notification_email(to_emails: List[str], order_id: str, expected_date, current_status: str):
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        raise ValueError("SMTP_USERNAME and SMTP_PASSWORD must be set in environment variables.")

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .delay-box {{ background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; margin: 20px 0; }}
            .footer {{ background-color: #f8f9fa; padding: 10px; text-align: center; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Order Delay Notification</h2>
            <p>Order #{order_id} is experiencing a delay.</p>
        </div>
        <div class="content">
            <div class="delay-box">
                <h3>Expected Delivery Date: {expected_date.strftime('%Y-%m-%d')}</h3>
                <p>Your order is currently <strong>{current_status}</strong> and has passed the expected delivery date.</p>
            </div>
            <p>We apologize for the inconvenience. We are working to resolve this as soon as possible. Please contact us for more details.</p>
        </div>
        <div class="footer">
            <p>Made-to-Order Rubber Spares<br>
            If you have any questions, please contact us.</p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart('alternative')
    msg['From'] = SMTP_USERNAME
    msg['To'] = ', '.join(to_emails)
    msg['Subject'] = f"Delay Notification - Order #{order_id}"

    # Attach both plain text and HTML versions
    plain_text = f"Your order #{order_id} is delayed. Expected delivery: {expected_date.strftime('%Y-%m-%d')}. Current status: {current_status}"
    msg.attach(MIMEText(plain_text, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, to_emails, text)
        server.quit()
        print(f"Delay notification email sent successfully to {to_emails}")
    except Exception as e:
        print(f"Failed to send delay notification email: {e}")
        raise

def send_raw_material_arrival_email(to_emails: List[str], order_id: str, bill_no: str, batch_no: str, quantity: float):
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        raise ValueError("SMTP_USERNAME and SMTP_PASSWORD must be set in environment variables.")

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .arrival-box {{ background-color: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0; }}
            .footer {{ background-color: #f8f9fa; padding: 10px; text-align: center; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Raw Material Arrival Notification</h2>
            <p>Raw materials have arrived for Order #{order_id}.</p>
        </div>
        <div class="content">
            <div class="arrival-box">
                <h3>Material Details:</h3>
                <p><strong>Bill No:</strong> {bill_no}</p>
                <p><strong>Batch No:</strong> {batch_no}</p>
                <p><strong>Quantity Received:</strong> {quantity} kg</p>
            </div>
            <p>The production process can now begin for this order.</p>
        </div>
        <div class="footer">
            <p>Made-to-Order Rubber Spares<br>
            Production team has been notified.</p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart('alternative')
    msg['From'] = SMTP_USERNAME
    msg['To'] = ', '.join(to_emails)
    msg['Subject'] = f"Raw Material Arrived - Order #{order_id}"

    plain_text = f"Raw materials arrived for order #{order_id}. Bill: {bill_no}, Batch: {batch_no}, Quantity: {quantity} kg"
    msg.attach(MIMEText(plain_text, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, to_emails, text)
        server.quit()
        print(f"Raw material arrival email sent successfully to {to_emails}")
    except Exception as e:
        print(f"Failed to send raw material arrival email: {e}")
        raise

def send_natural_rubber_alert_email(to_emails: List[str], order_id: str, deadline):
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        raise ValueError("SMTP_USERNAME and SMTP_PASSWORD must be set in environment variables.")

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .alert-box {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
            .footer {{ background-color: #f8f9fa; padding: 10px; text-align: center; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Natural Rubber Consumption Alert</h2>
            <p>Order #{order_id} requires immediate attention.</p>
        </div>
        <div class="content">
            <div class="alert-box">
                <h3>Urgent: Natural Rubber Not Consumed</h3>
                <p>The natural rubber for Order #{order_id} has not been consumed by the deadline: {deadline.strftime('%Y-%m-%d')}.</p>
                <p>Please process this material immediately to avoid degradation.</p>
            </div>
        </div>
        <div class="footer">
            <p>Made-to-Order Rubber Spares<br>
            Quality control alert.</p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart('alternative')
    msg['From'] = SMTP_USERNAME
    msg['To'] = ', '.join(to_emails)
    msg['Subject'] = f"Natural Rubber Alert - Order #{order_id}"

    plain_text = f"Natural rubber for order #{order_id} not consumed by deadline {deadline.strftime('%Y-%m-%d')}. Process immediately."
    msg.attach(MIMEText(plain_text, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, to_emails, text)
        server.quit()
        print(f"Natural rubber alert email sent successfully to {to_emails}")
    except Exception as e:
        print(f"Failed to send natural rubber alert email: {e}")
        raise
