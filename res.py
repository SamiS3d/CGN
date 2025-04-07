#include <stdio.h>
#include <stdlib.h>
#include <math.h>

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
    // الفترات الزمنية الملتقطة (بـ µs)
    int periods[] = {10265, 1100, 250, 425, 921, 1079, 280, 395, 945, 406, 929, 405, 936, 1084, 270, 395, 945, 400, 945};
    int size = sizeof(periods) / sizeof(periods[0]);

    // تطبيق فلتر المتوسط المتحرك
    int window_size = 3;  // حجم النافذة لتصفية الضوضاء
    applyMovingAverageFilter(periods, size, window_size);

    // تحليل الفترات الزمنية
    analyzePeriods(periods, size);

    // تحويل الفترات إلى كود ثنائي
    convertToBinaryCode(periods, size);

    return 0;
}
