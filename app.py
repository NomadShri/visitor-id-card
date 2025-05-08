import os
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import barcode
from barcode.writer import ImageWriter

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/generate', methods=['POST'])
def generate():
    name = request.form['name']
    mobile = request.form['mobile']
    aadhar = request.form['aadhar']
    meeting_with = request.form['meeting_with']
    work = request.form['work']
    photo_data = request.form.get('photo_data')
    photo_file = request.files.get('photo')

    # Prepare base card
    card = Image.new('RGB', (800, 500), 'white')
    draw = ImageDraw.Draw(card)

    # Load fonts
    title_font = ImageFont.truetype("Roboto-Regular", 28)
    text_font = ImageFont.truetype("Roboto-Regular", 22)

    # Load logo
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(base_dir, 'static', 'logo.png')
    logo = Image.open(logo_path).resize((100, 100))
    card.paste(logo, (20, 20))

    # Draw company name (centered)
    company_name = "Maharaja Ganga Singh University, Bikaner"
    bbox = draw.textbbox((0, 0), company_name, font=title_font)
    text_width = bbox[2] - bbox[0]
    draw.text(((800 - text_width) / 2, 40), company_name, font=title_font, fill='red')

    # Handle visitor photo (top-right, below title)
    if photo_data and photo_data.strip() != "":
        header, encoded = photo_data.split(",", 1)
        image_data = base64.b64decode(encoded)
        visitor_photo = Image.open(io.BytesIO(image_data))
    elif photo_file and photo_file.filename != "":
        visitor_photo = Image.open(photo_file.stream)
    else:
        return "Error: No photo provided!"

    visitor_photo = visitor_photo.convert("RGB")
    visitor_photo = visitor_photo.resize((120, 120))
    card.paste(visitor_photo, (650, 120))  # moved down

    # Draw visitor info (start below logo)
    y_start = 150
    line_height = 35
    draw.text((20, y_start + 100), f"Name: {name}", font=text_font, fill='black')
    draw.text((20, y_start + 100 + line_height), f"Mobile: {mobile}", font=text_font, fill='black')
    draw.text((20, y_start + 100 + line_height * 2), f"Aadhar: {aadhar}", font=text_font, fill='black')
    draw.text((20, y_start + 100 + line_height * 3), f"Meeting With: {meeting_with}", font=text_font, fill='black')
    draw.text((20, y_start + 100 + line_height * 4), f"Work: {work}", font=text_font, fill='black')

    # Generate barcode
    CODE128 = barcode.get_barcode_class('code128')
    aadhar_barcode = CODE128(aadhar, writer=ImageWriter())
    barcode_buffer = io.BytesIO()
    aadhar_barcode.write(barcode_buffer)
    barcode_img = Image.open(barcode_buffer)
    barcode_img = barcode_img.resize((400, 80))
    card.paste(barcode_img, (200, 400))

    # Save and send
    output = io.BytesIO()
    card.save(output, format='PNG')
    output.seek(0)

    return send_file(output, mimetype='image/png', as_attachment=True, download_name='visitor_id.png')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
