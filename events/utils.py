import io
import qrcode
from qrcode.image.pure import PyPNGImage
from django.core.files import File
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.conf import settings
import os
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

def generate_ticket_qr(ticket):
    """
    Generates a QR code containing ticket details and saves it to the Ticket model.
    """
    # Define text to embed in the QR code
    qr_data = f"EVENTRIX VERIFIED TICKET\nTicket Ref: {ticket.ticket_code}\nEvent: {ticket.booking.event.title}\nUser: {ticket.booking.user.username}\nSeats: {', '.join(s.row_label + str(s.seat_number) for s in ticket.booking.seats.all())}"
    
    # Generate QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save image to a BytesIO buffer
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    filename = f"qr_{ticket.ticket_code}.png"
    
    # Save the file to Django ImageField
    ticket.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
    buffer.close()


def generate_ticket_pdf(ticket):
    """
    Generates a premium-design printable PDF ticket and saves it to the Ticket model.
    """
    booking = ticket.booking
    event = booking.event
    user = booking.user
    
    buffer = io.BytesIO()
    
    # Page setup
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TicketTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor('#6c5ce7'),
        spaceAfter=15
    )
    
    label_style = ParagraphStyle(
        'TicketLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#a4b0be')
    )
    
    value_style = ParagraphStyle(
        'TicketValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        textColor=colors.HexColor('#2f3542'),
        spaceAfter=8
    )
    
    story = []
    
    # Eventrix Branding Header
    story.append(Paragraph("<b>EVENTRIX OFFICIAL ENTRY TICKET</b>", title_style))
    story.append(Spacer(1, 0.1 * inch))
    
    # Grid details
    seat_labels = ", ".join(f"{s.row_label}{s.seat_number}" for s in booking.seats.all())
    
    # Load QR code image file path
    qr_image_path = ticket.qr_code.path
    
    # Construct a clean 2-column layout (Left: Details, Right: QR Code)
    details_data = [
        [Paragraph("EVENT", label_style), ""],
        [Paragraph(f"<b>{event.title}</b>", value_style), ""],
        [Paragraph("DATE & TIME", label_style), Paragraph("VENUE", label_style)],
        [Paragraph(event.date_time.strftime('%d %B %Y, %I:%M %p'), value_style), Paragraph(f"{event.venue}, {event.city}", value_style)],
        [Paragraph("BOOKED BY", label_style), Paragraph("SEAT NUMBERS", label_style)],
        [Paragraph(f"{user.first_name} {user.last_name} (@{user.username})", value_style), Paragraph(seat_labels, value_style)],
        [Paragraph("BOOKING REFERENCE", label_style), Paragraph("AMOUNT PAID", label_style)],
        [Paragraph(f"#{booking.id}", value_style), Paragraph(f"INR {booking.total_amount}", value_style)],
        [Paragraph("TICKET VERIFICATION ID", label_style), ""],
        [Paragraph(str(ticket.ticket_code), value_style), ""]
    ]
    
    details_table = Table(details_data, colWidths=[2.5 * inch, 2.5 * inch])
    details_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (0, 1), (1, 1)),
        ('SPAN', (0, 8), (1, 8)),
        ('SPAN', (0, 9), (1, 9)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    # QR Image element
    qr_img_el = Image(qr_image_path, width=2.0 * inch, height=2.0 * inch)
    
    # Outer layout table (Left: Details Table, Right: QR Image)
    main_layout_data = [
        [details_table, qr_img_el]
    ]
    
    main_layout_table = Table(main_layout_data, colWidths=[5.0 * inch, 2.2 * inch])
    main_layout_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1.5, colors.HexColor('#6c5ce7')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
    ]))
    
    story.append(main_layout_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # Important Information
    info_title_style = ParagraphStyle(
        'InfoTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#2f3542'),
        spaceAfter=5
    )
    info_text_style = ParagraphStyle(
        'InfoText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor('#747d8c'),
        spaceAfter=3
    )
    
    story.append(Paragraph("<b>IMPORTANT INSTRUCTIONS</b>", info_title_style))
    story.append(Paragraph("1. Please arrive at the venue at least 30 minutes before the event scheduled time.", info_text_style))
    story.append(Paragraph("2. Carry this printable ticket or show the digital QR code at the entrance for verification.", info_text_style))
    story.append(Paragraph("3. Food and beverages from outside may not be permitted inside the event arena.", info_text_style))
    story.append(Paragraph("4. Tickets are non-refundable and non-transferable under standard booking guidelines.", info_text_style))
    
    # Build document
    doc.build(story)
    
    # Save the file to Django FileField
    filename = f"ticket_{ticket.ticket_code}.pdf"
    ticket.pdf_file.save(filename, ContentFile(buffer.getvalue()), save=False)
    buffer.close()


