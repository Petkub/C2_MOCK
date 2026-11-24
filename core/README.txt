ข้อสอบจำลองท้ายค่าย 2 สอวน. คอมพิวเตอร์ (Track A 12 ชุด + Track B 8 ชุด ชุดละ 6 ข้อ 3 ชั่วโมง)
====================================================================

โครงสร้างโฟลเดอร์  (หนึ่งข้อ หนึ่งโฟลเดอร์)
  C2_Mock_Test/
    README.txt, Progress.md
    Judge/                               ตัวตรวจและชุดทดสอบ (ไม่ต้องแก้อะไรในโฟลเดอร์นี้)
    Mock_A01/                            โฟลเดอร์ของชุด A1 (Mock_A01 ... Mock_A12 = Track A, Mock_B01 ... Mock_B08 = Track B)
      Mock_A01.pdf                       โจทย์ทั้งชุด (หน้าปก + 6 ข้อ) ใช้ตอนจับเวลาทำทั้งชุดเหมือนสอบจริง
      Makefile, judge.bat                ใช้ตรวจทั้งชุดหรือตรวจทีละข้อ (make 3 / judge 3)
      1/
      2/
      3/                                 โฟลเดอร์ของข้อ 3
        A01-3.cpp                        ไฟล์คำตอบของข้อนี้ (ชุด A01 ข้อ 3) เริ่มต้นเป็นไฟล์ว่าง เขียน code ลงไฟล์นี้ได้เลย
        3_<ชื่อโจทย์ภาษาอังกฤษ>.pdf        โจทย์ของข้อนี้ข้อเดียว (เนื้อหาเดียวกับในไฟล์ทั้งชุด)
                                         (โฟลเดอร์ของข้อมีแค่สองไฟล์นี้ ไม่มี Makefile / judge.bat)
      4/
      5/
      6/
  ห้ามเปลี่ยนชื่อโฟลเดอร์และชื่อไฟล์ .cpp เพราะ judge รู้ว่าเป็นโจทย์ข้อใดจากชื่อไฟล์ (A01-3.cpp) หรือจากโฟลเดอร์ที่ไฟล์อยู่
  (Mock_A01/3/) ชื่อไฟล์ .cpp ไม่ซ้ำกันทั้งชุด เปิดหลายข้อพร้อมกันใน editor ก็ไม่สับสน

โฟลเดอร์ old/ (เช่น Mock_A01/old/ มีเฉพาะเมื่อจำเป็น): เมื่ออัปเดตแล้วโจทย์ข้อใดถูกเปลี่ยนเป็นโจทย์ใหม่ code ที่เขียนไว้
  ของโจทย์เดิมจะถูกย้ายมาเก็บที่ <โฟลเดอร์ชุด>/old/<ข้อ>_<ชื่อโจทย์เดิม>.cpp ไม่ปนกับโจทย์ใหม่ ส่วนโจทย์ที่ย้ายไปอยู่ข้ออื่น
  หรือชุดอื่น ไฟล์ที่เขียนไว้จะย้ายตามโจทย์ไปเอง (ถ้าที่ใหม่มี code อยู่แล้ว ไฟล์ที่ย้ายมาจะไปอยู่ใน old/ แทน)
  judge แจ้งทุกไฟล์ที่ย้าย ไม่มีไฟล์ใดถูกลบหรือถูกเขียนทับ ไฟล์ว่างที่ยังไม่ได้เขียนไม่ถูกย้าย
  คะแนนที่บันทึกไว้ยังอยู่กับโจทย์ข้อเดิมเสมอ ไฟล์ใน old/ เก็บไว้ให้ดูเท่านั้น จะลบทิ้งเองเมื่อไม่ใช้แล้วก็ได้

การให้คะแนน: ไม่มี subtask — ข้อละ 100 หรือ 0 คะแนนเหมือนข้อสอบจริง (ได้ 100 เมื่อผ่านทุกชุดทดสอบ),
             time limit 1 วินาทีต่อชุด (บางข้อของ Track B 2 วินาที ตามที่เขียนในโจทย์) · judge บอกจำนวนชุดทดสอบที่ผ่านด้วย
การรัน: compile ด้วย g++ -O2 -std=c++17 · หน่วยความจำ 256 MB ต่อชุด (เกินแล้วได้ MLE)
        stack 256 MB ทุกระบบ (recursion ลึก 10^6 ชั้นก็ได้)
ชุดทดสอบ 4 ชุดแรกของทุกข้อคือตัวอย่างในโจทย์

