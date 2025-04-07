import pigpio
import time

TX_GPIO = 22

pi = pigpio.pi()
if not pi.connected:
    exit("لم يتم الاتصال بـ pigpio daemon.")

pi.set_mode(TX_GPIO, pigpio.OUTPUT)

def send_code(code="101010101010101010101010"):
    short = 350
    long = 1050
    sync = 3000

    pulses = []

    for bit in code:
        if bit == "1":
            pulses.append(pigpio.pulse(1 << TX_GPIO, 0, long))
            pulses.append(pigpio.pulse(0, 1 << TX_GPIO, short))
        else:
            pulses.append(pigpio.pulse(1 << TX_GPIO, 0, short))
            pulses.append(pigpio.pulse(0, 1 << TX_GPIO, long))

    # نبضة المزامنة
    pulses.append(pigpio.pulse(0, 1 << TX_GPIO, sync))

    pi.wave_add_generic(pulses)
    wid = pi.wave_create()

    if wid >= 0:
        for _ in range(10):  # إرسال الكود 10 مرات
            pi.wave_send_once(wid)
            while pi.wave_tx_busy():
                time.sleep(0.01)
            time.sleep(0.01)

        print("✅ تم إرسال الكود.")
        pi.wave_delete(wid)
    else:
        print("❌ فشل في إنشاء الويف")

send_code()

pi.stop()
