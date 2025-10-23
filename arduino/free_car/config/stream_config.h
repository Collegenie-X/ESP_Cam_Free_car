#ifndef STREAM_CONFIG_H
#define STREAM_CONFIG_H

/**
 * 스트리밍 설정 헤더 파일
 * FPS 및 메모리 관리 설정
 */

// ========== FPS 설정 ==========
// 메모리 누수 방지 및 제어 응답성을 위해 낮은 FPS 권장
// 옵션 1: 5 FPS (매우 안정적, 제어 명령 빠름) - 권장
// 옵션 2: 10 FPS (안정적, 제어 명령 정상)
// 옵션 3: 15 FPS (균형)

#define STREAM_FPS_MODE 1  // 1: 5 FPS, 2: 10 FPS, 3: 15 FPS

#if STREAM_FPS_MODE == 1
    #define STREAM_DELAY_MS 200     // 5 FPS
    #define STREAM_MODE_NAME "안정 모드 (5 FPS, 제어 우선)"
#elif STREAM_FPS_MODE == 2
    #define STREAM_DELAY_MS 100     // 10 FPS
    #define STREAM_MODE_NAME "균형 모드 (10 FPS)"
#elif STREAM_FPS_MODE == 3
    #define STREAM_DELAY_MS 66      // 15 FPS
    #define STREAM_MODE_NAME "부드러움 모드 (15 FPS)"
#else
    #define STREAM_DELAY_MS 200     // 기본값: 5 FPS
    #define STREAM_MODE_NAME "안정 모드 (5 FPS, 제어 우선)"
#endif

// ========== 메모리 관리 설정 ==========
// 메모리 경고 임계값 (bytes)
#define MEMORY_WARNING_THRESHOLD 100000   // 100KB 이하 시 경고

// 메모리 위험 임계값 (bytes)
#define MEMORY_CRITICAL_THRESHOLD 80000   // 80KB 이하 시 위험

// 메모리 체크 간격 (ms)
#define MEMORY_CHECK_INTERVAL 5000        // 5초마다

// 메모리 정리 간격 (프레임 단위)
#define MEMORY_CLEANUP_INTERVAL 100       // 100프레임마다

// ========== HTTP 서버 응답성 설정 ==========
// 스트림 중에도 다른 HTTP 요청(모터 제어 등)을 처리하기 위한 설정
#define YIELD_INTERVAL_FRAMES 1     // 매 프레임마다 제어권 양보
#define EXTRA_YIELD_DELAY_MS 50     // 추가 양보 대기 시간

// ========== 디버그 설정 ==========
// 디버그 출력 활성화 (true: 활성화, false: 비활성화)
#define STREAM_DEBUG_ENABLED true

/**
 * 스트림 설정 정보 출력
 */
void printStreamConfig() {
    Serial.println("\n========== 스트리밍 설정 ==========");
    Serial.printf("모드: %s\n", STREAM_MODE_NAME);
    Serial.printf("프레임 지연: %d ms\n", STREAM_DELAY_MS);
    Serial.printf("메모리 경고: %d bytes\n", MEMORY_WARNING_THRESHOLD);
    Serial.printf("메모리 위험: %d bytes\n", MEMORY_CRITICAL_THRESHOLD);
    Serial.printf("디버그: %s\n", STREAM_DEBUG_ENABLED ? "활성화" : "비활성화");
    Serial.println("====================================\n");
}

#endif // STREAM_CONFIG_H

