import pigpio
import time

GPIO_PIN = 27  # البن المتصل بـ DATA من المستقبل

# إنشاء كائن pigpio
pi = pigpio.pi()
if not pi.connected:
    exit("❌ لم يتم الاتصال بـ pigpio daemon. تأكد من تشغيل sudo pigpiod.")

print(f"📡 الاستماع على GPIO {GPIO_PIN}...")

last_tick = None
timings = []

# دالة لتحليل الفترات وتحويلها لبتات
def decode_timings(timings):
    bits = ""
    i = 0

    while i < len(timings) - 1:
        short = timings[i]
        long = timings[i + 1]

        # تصفية الضوضاء باستخدام حدود منطقية (300-600µs للنبضات القصيرة، 800-1300µs للنبضات الطويلة)
        if 200 < short < 600 and 800 < long < 1400:
            bits += "1"
        elif 800 < short < 1400 and 200 < long < 600:
            bits += "0"
        else:
            # تجاهل الفترات غير المنطقية
            print(f"⚠️ فترات غير معروفة: short={short}, long={long}")
            bits += "?"  # أو تجاهلها

        i += 2

    return bits

# الكولباك عند كل تغيير إشارة
def rf_callback(gpio, level, tick):
    global last_tick, timings

    if level == pigpio.TIMEOUT:
        if len(timings) > 20:  # تأكد إنه فيه إشارة حقيقية
            print("\n✅ تم التقاط إشارة:")
            print("🕒 الفترات (µs):", timings)

            binary = decode_timings(timings)
            print("📡 الكود الثنائي:")
            print(binary)

            if "?" not in binary and len(binary) >= 20:
                print("✅ كود نظيف ومفهوم ✅")
            else:
                print("⚠️ كود غير واضح أو فيه ضوضاء.")

        timings = []
        return

    if last_tick is not None:
        delta = pigpio.tickDiff(last_tick, tick)
        timings.append(delta)
    last_tick = tick

# إعدادات GPIO
pi.set_mode(GPIO_PIN, pigpio.INPUT)
pi.set_pull_up_down(GPIO_PIN, pigpio.PUD_DOWN)
pi.set_watchdog(GPIO_PIN, 10)  # 10ms = 10000µs لفصل الإشارة

# تفعيل الكولباك
cb = pi.callback(GPIO_PIN, pigpio.EITHER_EDGE, rf_callback)

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n📴 تم إيقاف البرنامج.")

finally:
    cb.cancel()
    pi.stop()
