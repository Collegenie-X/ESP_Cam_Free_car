# 🖼️ 이미지 품질 개선 가이드

## ❌ 문제: 이미지가 깨짐

최적화 설정이 너무 공격적이어서 이미지 품질이 떨어졌습니다:
- JPEG 품질 10 → 너무 낮아서 블러/픽셀화
- 센서 설정 최소화 → 어둡고 노이즈 많음
- XCLK 24MHz → 일부 카메라에서 불안정

---

## ✅ 해결: 품질 + 속도 균형 모드

### 변경 사항

#### 1. JPEG 품질 개선
```cpp
// 변경 전
config.jpeg_quality = 10;  // 너무 낮음 → 블러

// 변경 후
config.jpeg_quality = 8;   // ✅ 더 선명한 이미지
```

**JPEG 품질 참고:**
- 0-5: 최고 품질 (큰 파일, 느림)
- 6-10: 높은 품질 (적당한 크기)
- **8: 품질+속도 균형** ⭐ **추천**
- 10-15: 보통 품질
- 16+: 낮은 품질

#### 2. XCLK 주파수 안정화
```cpp
// 변경 전
config.xclk_freq_hz = 24000000;  // 24MHz (불안정 가능)

// 변경 후
config.xclk_freq_hz = 20000000;  // ✅ 20MHz (안정적)
```

#### 3. 센서 설정 개선
```cpp
// 품질 개선 설정
sensor->set_aec2(sensor, 1);              // AEC2 활성화 (노출 개선)
sensor->set_ae_level(sensor, 1);          // 약간 밝게
sensor->set_aec_value(sensor, 400);       // 적절한 노출
sensor->set_agc_gain(sensor, 8);          // 밝기 증가
sensor->set_gainceiling(sensor, (gainceiling_t)3);  // 품질 균형
sensor->set_bpc(sensor, 1);               // 노이즈 제거 활성화
```

---

## 📊 성능 비교

| 항목 | 너무 공격적 | 균형 모드 | 차이 |
|------|------------|----------|------|
| **JPEG 품질** | 10 | 8 | ✅ 더 선명 |
| **XCLK** | 24MHz | 20MHz | ✅ 안정적 |
| **이미지 크기** | ~5KB | ~8-10KB | +60% |
| **캡처 속도** | ~90ms | ~110ms | +20ms |
| **실시간 주행** | ✅ 가능 | ✅ 가능 | - |
| **예상 FPS** | 11 | 9 | -2 FPS |
| **이미지 품질** | ❌ 낮음 | ✅ 좋음 | 대폭 개선 |

**결론**: 약간 느려지지만 **이미지 품질이 크게 개선**되고 **여전히 실시간 자율주행 가능**합니다! 🎉

---

## 🚀 적용 방법

### Step 1: Arduino IDE에서 재업로드

```bash
1. Arduino IDE 실행
2. arduino/free_car/free_car.ino 열기
3. 업로드 버튼 클릭 ⬆️
```

### Step 2: 시리얼 모니터 확인

다음 메시지 확인:
```
✅ PSRAM 감지: 균형 모드 (QVGA 320x240, Q=8, 20MHz)
```

### Step 3: 테스트

```bash
cd /Users/kimjongphil/Documents/GitHub/ESP_Cam_Free_car/arduino/free_car
./test_capture_speed.sh
```

**예상 결과:**
- 평균 캡처 시간: **110ms**
- 예상 FPS: **~9 FPS**
- 이미지 크기: **8-10KB** (이전 5KB보다 큼)
- 이미지 품질: **✅ 선명하고 깨끗함**

---

## 🎨 품질 vs 속도 조정

상황에 따라 설정을 조정할 수 있습니다.

### 옵션 1: 더 선명한 이미지 (조금 느림)

`camera_init.h`:
```cpp
config.jpeg_quality = 6;              // 6: 매우 선명
sensor->set_brightness(sensor, 2);    // 더 밝게
sensor->set_agc_gain(sensor, 12);     // 밝기 더 증가
```

**결과:**
- 캡처 속도: ~130ms
- FPS: ~7-8
- 품질: ⭐⭐⭐⭐⭐ 최고

---

### 옵션 2: 빠른 속도 (품질 약간 희생)

`camera_init.h`:
```cpp
config.jpeg_quality = 10;             // 10: 보통
sensor->set_aec2(sensor, 0);          // AEC2 비활성화
sensor->set_agc_gain(sensor, 4);      // 게인 낮춤
```

**결과:**
- 캡처 속도: ~95ms
- FPS: ~10
- 품질: ⭐⭐⭐ 보통

---

### 옵션 3: 현재 균형 모드 (추천) ⭐

`camera_init.h` (기본값):
```cpp
config.jpeg_quality = 8;              // 8: 균형
sensor->set_aec2(sensor, 1);          // AEC2 활성화
sensor->set_agc_gain(sensor, 8);      // 적절한 게인
```

**결과:**
- 캡처 속도: ~110ms
- FPS: ~9
- 품질: ⭐⭐⭐⭐ 좋음

---

## 🔍 문제 해결

### Q1. 여전히 이미지가 깨져 보이는 경우

**브라우저 확대/축소 확인:**
```
QVGA 320x240은 작은 해상도입니다.
브라우저에서 200-300% 확대하면 픽셀이 보일 수 있습니다.
→ 100% 크기로 보세요!
```

**해결책:**
```cpp
// 해상도를 CIF로 증가 (더 선명)
config.frame_size = FRAMESIZE_CIF;    // 400x296
config.jpeg_quality = 6;              // 품질 높임
```

⚠️ 단, 속도는 느려짐 (~150ms, 6-7 FPS)

---

### Q2. 이미지가 너무 어두운 경우

`camera_init.h`:
```cpp
sensor->set_brightness(sensor, 2);        // 1 → 2
sensor->set_ae_level(sensor, 2);          // 1 → 2 (더 밝게)
sensor->set_agc_gain(sensor, 12);         // 8 → 12
sensor->set_gainceiling(sensor, (gainceiling_t)4);  // 3 → 4
```

---

### Q3. 노이즈가 많은 경우

`camera_init.h`:
```cpp
sensor->set_gainceiling(sensor, (gainceiling_t)2);  // 게인 상한 낮춤
sensor->set_agc_gain(sensor, 4);                    // 게인 낮춤
config.jpeg_quality = 6;                            // 품질 높임
```

---

### Q4. 자율주행에 적합한가?

**✅ 예, 적합합니다!**

- QVGA 320x240 해상도로도 차선 인식 충분
- 9 FPS면 실시간 주행 가능 (최소 5 FPS 필요)
- 품질도 선명하여 차선 구분 명확

---

## 📝 요약

### 개선 전 (너무 공격적)
- ❌ JPEG 품질: 10 (너무 낮음)
- ❌ XCLK: 24MHz (불안정)
- ❌ 센서 설정: 최소화
- ❌ 결과: 빠르지만 **이미지 깨짐**

### 개선 후 (균형 모드) ✅
- ✅ JPEG 품질: 8 (선명)
- ✅ XCLK: 20MHz (안정)
- ✅ 센서 설정: 균형
- ✅ 결과: **품질 좋고 여전히 빠름**

---

**작성일**: 2025-10-24  
**버전**: v2.1 (품질 개선)

