# 카메라 파라미터 테스트 가이드

## 현재 UI에 표시되는 3개 섹션

### 1. 🌟 기본 설정
- **brightness** (밝기): -2 ~ 2, 기본값 2 ✅ 아두이노 지원 확인됨
- **contrast** (대비): -2 ~ 2, 기본값 2 ✅ 아두이노 지원 확인됨
- **saturation** (채도): -2 ~ 2, 기본값 1 ✅ 아두이노 지원 확인됨

### 2. 💡 노출/게인 설정
- **agc_gain** (AGC 게인): 0 ~ 30, 기본값 30 ✅ 아두이노 지원 확인됨
- **gainceiling** (게인 상한): 0 ~ 6, 기본값 6 ✅ 아두이노 지원 확인됨
- **aec_value** (노출 시간): 0 ~ 2000, 기본값 2000 ✅ 아두이노 지원 확인됨
- **aec2** (자동 노출 DSP): 0/1, 기본값 1 ✅ 아두이노 지원 확인됨

### 3. 🖼️ 품질/노이즈
- **quality** (JPEG 품질): 4 ~ 63, 기본값 10 ⚠️ **테스트 필요**
- **denoise** (노이즈 제거): 0 ~ 8, 기본값 0 ⚠️ **테스트 필요**

## 테스트 방법

1. **Flask 서버 실행**
   ```bash
   cd frontend
   ./run.sh
   ```

2. **브라우저에서 접속**
   - http://localhost:5000

3. **각 슬라이더 테스트**
   - 기본 설정 3개는 아두이노에서 확인됨 (작동 보장)
   - 노출/게인 설정 4개도 아두이노에서 확인됨 (작동 보장)
   - **품질/노이즈 2개는 테스트가 필요합니다**

4. **501 에러 확인**
   - quality 또는 denoise 슬라이더를 움직일 때
   - 활동 로그에 "미지원 카메라 파라미터" 메시지가 뜨면
   - 해당 슬라이더가 자동으로 비활성화됩니다

## 아두이노 서버에서 미지원 파라미터 제거 방법

만약 quality 또는 denoise가 작동하지 않으면:

1. `frontend/config.py` 열기
2. `SUPPORTED_CAMERA_PARAMS` 섹션에서 해당 라인 주석 처리:

```python
SUPPORTED_CAMERA_PARAMS = {
    # 기본 설정
    "brightness",
    "contrast",
    "saturation",
    # 노출/게인 설정
    "agc_gain",
    "gainceiling",
    "aec_value",
    "aec2",
    # 품질/노이즈 (작동 안 하면 아래 주석 처리)
    # "quality",       # ← 이렇게 주석 처리
    # "denoise",       # ← 이렇게 주석 처리
}
```

3. 서버 재시작

## 야간 모드 설정 (모든 값 최대)

```python
{
    "brightness": 2,      # 최대
    "contrast": 2,        # 최대
    "saturation": 2,      # 최대
    "agc_gain": 30,       # 최대
    "gainceiling": 6,     # 최대 (128x)
    "aec_value": 2400,    # 최대 노출
    "aec2": 1,            # DSP 켜기
    "quality": 10,        # 고품질
    "denoise": 4,         # 노이즈 제거 중간값
}
```

## 주간 모드 설정

```python
{
    "brightness": 0,
    "contrast": 2,
    "saturation": 2,
    "agc_gain": 10,
    "gainceiling": 3,
    "aec_value": 100,
    "aec2": 1,
    "quality": 10,
    "denoise": 0,
}
```

## 아두이노 camera_init.h 확인사항

- brightness, contrast, saturation: sensor->set_brightness() 등으로 설정됨 ✅
- agc_gain: sensor->set_agc_gain(sensor, 30) ✅
- gainceiling: sensor->set_gainceiling(sensor, (gainceiling_t)6) ✅
- aec_value: sensor->set_aec_value(sensor, 2000) ✅
- aec2: sensor->set_aec2(sensor, 1) ✅
- **quality**: ❓ 코드에 없음 (테스트 필요)
- **denoise**: ❓ 코드에 없음 (테스트 필요)

## 다음 단계

1. 위 3개 섹션으로 UI 테스트
2. quality/denoise 작동 여부 확인
3. 작동 안 하면 config.py에서 제거
4. 모터 제어와 카메라 제어가 동시에 잘 작동하는지 확인

