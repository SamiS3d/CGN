import pigpio
import time

GPIO_PIN = 27

pi = pigpio.pi()
if not pi.connected:
    exit("❌ لم يتم الاتصال بـ pigpio daemon. تأكد من تشغيل sudo pigpiod.")

print(f"📡 الاستماع على GPIO {GPIO_PIN}...")

last_tick = None
timings = []

def decode_timings(timings):
    bits = ""
    i = 0

    if timings and timings[0] > 5000:
        print("🔍 تم الكشف عن نبضة sync")
        timings.pop(0)

    while i < len(timings) - 1:
        short = timings[i]
        long = timings[i + 1]

        if short > 2000 or long > 2000:
            print(f"⚠️ تجاهل نبضة طويلة جدًا: short={short}, long={long}")
            i += 2
            continue

        if short < 50 or long < 50:
            print(f"⚠️ تجاهل نبضة ضوضاء: short={short}, long={long}")
            i += 2
            continue

        if 50 < short < 350 and 350 < long < 1000:
            bits += "1"
        elif 350 < short < 1000 and 50 < long < 350:
            bits += "0"
        else:
            print(f"⚠️ فترات غير معروفة: short={short}, long={long}")
            bits += "?"

        i += 2

    return bits

def rf_callback(gpio, level, tick):
    global last_tick, timings

    if level == pigpio.TIMEOUT:
        if len(timings) > 20:
            print("\n✅ تم التقاط إشارة:")
            print("🕒 الفترات (µs):", timings)

            with open("timings.txt", "a") as f:
                f.write(str(timings) + "\n")

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

pi.set_mode(GPIO_PIN, pigpio.INPUT)
pi.set_pull_up_down(GPIO_PIN, pigpio.PUD_DOWN)
pi.set_watchdog(GPIO_PIN, 20)

cb = pi.callback(GPIO_PIN, pigpio.EITHER_EDGE, rf_callback)

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n📴 تم إيقاف البرنامج.")

finally:
    cb.cancel()
    pi.stop()