Track A (ชุด A1–A12): ข้อสอบจำลองแบบข้อสอบจริง ชุดละ 6 ข้อ
  ทำตามลำดับ A1 → A12 จับเวลา 3 ชั่วโมงเหมือนสอบจริง: เปิด Mock_A01/Mock_A01.pdf อ่านทั้ง 6 ข้อก่อน เขียนคำตอบของแต่ละข้อ
  ในโฟลเดอร์ของข้อนั้น แล้วตรวจทีละข้อหรือตรวจทั้งชุดก็ได้ ตั้งเป้าให้ผ่านทุกข้อตั้งแต่ส่งครั้งแรก
  และจดไว้ว่าข้อไหนผ่านตั้งแต่ครั้งแรกบ้าง (อัตราผ่านครั้งแรก) · เป้าหมาย: 400 ผ่าน · 500 ลุ้น 5 อันดับแรก · 600 อันดับต้น
Track B (ชุด B1–B8): ยากกว่าข้อสอบจริง / มีเนื้อหาเกินหลักสูตรค่าย 2 สำหรับคนที่ทำ Track A ได้คล่องแล้ว
  ทำตามลำดับ B1 → B8 (ยากขึ้นทีละน้อย) ไม่มีคะแนนเป้าหมาย ข้อท้ายชุดยากกว่าข้อสอบจริง · ความคืบหน้านับแยกจาก Track A

ชุดทดสอบขนาดใหญ่: เพื่อให้ไฟล์ zip เล็ก judge จะสร้างชุดทดสอบใหญ่ของแต่ละข้อในเครื่องตอนตรวจข้อนั้นครั้งแรก
(รอไม่กี่วินาที ครั้งเดียว) และตรวจด้วย checksum ว่าตรงกับต้นฉบับ ถ้าขึ้นข้อความว่าสร้างไม่ได้ ให้แจ้งผู้สอน

วิธีตรวจ (ต้องมี Python 3.7+ และ g++)
  ก) VS Code (ง่ายที่สุด): File > Open Folder... เลือกโฟลเดอร์ C2_Mock_Test (ไม่ใช่ Mock_A01)
     ต้องเป็นโฟลเดอร์ที่มี Judge อยู่ข้างในทันที (ถ้ามี C2_Mock_Test ซ้อนอยู่ใน C2_Mock_Test ให้เลือกอันข้างใน)
     ถ้ากด Ctrl+Shift+B แล้วขึ้นรายการ g++ / gcc ให้เลือกแทนการตรวจ แปลว่าเปิดผิดโฟลเดอร์
     เปิดไฟล์ที่ทำ เช่น Mock_A02/3/A02-3.cpp แล้วกด Ctrl+Shift+B (Mac: Cmd+Shift+B) = ตรวจข้อนั้น
     ตรวจทั้งชุด: Terminal > Run Task... > Judge whole set
  ข) terminal ในโฟลเดอร์ของชุด (เช่น cd Mock_A03)
       Linux / macOS     make 3        (เฉพาะข้อ 3)   make          (ทั้งชุด)
       Windows           judge 3       (เฉพาะข้อ 3)   judge         (ทั้งชุด)   (PowerShell: .\judge 3 และ .\judge)
     หรือดับเบิลคลิก judge.bat ในโฟลเดอร์ชุดนั้น (Windows) เพื่อตรวจทั้งชุด
     ในโฟลเดอร์ของข้อ (เช่น Mock_A03/3) ไม่มี Makefile และ judge.bat จึงสั่ง make / judge ที่นั่นไม่ได้
     ให้ตรวจด้วย Ctrl+Shift+B หรือสั่ง make 3 / judge 3 ในโฟลเดอร์ชุด หรือเรียก judge ตรง ๆ ตามข้อ ค)
  ค) เรียก judge ตรง ๆ (ทุกระบบ  Windows ใช้ python แทน python3)
       ในโฟลเดอร์ข้อ      python3 ../../Judge/judge.py
       ในโฟลเดอร์ชุด      python3 ../Judge/judge.py   (ทั้งชุด)   หรือ   python3 ../Judge/judge.py 3   (เฉพาะข้อ 3)
       จากที่ใดก็ได้       python3 <ที่อยู่ของ C2_Mock_Test>/Judge/judge.py <ไฟล์ .cpp>
  ถ้าจะตรวจไฟล์ชื่ออื่นหรือไฟล์ที่อยู่ที่อื่น ให้ระบุข้อเอง: python3 ../../Judge/judge.py my.cpp A3-5   (ชุด A3 ข้อ 5)
  ดูรายชื่อโจทย์ทั้งหมด (พร้อมโฟลเดอร์และชื่อไฟล์ของแต่ละข้อ): python3 ../Judge/judge.py --list   (พิมพ์ในโฟลเดอร์ชุด)
  ไฟล์ที่ compile แล้วอยู่ใน Judge/.build/ ชั่วคราวและถูกลบเมื่อตรวจเสร็จ ไม่มีไฟล์ใดเพิ่มในโฟลเดอร์ของข้อหรือของชุด
  ตัวเลือก: --tl 2 (เพิ่ม time limit ถ้าเครื่องช้า)  --ml 512 (หน่วยความจำ MB, ปกติ 256)  --diff 5  --stop

