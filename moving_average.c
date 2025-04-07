#include <stdio.h>
#include <stdlib.h>
#include <pigpio.h>
#include <time.h>

// دالة لتصفية الضوضاء عبر حساب المتوسط المتحرك
void applyMovingAverageFilter(int* data, int size, int window_size) {
    int* filtered_data = (int*)malloc(size * sizeof(int));
    for (int i = 0; i < size; i++) {
        int start = i - window_size / 2;
        int end = i + window_size / 2;
        if (start < 0) start = 0;
        if (end >= size) end = size - 1;

        int sum = 0;
        int count = 0;
        for (int j = start; j <= end; j++) {
            sum += data[j];
            count++;
        }
        filtered_data[i] = sum / count;
    }

    // تحديث البيانات بعد التصفية
    for (int i = 0; i < size; i++) {
        data[i] = filtered_data[i];
    }

    free(filtered_data);
}

// دالة لتحويل الفترات الزمنية إلى قيمة ثنائية
void convertToBinaryCode(int* periods, int size) {
    printf("الكود الثنائي:\n");
    for (int i = 0; i < size; i++) {
        if (periods[i] < 500) {
            printf("0");
        } else {
            printf("1");
        }
    }
    printf("\n");
}

// دالة لفحص الفترات واستخراج الفترات المناسبة
void analyzePeriods(int* periods, int size) {
    int threshold_short = 500;
    int threshold_long = 1000;

    for (int i = 0; i < size; i++) {
        if (periods[i] < threshold_short) {
            printf("فترة قصيرة: %d µs\n", periods[i]);
        } else if (periods[i] > threshold_long) {
            printf("فترة طويلة: %d µs\n", periods[i]);
        } else {
            printf("فترة غير معروفة: %d µs\n", periods[i]);
        }
    }
}

int main() {
    // تهيئة مكتبة pigpio
    if (gpioInitialise() < 0) {
        printf("فشل في تهيئة مكتبة pigpio\n");
        return 1;
    }

    // تحديد GPIO 27 كدخال
    int gpio_pin = 27;
    gpioSetMode(gpio_pin, PI_INPUT);

    // متغيرات لتخزين الفترات الزمنية
    int periods[1000]; // تخزين الفترات الزمنية
    int period_count = 0;

    // قراءة الإشارة بشكل مستمر
    int previous_level = 0;
    uint32_t previous_time = 0;
    while (1) {
        int current_level = gpioRead(gpio_pin);
        uint32_t current_time = gpioTick();

        if (current_level != previous_level) {
            // إذا تغيرت الحالة، احسب الفترة الزمنية
            if (previous_level == 1) {
                // إذا كانت الإشارة كانت HIGH في المرة السابقة
                int period = current_time - previous_time;
                periods[period_count++] = period;
                printf("فترة: %d µs\n", period);
            }

            previous_level = current_level;
            previous_time = current_time;
        }

        // إذا تم جمع 1000 فترة، قم بتحليلها
        if (period_count >= 1000) {
            // تطبيق فلتر المتوسط المتحرك
            int window_size = 3;  // حجم النافذة لتصفية الضوضاء
            applyMovingAverageFilter(periods, period_count, window_size);

            // تحليل الفترات الزمنية
            analyzePeriods(periods, period_count);

            // تحويل الفترات إلى كود ثنائي
            convertToBinaryCode(periods, period_count);

            // إنهاء البرنامج بعد التحليل
            break;
        }
    }

    // إنهاء مكتبة pigpio
    gpioTerminate();
    return 0;
}
