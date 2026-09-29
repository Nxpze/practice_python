import os
import sys

# 1. ตรวจสอบและป้องกันกรณีลืมติดตั้งไลบรารี pypdf
try:
    from pypdf import PdfReader, PdfWriter
    from pypdf.errors import PdfReadError
except ImportError:
    print("❌ ไม่พบไลบรารี 'pypdf'")
    print("💡 กรุณาติดตั้งก่อนใช้งานด้วยคำสั่ง: pip install pypdf")
    sys.exit(1)


def lock_pdf(input_pdf_path, output_pdf_path, password):
    # ตัดเครื่องหมายคำพูดและช่องว่างส่วนเกินออกจาก path (กรณีลากไฟล์มาวางใน Terminal)
    input_pdf_path = str(input_pdf_path).strip().strip("'\"")
    output_pdf_path = str(output_pdf_path).strip().strip("'\"")

    # ตรวจสอบความถูกต้องของ path ไฟล์ต้นทาง
    if not input_pdf_path:
        print("❌ กรุณาระบุชื่อหรือพาธของไฟล์ PDF ที่ต้องการล็อค")
        return False

    if not os.path.exists(input_pdf_path):
        print(f"❌ ไม่พบไฟล์ต้นฉบับ: '{input_pdf_path}'")
        return False

    if not os.path.isfile(input_pdf_path):
        print(f"❌ พาธที่ระบุไม่ใช่ไฟล์: '{input_pdf_path}'")
        return False

    # ตรวจสอบความถูกต้องของ path ไฟล์ปลายทาง
    if not output_pdf_path:
        print("❌ กรุณาระบุชื่อหรือพาธของไฟล์ PDF ใหม่ที่ต้องการบันทึก")
        return False

    # ป้องกันการบันทึกทับไฟล์เดิมโดยตรงขณะอ่าน ซึ่งอาจทำให้ไฟล์เสียหาย
    if os.path.abspath(input_pdf_path) == os.path.abspath(output_pdf_path):
        print("❌ ไฟล์ต้นฉบับและไฟล์ใหม่ต้องไม่เป็นไฟล์เดียวกัน เพื่อป้องกันไฟล์เสียหาย")
        return False

    # สร้างโฟลเดอร์ปลายทางให้อัตโนมัติหากยังไม่มี
    output_dir = os.path.dirname(output_pdf_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    try:
        # 1. อ่านไฟล์ PDF ต้นฉบับ
        reader = PdfReader(input_pdf_path)

        # ตรวจสอบว่าไฟล์เดิมถูกเข้ารหัสรหัสผ่านไว้แล้วหรือไม่
        if reader.is_encrypted:
            print("⚠️ แจ้งเตือน: ไฟล์ PDF นี้มีการตั้งรหัสผ่านไว้อยู่แล้ว")

        writer = PdfWriter()

        # 2. คัดลอกหน้าทั้งหมดจากไฟล์เดิมไปยังไฟล์ใหม่
        writer.append_pages_from_reader(reader)

        # 3. ใส่รหัสผ่านเพื่อเข้ารหัสไฟล์ (Lock)
        writer.encrypt(password)

        # 4. บันทึกไฟล์ PDF ที่ล็อคแล้วออกไป
        with open(output_pdf_path, "wb") as out_file:
            writer.write(out_file)

        print(f"ล็อคไฟล์ PDF เรียบร้อยแล้ว! ไฟล์ใหม่อยู่ที่: {output_pdf_path} ด้วยรหัสผ่าน: {password}")
        return True

    except PdfReadError as e:
        print(f"❌ ไม่สามารถอ่านไฟล์ PDF ได้ (ไฟล์อาจเสียหายหรือไม่ใช่ไฟล์ PDF ที่ถูกต้อง): {e}")
        return False
    except PermissionError:
        print("❌ ไม่มีสิทธิ์ในการอ่านหรือเขียนไฟล์ (Permission Denied) กรุณาตรวจสอบสิทธิ์การเข้าถึง")
        return False
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}")
        return False


# --- ตัวอย่างการใช้งาน ---
if __name__ == "__main__":
    try:
        old_file = input("ป้อนชื่อไฟล์ PDF ที่ต้องการล็อค: ")       # ชื่อไฟล์ PDF ที่ต้องการล็อค
        new_file = input("ป้อนชื่อไฟล์ PDF ใหม่ที่ต้องการ: ") # ชื่อไฟล์ใหม่ที่จะได้หลังล็อค
        pass_word = input("ป้อนรหัสผ่านสำหรับไฟล์ PDF: ")      # รหัสผ่านที่ต้องการตั้ง

        lock_pdf(old_file, new_file, pass_word)
    except KeyboardInterrupt:
        print("\n\nยกเลิกการทำงานเรียบร้อยแล้ว")
    except EOFError:
        print("\n\nสิ้นสุดการทำงาน")
