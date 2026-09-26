import os
import socket
import struct
import threading
import time
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
import tftpy

# البورتات المستهدفة للبحث والاستجابة
TARGET_PORTS = {
    6666: "U-Boot NetConsole",
    9000: "Magic UDP Trigger",
    8080: "HTTP Web Recovery",
    23: "Telnet Serial-IP",
}


class SttitenUpdateUI(BoxLayout):

  def __init__(self, **kwargs):
    super().__init__(orientation="vertical", padding=12, spacing=8, **kwargs)

    # Title
    self.add_widget(
        Label(
            text="Sttiten Update v1.0",
            font_size="22sp",
            bold=True,
            size_hint_y=None,
            height=35,
            color=(0.12, 0.53, 0.9, 1),
        )
    )

    # Inputs Layout (IP, MAC)
    grid = GridLayout(cols=2, spacing=5, size_hint_y=None, height=90)

    grid.add_widget(
        Label(
            text="عنوان IP:",
            size_hint_x=0.3,
            halign="right",
            valign="middle",
        )
    )
    self.ip_input = TextInput(
        text="192.168.1.50",
        multiline=False,
        hint_text="مثال: 192.168.1.50",
    )
    grid.add_widget(self.ip_input)

    grid.add_widget(
        Label(
            text="عنوان MAC:",
            size_hint_x=0.3,
            halign="right",
            valign="middle",
        )
    )
    self.mac_input = TextInput(
        text="00:1A:79:XX:XX:XX",
        multiline=False,
        hint_text="AA:BB:CC:DD:EE:FF",
    )
    grid.add_widget(self.mac_input)

    self.add_widget(grid)

    # File Selection Layout
    file_box = BoxLayout(
        orientation="horizontal", spacing=5, size_hint_y=None, height=40
    )
    self.file_input = TextInput(
        hint_text="مسار ملف التحديث (.bin)",
        multiline=False,
        readonly=True,
    )
    file_box.add_widget(self.file_input)

    btn_browse = Button(
        text="اختر .bin", size_hint_x=0.3, background_color=(0.2, 0.4, 0.8, 1)
    )
    btn_browse.bind(on_press=self.open_file_chooser)
    file_box.add_widget(btn_browse)

    self.add_widget(file_box)

    # Console Log Box
    self.log_output = Label(
        text="★ جاهز لبدء العملية...\n",
        size_hint_y=None,
        halign="left",
        valign="top",
        color=(0, 1, 0, 1),
    )
    self.log_output.bind(size=self.log_output.setter("text_size"))

    scroll = ScrollView(size_hint=(1, 1))
    scroll.add_widget(self.log_output)
    self.add_widget(scroll)

    # Start Action Button
    self.start_btn = Button(
        text="تنشيط وفحص وتمرير التحديث",
        size_hint_y=None,
        height=50,
        bold=True,
        background_color=(0.15, 0.65, 0.25, 1),
    )
    self.start_btn.bind(on_press=self.start_process)
    self.add_widget(self.start_btn)

    self.local_ip = self.get_local_ip()

  def get_local_ip(self):
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      s.connect(("8.8.8.8", 80))
      ip = s.getsockname()[0]
      s.close()
      return ip
    except Exception:
      return "127.0.0.1"

  def log(self, message):
    def update_text(dt):
      self.log_output.text += f"[{time.strftime('%H:%M:%S')}] {message}\n"

    Clock.schedule_once(update_text)

  def open_file_chooser(self, instance):
    content = BoxLayout(orientation="vertical")
    filechooser = FileChooserListView(
        path="/sdcard" if os.path.exists("/sdcard") else "."
    )
    content.add_widget(filechooser)

    btn_layout = BoxLayout(size_hint_y=None, height=40)
    btn_select = Button(text="موافق")
    btn_cancel = Button(text="إلغاء")
    btn_layout.add_widget(btn_select)
    btn_layout.add_widget(btn_cancel)
    content.add_widget(btn_layout)

    popup = Popup(
        title="اختر ملف التحديث .bin", content=content, size_hint=(0.9, 0.9)
    )

    def select_file(inst):
      if filechooser.selection:
        selected = filechooser.selection[0]
        if selected.endswith(".bin"):
          self.file_input.text = selected
          popup.dismiss()
        else:
          self.log("❌ خطأ: يجب اختيار ملف ينتهي بـ .bin")

    btn_select.bind(on_press=select_file)
    btn_cancel.bind(on_press=popup.dismiss)
    popup.open()

  def send_mac_trigger(self, mac_str, target_ip):
    """إرسال حزمة Magic Packet بالاعتماد على الـ MAC Address للتنشيط الشبكي"""
    try:
      clean_mac = mac_str.replace(":", "").replace("-", "")
      if len(clean_mac) != 12:
        self.log("⚠️ تنبيه: صيغة MAC غير دقيقة، تم التجاوز...")
        return
      mac_bytes = bytes.fromhex(clean_mac)
      magic_packet = b"\xff" * 6 + mac_bytes * 16

      sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

      # إرسال الحزمة المباشرة والعامة
      sock.sendto(magic_packet, ("255.255.255.255", 9000))
      sock.sendto(magic_packet, (target_ip, 9000))
      sock.close()
      self.log(f"✔ تم إرسال حزمة التنشيث للـ MAC: {mac_str}")
    except Exception as e:
      self.log(f"خطأ في إرسال MAC Packet: {e}")

  def scan_ports(self, target_ip):
    self.log(f"مسح البورتات على الهدف: {target_ip}...")
    for port, desc in TARGET_PORTS.items():
      try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)
        if sock.connect_ex((target_ip, port)) == 0:
          self.log(f"✔ تم اكتشاف بورت مفتوح: {port} ({desc})")
          sock.close()
          return port
        sock.close()
      except Exception:
        pass
    return 6666  # Default UDP NetConsole Port

  def run_pipeline(self):
    target_ip = self.ip_input.text.strip()
    mac_str = self.mac_input.text.strip()
    fw_path = self.file_input.text.strip()

    if not target_ip:
      self.log("❌ خطأ: أدخل عنوان IP أولاً.")
      self.start_btn.disabled = False
      return

    if not os.path.exists(fw_path) or not fw_path.endswith(".bin"):
      self.log("❌ خطأ: يرجى اختيار ملف .bin صحيح للتحديث.")
      self.start_btn.disabled = False
      return

    # 1. التنشيط بالـ MAC Address
    if mac_str:
      self.send_mac_trigger(mac_str, target_ip)

    # 2. اكتشاف البورت
    port = self.scan_ports(target_ip)

    # 3. تشغيل خادم TFTP بدون روت على بورت غير قياسي (6969)
    # ملاحظة: تم تعديل البورت لـ 6969 ليعمل على أندرويد بدون صلاحيات روت
    tftp_port = 6969
    self.log(f"بدء خادم TFTP محلي على البورت {tftp_port} (بدون روت)...")
    fw_dir = os.path.dirname(fw_path)
    fw_name = os.path.basename(fw_path)

    try:
      server = tftpy.TftpServer(fw_dir)
      threading.Thread(
          target=server.listen, args=(self.local_ip, tftp_port), daemon=True
      ).start()
    except Exception as e:
      self.log(f"تنبيه سيرفر TFTP: {e}")

    # 4. إرسال أمر التحديث المباشر عبر الشبكة
    self.log("إرسال أمر التفليش للبوتلودر...")
    try:
      sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      # أمر يوجه البوتلودر للسحب من سيرفر الـ TFTP عبر البورت المخصص
      payload = (
          f"tftp 0x80000000 {self.local_ip}:{tftp_port} {fw_name}; flash"
          " write\n"
      )

      for _ in range(8):
        sock.sendto(b"\x03\x03\x03", (target_ip, port))
        sock.sendto(payload.encode("utf-8"), (target_ip, port))
        time.sleep(0.08)

      sock.close()
      self.log("==========================================")
      self.log("✔ تم إرسال أوامر التحديث بنجاح!")
      self.log("أعد تشغيل الرسيفر الآن (Power Cycle) ليتم التفليش.")
      self.log("==========================================")
    except Exception as e:
      self.log(f"❌ خطأ أثناء إرسال الأوامر: {e}")

    self.start_btn.disabled = False

  def start_process(self, instance):
    self.start_btn.disabled = True
    threading.Thread(target=self.run_pipeline, daemon=True).start()


class SttitenUpdateApp(App):

  def build(self):
    return SttitenUpdateUI()


if __name__ == "__main__":
  SttitenUpdateApp().run()
