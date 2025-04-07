import pigpio
import time

GPIO_PIN = 27  # البن المتصل بخط DATA من المستقبل

# إنشاء كائن pigpio
pi = pigpio.pi()
if not pi.connected:
    exit("❌ لم يتم الاتصال بـ pigpio daemon. تأكد من تشغيل sudo pigpiod.")

print(f"📡 الاستماع على GPIO {GPIO_PIN}...")

# إعداد المتغيرات
last_tick = None
timings = []

# دالة المعالجة عند حدوث نبضة
def rf_callback(gpio, level, tick):
    global last_tick, timings

    if level == pigpio.TIMEOUT:
        if len(timings) > 5:  # تأكد أنه فيه إشارة حقيقية
            print("\n✅ تم التقاط إشارة:")
            print("🕒 الفترات الزمنية (us):")
            print(timings)
        timings = []
        return

    if last_tick is not None:
        delta = pigpio.tickDiff(last_tick, tick)
        timings.append(delta)
    last_tick = tick

# إعداد الـ GPIO
pi.set_mode(GPIO_PIN, pigpio.INPUT)
pi.set_pull_up_down(GPIO_PIN, pigpio.PUD_DOWN)
pi.set_watchdog(GPIO_PIN, 10)  # 10ms = 10000µs، لإنهاء الإشارة

# تعيين الكولباك
cb = pi.callback(GPIO_PIN, pigpio.EITHER_EDGE, rf_callback)

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n📴 تم إيقاف البرنامج.")

finally:
    cb.cancel()
    pi.stop()