ติดตามความคืบหน้า (ข้อที่ผ่านเต็ม 100)
  ทุกครั้งที่ตรวจ judge จะบันทึกคะแนนที่ดีที่สุดของแต่ละข้อไว้ใน Judge/progress.json
  และแสดงแถบสรุปของชุดนั้นท้ายผลตรวจ (✔ = 100, ตัวเลข = คะแนนดีที่สุด, • = ยังไม่ได้ทำ)
  ดูหน้าสรุปเต็มในเทอร์มินัล:  VS Code: เปิดไฟล์ Progress.md แล้วกด Ctrl+Shift+B (Mac: Cmd+Shift+B)
                               หรือ Terminal > Run Task... > Show progress
                               make progress  ·  judge progress (Windows)  ·  python3 ../Judge/judge.py --progress
                               (พิมพ์ในโฟลเดอร์ชุด ถ้าอยู่ในโฟลเดอร์ข้อ ใช้ python3 ../../Judge/judge.py --progress)
                               (ดูเฉพาะชุด A2: python3 ../Judge/judge.py --progress A2)
  ไฟล์คำตอบที่ยังว่างอยู่จะไม่ถูกนับ
  (ถ้าอยากได้ปุ่มลัดแยก เช่น Ctrl+Alt+P: Ctrl+Shift+P > "Preferences: Open Keyboard Shortcuts (JSON)" แล้วเพิ่ม
   {"key": "ctrl+alt+p", "command": "workbench.action.tasks.runTask", "args": "Show progress"} )

Reports to your teacher (Discord) and code copies
  The first time you judge on a computer, the judge asks for the student code your teacher gave you
  (<name>-XXXX; press Enter to skip if you have none yet). In VS Code, click into the terminal panel before typing.
  Then it asks two separate questions:
    1) Send your scores to your teacher? (answer y to get messages in your own Discord channel)
    2) Keep a copy of your code with your teacher? (to move to another computer; n is fine, scores are still sent)
  One login per computer, for both C2_Practice and C2_Mock (file ~/.config/stupidgrader/student.json,
  Windows: %APPDATA%\stupidgrader\student.json).
  What is sent: your student code, the problem, the score, the result of each test (e.g. AAAW), the run number,
  the time, a checksum of your file, and the code of that problem only when code copies are on (64 KB at most).
  Nothing else from your computer.
  It is sent after you see your result (3 seconds at most). Without internet the judge works as usual and sends
  later ("... waiting to be sent to your teacher"). With both turned off, judging works exactly the same.
  Commands (in a set folder; on Windows type python instead of python3)
    python3 ../Judge/judge.py --report status        who you are logged in as, login file, last send, results waiting
    python3 ../Judge/judge.py --report off           stop sending scores (--report on starts again)
    python3 ../Judge/judge.py --sync off             stop keeping code copies (--sync on starts again)
    python3 ../Judge/judge.py --login <name>-XXXX    log in or change account; --logout logs out (your files stay)
  Moving to a new computer
    a) Online (code copies must have been on): install the package on the new computer, judge any problem and
       enter the same code; the judge offers to copy your code there. Later: python3 ../Judge/judge.py --pull
    b) Offline: on the old computer run python3 ../Judge/judge.py --backup (it makes
       <package>_backup_<date-time>.zip next to the Judge folder), copy the zip to the new computer and run
       python3 ../Judge/judge.py --restore <zip file>
    Neither one overwrites a file that already has code: an empty file gets its code back; if there is other code
    in it, the copy goes to <set folder>/old/<problem>_cloud_<date>.cpp (from a zip: _backup_), so you can compare
    and choose.
  Shared computer: put your own code on one line in Judge/.student; this package then uses that file instead.

การอัปเดต: เมื่อต่ออินเทอร์เน็ต judge จะอัปเดตตัวเองจาก GitHub อัตโนมัติ (ตรวจสอบไม่เกินทุก 10 นาที ไฟล์ .cpp ของคุณ
จะไม่ถูกแก้ ถ้าโจทย์ถูกย้ายหรือถูกเปลี่ยน ไฟล์ที่เขียนไว้จะย้ายตามที่อธิบายในหัวข้อโฟลเดอร์ old/ ข้างบน)
บังคับตรวจสอบทันที (พิมพ์ในโฟลเดอร์ชุด): python3 ../Judge/judge.py --update  (เลขเวอร์ชันแสดงในกรอบหัวเรื่อง)
