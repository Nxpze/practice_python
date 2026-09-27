from pypdf import PdfReader, PdfWriter

def lock_pdf(input_pdf_path, output_pdf_path, password):
    # 1. อ่านไฟล์ PDF ต้นฉบับ
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # 2. คัดลอกหน้าทั้งหมดจากไฟล์เดิมไปยังไฟล์ใหม่
    writer.append_pages_from_reader(reader)

    # 3. ใส่รหัสผ่านเพื่อเข้ารหัสไฟล์ (Lock)
    writer.encrypt(password)

    # 4. บันทึกไฟล์ PDF ที่ล็อคแล้วออกไป
    with open(output_pdf_path, "wb") as out_file:
        writer.write(out_file)
        
    print(f"ล็อคไฟล์ PDF เรียบร้อยแล้ว! ไฟล์ใหม่อยู่ที่: {output_pdf_path} ด้วยรหัสผ่าน: {password}")

# --- ตัวอย่างการใช้งาน ---
old_file = input("ป้อนชื่อไฟล์ PDF ที่ต้องการล็อค: ")       # ชื่อไฟล์ PDF ที่ต้องการล็อค
new_file = input("ป้อนชื่อไฟล์ PDF ใหม่ที่ต้องการ: ") # ชื่อไฟล์ใหม่ที่จะได้หลังล็อค
pass_word = input("ป้อนรหัสผ่านสำหรับไฟล์ PDF: ")      # รหัสผ่านที่ต้องการตั้ง

lock_pdf(old_file, new_file, pass_word)
