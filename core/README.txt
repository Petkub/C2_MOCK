ข้อสอบจำลองท้ายค่าย 2 สอวน. คอมพิวเตอร์ (ชุดละ 5 ข้อ 3 ชั่วโมง)
====================================================================

  Mock_K/Mock_K.pdf        โจทย์ชุดที่ K (หน้าปก + 5 ข้อ ข้อละ 1 หน้า)
  Mock_K/1.cpp ... 5.cpp   ไฟล์คำตอบ เขียน code ลงไฟล์เหล่านี้
  Judge/                   ตัวตรวจและชุดทดสอบ (ไม่ต้องแก้)

การให้คะแนน: ไม่มี subtask — คะแนนข้อละ 100 x (ชุดทดสอบที่ผ่าน / ชุดทดสอบทั้งหมด), time limit 1 วินาทีต่อชุด
ชุดทดสอบ 5 ชุดแรกของทุกข้อคือตัวอย่างในโจทย์

ชุดทดสอบขนาดใหญ่: เพื่อให้ไฟล์ zip เล็ก judge จะสร้างชุดทดสอบใหญ่ของแต่ละข้อในเครื่องตอนตรวจข้อนั้นครั้งแรก
(รอไม่กี่วินาที ครั้งเดียว) และตรวจด้วย checksum ว่าตรงกับต้นฉบับ ถ้าขึ้นข้อความว่าสร้างไม่ได้ ให้แจ้งผู้สอน

วิธีตรวจ (ต้องมี Python 3.7+ และ g++)
  ก) VS Code (ง่ายที่สุด): File > Open Folder... เลือกโฟลเดอร์ C2_Mock_Test (ไม่ใช่ Mock_K)
     เปิดไฟล์ที่ทำ เช่น Mock_2/3.cpp แล้วกด Ctrl+Shift+B (Mac: Cmd+Shift+B) = ตรวจข้อนั้น
     ตรวจทั้งชุด: Terminal > Run Task... > Judge whole set
  ข) terminal ในโฟลเดอร์ Mock_K:
  Linux / macOS   make (ทั้งชุด)  ·  make 3 (เฉพาะข้อ 3)
  Windows         judge (ทั้งชุด) ·  judge 3   หรือดับเบิลคลิก judge.bat
  ทุกระบบ         python3 ../Judge/judge.py   ·   python3 ../Judge/judge.py 3.cpp
  ตัวเลือก: --tl 2 (เพิ่ม time limit ถ้าเครื่องช้า)  --diff 5  --stop

ติดตามความคืบหน้า (ข้อที่ผ่านเต็ม 100)
  ทุกครั้งที่ตรวจ judge จะบันทึกคะแนนที่ดีที่สุดของแต่ละข้อไว้ใน Judge/progress.json
  และแสดงแถบสรุปของชุดนั้นท้ายผลตรวจ (✔ = 100, ตัวเลข = คะแนนดีที่สุด, • = ยังไม่ได้ทำ)
  ดูหน้าสรุปเต็มในเทอร์มินัล:  VS Code: เปิดไฟล์ Progress.md แล้วกด Ctrl+Shift+B (Mac: Cmd+Shift+B)
                               หรือ Terminal > Run Task... > Show progress
                               make progress  ·  judge progress (Windows)  ·  python3 ../Judge/judge.py --progress
                               (ดูเฉพาะชุดที่ 2: python3 ../Judge/judge.py --progress 2)
  ไฟล์ starter ที่ยังไม่ได้แก้จะไม่ถูกนับ
  (ถ้าอยากได้ปุ่มลัดแยก เช่น Ctrl+Alt+P: Ctrl+Shift+P > "Preferences: Open Keyboard Shortcuts (JSON)" แล้วเพิ่ม
   {"key": "ctrl+alt+p", "command": "workbench.action.tasks.runTask", "args": "Show progress"} )
Updates: the judge updates itself from GitHub when online (checked at most once an hour; your .cpp files
are never touched). Force a check: python3 ../Judge/judge.py --update   (version shown in the header box)