def send_ticket_email(ticket):
    """
    Sends a confirmation email to the customer with ticket details and PDF attached.
    """
    booking = ticket.booking
    user = booking.user
    event = booking.event
    
    subject = f"Your Ticket Confirmation: {event.title}"
    
    context = {
        'ticket': ticket,
        'booking': booking,
        'user': user,
        'event': event,
        'seat_labels': ", ".join(f"{s.row_label}{s.seat_number}" for s in booking.seats.all()),
    }
    
    try:
        html_message = render_to_string('emails/ticket_confirmation.html', context)
        plain_message = strip_tags(html_message)
    except Exception as e:
        logger.error(f"Failed to render HTML email template: {e}")
        plain_message = f"Dear {user.first_name or user.username},\n\nYour booking for {event.title} has been confirmed. Seat numbers: {context['seat_labels']}. Ticket Code: {ticket.ticket_code}."
        html_message = None

    email = EmailMessage(
        subject=subject,
        body=html_message or plain_message,
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email],
    )
    if html_message:
        email.content_subtype = "html"
        
    if ticket.pdf_file:
        try:
            ticket.pdf_file.open('rb')
            email.attach(
                filename=f"ticket_{ticket.ticket_code}.pdf",
                content=ticket.pdf_file.read(),
                mimetype='application/pdf'
            )
            ticket.pdf_file.close()
        except Exception as e:
            logger.error(f"Failed to attach ticket PDF to email: {e}")
            
    try:
        email.send(fail_silently=False)
        logger.info(f"Ticket email sent successfully to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send ticket email to {user.email}: {e}")


def send_reminder_email(booking, days_left):
    """
    Sends a reminder email to the customer about their upcoming event.
    """
    user = booking.user
    event = booking.event
    
    if days_left == 0:
        subject = f"[Reminder] Your event '{event.title}' is TODAY!"
        template_name = 'emails/event_reminder_today.html'
    else:
        subject = f"[Reminder] Upcoming event: '{event.title}' in 3 days!"
        template_name = 'emails/event_reminder_3days.html'
        
    context = {
        'booking': booking,
        'user': user,
        'event': event,
        'seat_labels': ", ".join(f"{s.row_label}{s.seat_number}" for s in booking.seats.all()),
    }
    
    try:
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
    except Exception as e:
        logger.error(f"Failed to render HTML reminder email template: {e}")
        if days_left == 0:
            plain_message = f"Dear {user.first_name or user.username},\n\nThis is a friendly reminder that you have an event today: {event.title} at {event.venue}, {event.city}.\nDate & Time: {event.date_time.strftime('%Y-%m-%d %I:%M %p')}\nSeats: {context['seat_labels']}."
        else:
            plain_message = f"Dear {user.first_name or user.username},\n\nThis is a friendly reminder that you have an upcoming event in 3 days: {event.title} at {event.venue}, {event.city}.\nDate & Time: {event.date_time.strftime('%Y-%m-%d %I:%M %p')}\nSeats: {context['seat_labels']}."
        html_message = None

    email = EmailMessage(
        subject=subject,
        body=html_message or plain_message,
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email],
    )
    if html_message:
        email.content_subtype = "html"
        
    try:
        email.send(fail_silently=False)
        logger.info(f"Reminder email sent successfully to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send reminder email to {user.email}: {e}")
        return False
