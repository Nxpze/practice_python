import os
import shutil
import subprocess
import tempfile
import pyzipper


def is_zip_file(file_path: str) -> bool:
    """ตรวจสอบว่าเป็นไฟล์ ZIP ที่ถูกต้องหรือไม่"""
    if not os.path.isfile(file_path):
        return False
    return pyzipper.is_zipfile(file_path)


def encrypt_zip(input_path: str, output_zip_path: str, password: str, encryption_mode: str = "standard"):
    """
    เข้ารหัส / ล็อกไฟล์ ZIP, ไฟล์เดี่ยว หรือโฟลเดอร์ ด้วยรหัสผ่าน
    
    Parameters:
    - input_path: เส้นทางไฟล์ ZIP เดิม, ไฟล์ หรือโฟลเดอร์ที่ต้องการล็อก
    - output_zip_path: เส้นทางไฟล์ ZIP ใหม่ที่ต้องการบันทึก
    - password: รหัสผ่านสำหรับล็อกไฟล์
    - encryption_mode: 
        * 'standard' (ค่าเริ่มต้น): เข้ารหัสแบบ ZipCrypto มาตรฐาน ดับเบิลคลิกแตกไฟล์บน Mac (Finder/Archive Utility) และ Windows Explorer ได้ทันที
        * 'aes': เข้ารหัสแบบ AES-256 (ความปลอดภัยสูง) แตกไฟล์ผ่าน 7-Zip, Keka, The Unarchiver หรือฟังก์ชันแตกไฟล์ในโปรแกรมนี้
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"ไม่พบไฟล์หรือโฟลเดอร์ต้นทาง: {input_path}")

    abs_output = os.path.abspath(output_zip_path)
    password_bytes = password.encode("utf-8")

    # -------------------------------------------------------------
    # โหมด 1: Standard (ZipCrypto) - รองรับ macOS Archive Utility & Windows Explorer
    # -------------------------------------------------------------
    if encryption_mode.lower() == "standard" and shutil.which("zip"):
        temp_dir = tempfile.mkdtemp()
        try:
            if is_zip_file(input_path):
                # แตกไฟล์ ZIP เดิมลงโฟลเดอร์ชั่วคราว (กรองไฟล์ขยะระบบ Mac ออก เพื่อป้องกัน Finder ค้าง/วนลูปถามรหัส)
                with pyzipper.AESZipFile(input_path, "r") as zf:
                    for item in zf.infolist():
                        base = os.path.basename(item.filename)
                        if "__MACOSX" in item.filename or base.startswith("._") or base == ".DS_Store":
                            continue
                        zf.extract(item, temp_dir)
            elif os.path.isdir(input_path):
                for item in os.listdir(input_path):
                    if item.startswith("._") or item in [".DS_Store", "__MACOSX"]:
                        continue
                    s = os.path.join(input_path, item)
                    d = os.path.join(temp_dir, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, ignore=shutil.ignore_patterns(".*", "__MACOSX*"))
                    else:
                        shutil.copy2(s, d)
            elif os.path.isfile(input_path):
                shutil.copy2(input_path, temp_dir)

            if os.path.exists(abs_output):
                os.remove(abs_output)

            items = [item for item in os.listdir(temp_dir) if not item.startswith(".")]
            if not items:
                raise ValueError("ไม่พบไฟล์ที่ต้องการบีบอัด")

            # ใช้ zip พร้อม flag -X (ตัด Extended Attributes ออก) เพื่อป้องกัน Mac Archive Utility วนลูปถามรหัส
            cmd = ["zip", "-q", "-r", "-X", "-P", password, abs_output] + items
            cmd += ["-x", ".*", "-x", "__MACOSX*", "-x", "*/.*", "-x", "*__MACOSX*"]
            
            res = subprocess.run(cmd, cwd=temp_dir, capture_output=True, text=True)
            if res.returncode != 0:
                raise RuntimeError(f"เกิดข้อผิดพลาดในการสร้างไฟล์ ZIP: {res.stderr}")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    # -------------------------------------------------------------
    # โหมด 2: AES-256 (ความปลอดภัยระดับสูง)
    # -------------------------------------------------------------
    else:
        if os.path.exists(abs_output):
            os.remove(abs_output)

        with pyzipper.AESZipFile(
            output_zip_path,
            "w",
            compression=pyzipper.ZIP_DEFLATED,
            encryption=pyzipper.WZ_AES
        ) as secured_zip:
            secured_zip.setpassword(password_bytes)

            if is_zip_file(input_path):
                with pyzipper.AESZipFile(input_path, "r") as current_zip:
                    for item in current_zip.infolist():
                        base = os.path.basename(item.filename)
                        if "__MACOSX" in item.filename or base.startswith("._") or base == ".DS_Store":
                            continue
                        if item.is_dir():
                            secured_zip.writestr(item.filename, b"")
                        else:
                            file_data = current_zip.read(item.filename)
                            secured_zip.writestr(item.filename, file_data)
                        print(f"กำลังเข้ารหัสไฟล์: {item.filename}")
            elif os.path.isdir(input_path):
                for root, _, files in os.walk(input_path):
                    for file in files:
                        if file.startswith("._") or file == ".DS_Store":
                            continue
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, start=input_path)
                        with open(full_path, "rb") as f:
                            secured_zip.writestr(rel_path, f.read())
                        print(f"กำลังเข้ารหัสไฟล์: {rel_path}")
            elif os.path.isfile(input_path):
                file_name = os.path.basename(input_path)
                with open(input_path, "rb") as f:
                    secured_zip.writestr(file_name, f.read())
                print(f"กำลังเข้ารหัสไฟล์: {file_name}")

    print(f"\n🔒 ล็อกไฟล์ ZIP สำเร็จแล้ว! ไฟล์ใหม่อยู่ที่: {output_zip_path}")


# Alias สำหรับรองรับโค้ดเดิม
encrypt_existing_zip = encrypt_zip


def extract_zip(zip_path: str, output_dir: str, password: str = ""):
    """
    ปลดล็อก / แตกไฟล์ ZIP ที่ติดรหัสผ่าน (รองรับทั้ง AES-256 และ Standard ZipCrypto)
    """
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"ไม่พบไฟล์ ZIP: {zip_path}")

    os.makedirs(output_dir, exist_ok=True)
    pwd_bytes = password.encode("utf-8") if password else None

    try:
        with pyzipper.AESZipFile(zip_path, "r") as zf:
            if pwd_bytes:
                zf.setpassword(pwd_bytes)

            # ตรวจสอบความถูกต้องของรหัสผ่าน
            zf.testzip()
            zf.extractall(output_dir)
            print(f"\n🔓 ปลดล็อกและแตกไฟล์ ZIP สำเร็จแล้ว! ไฟล์ถูกบันทึกไว้ที่: {output_dir}")
    except (RuntimeError, pyzipper.BadZipfile, pyzipper.BadZipFile) as e:
        error_str = str(e).lower()
        if "bad password" in error_str or "password" in error_str:
            raise RuntimeError("❌ รหัสผ่านไม่ถูกต้อง กรุณาตรวจสอบรหัสผ่านอีกครั้ง")
        else:
            raise RuntimeError(f"❌ ไม่สามารถแตกไฟล์ ZIP ได้: {e}")


# --- เมนูการใช้งาน ---
if __name__ == "__main__":
    print("=" * 55)
    print("🔐 โปรแกรมล็อกและปลดล็อกไฟล์ ZIP (ZIP Locker)")
    print("=" * 55)
    print("[1] ล็อกไฟล์ ZIP (Lock / เข้ารหัสด้วยรหัสผ่าน)")
    print("[2] ปลดล็อก / แตกไฟล์ ZIP (Unlock / ถอดรหัสผ่าน)")
    print("-" * 55)

    choice = input("เลือกเมนู (1 หรือ 2) [ค่าเริ่มต้น 1]: ").strip() or "1"

    if choice == "1":
        input_file = input("ป้อนชื่อไฟล์/โฟลเดอร์/ZIP ที่ต้องการล็อก: ").strip()
        output_file = input("ป้อนชื่อไฟล์ ZIP ใหม่ที่ต้องการ (เช่น locked.zip): ").strip()
        pwd = input("ป้อนรหัสผ่านสำหรับไฟล์ ZIP: ").strip()

        print("\nรูปแบบการเข้ารหัส:")
        print(" [1] มาตรฐาน (Standard) - แนะนำ! ดับเบิลคลิกแตกไฟล์บน Mac/Windows ได้ทันที")
        print(" [2] AES-256 (ความปลอดภัยสูง) - แตกไฟล์ผ่าน 7-Zip, Keka, WinRAR หรือโปรแกรมนี้")
        mode_choice = input("เลือกโหมด (1 หรือ 2) [ค่าเริ่มต้น 1]: ").strip() or "1"
        mode = "standard" if mode_choice == "1" else "aes"

        try:
            encrypt_zip(input_file, output_file, pwd, encryption_mode=mode)
            if mode == "standard":
                print("\n💡 คำแนะนำ: ไฟล์นี้เข้ารหัสแบบมาตรฐาน สามารถดับเบิลคลิกเปิดใน Mac Finder / Windows ได้ทันที")
            else:
                print("\n💡 คำแนะนำ: ไฟล์นี้เข้ารหัสแบบ AES-256 (Archive Utility ของ Mac ไม่รองรับการดับเบิลคลิก)")
                print("   สามารถแตกไฟล์ได้โดยเลือกเมนูข้อ [2] ในโปรแกรมนี้ หรือใช้แอป The Unarchiver / Keka")
        except Exception as err:
            print(f"\nเกิดข้อผิดพลาด: {err}")

    elif choice == "2":
        zip_file = input("ป้อนชื่อไฟล์ ZIP ที่ต้องการปลดล็อก: ").strip()
        dest_dir = input("ป้อนโฟลเดอร์ปลายทางสำหรับแตกไฟล์ (เช่น ./extracted): ").strip() or "./extracted"
        pwd = input("ป้อนรหัสผ่าน (ถ้ามี): ").strip()

        try:
            extract_zip(zip_file, dest_dir, pwd)
        except Exception as err:
            print(f"\n{err}")
    else:
        print("ตัวเลือกไม่ถูกต้อง")
