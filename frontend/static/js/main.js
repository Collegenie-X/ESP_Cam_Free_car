// ==================== 전역 변수 ====================
let statusUpdateInterval = null;
let imageCaptureInterval = null;
let lastFpsTime = Date.now();
let frameCount = 0;

// 이미지 캡처 주기 (밀리초) - ESP32 부하 고려
const IMAGE_CAPTURE_INTERVAL = 100; // 100ms = 약 10 FPS

// ==================== 초기화 ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('ESP32-CAM 모니터링 시스템 시작');
    
    // 상태 업데이트 시작 (1초마다)
    startStatusUpdate();
    
    // 이미지 캡처 시작 (주기적으로 /capture 호출)
    startImageCapture();
    
    // FPS 카운터 시작
    startFpsCounter();
    
    // 초기 로그
    addLog('시스템 초기화 완료 (폴링 모드)', 'success');
});

// ==================== 상태 업데이트 ====================
function startStatusUpdate() {
    // 즉시 실행
    updateStatus();
    
    // 1초마다 반복
    statusUpdateInterval = setInterval(updateStatus, 1000);
}

async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.error) {
            updateConnectionStatus(false);
            addLog('ESP32-CAM 연결 실패: ' + data.error, 'error');
            return;
        }
        
        // 연결 상태 업데이트
        updateConnectionStatus(true);
        
        // 상태 정보 업데이트
        document.getElementById('ip-address').textContent = data.ip_address || '-';
        document.getElementById('motor-status').textContent = 
            data.motor_status === 'running' ? '🟢 동작 중' : '🔴 정지';
        document.getElementById('current-command').textContent = data.current_command || '-';
        const ledIsOn = data.led_state === 'on';
        document.getElementById('led-status').textContent = 
            ledIsOn ? '💡 켜짐' : '🌑 꺼짐';
        
        // LED 토글 스위치 UI 업데이트
        updateLEDToggleUI(ledIsOn);
        
        document.getElementById('speed-value').textContent = data.speed || '-';
        document.getElementById('speed-display').textContent = data.speed || '--';
        
        // 카메라 설정 업데이트
        if (data.camera_settings) {
            document.getElementById('brightness-value').textContent = 
                data.camera_settings.brightness || '-';
            
            // 슬라이더 값 동기화 (사용자가 조작중이 아닐 때만)
            const brightnessSlider = document.getElementById('brightness-slider');
            if (!brightnessSlider.matches(':active')) {
                brightnessSlider.value = data.camera_settings.brightness || 0;
                document.getElementById('brightness-display').textContent = 
                    data.camera_settings.brightness || 0;
            }
            
            const contrastSlider = document.getElementById('contrast-slider');
            if (!contrastSlider.matches(':active')) {
                contrastSlider.value = data.camera_settings.contrast || 0;
                document.getElementById('contrast-display').textContent = 
                    data.camera_settings.contrast || 0;
            }
            
            const agcSlider = document.getElementById('agc-slider');
            if (!agcSlider.matches(':active')) {
                agcSlider.value = data.camera_settings.agc_gain || 0;
                document.getElementById('agc-display').textContent = 
                    data.camera_settings.agc_gain || 0;
            }
        }
        
    } catch (error) {
        console.error('상태 업데이트 실패:', error);
        updateConnectionStatus(false);
    }
}

function updateConnectionStatus(connected) {
    const indicator = document.getElementById('connection-indicator');
    const text = document.getElementById('connection-text');
    
    if (connected) {
        indicator.className = 'indicator connected';
        text.textContent = '연결됨';
    } else {
        indicator.className = 'indicator disconnected';
        text.textContent = '연결 끊김';
    }
}

function updateLEDToggleUI(isOn) {
    const toggle = document.getElementById('led-toggle');
    const statusText = document.getElementById('led-toggle-status');
    
    if (toggle && statusText) {
        toggle.checked = isOn;
        statusText.textContent = isOn ? 'ON' : 'OFF';
        statusText.style.color = isOn ? 'var(--success-color)' : 'var(--text-color)';
    }
}

// ==================== 이미지 캡처 (폴링 방식) ====================
function startImageCapture() {
    // 첫 이미지 즉시 로드
    captureImage();
    
    // 주기적으로 이미지 캡처
    imageCaptureInterval = setInterval(captureImage, IMAGE_CAPTURE_INTERVAL);
}

function captureImage() {
    const img = document.getElementById('camera-stream');
    const overlay = document.getElementById('stream-overlay');
    
    // 캐시 방지를 위한 타임스탬프 추가
    const timestamp = new Date().getTime();
    img.src = `/capture?t=${timestamp}`;
    
    // 이미지 로드 성공 시
    img.onload = function() {
        frameCount++;
        if (overlay) {
            overlay.classList.add('hidden');
        }
    };
    
    // 이미지 로드 실패 시
    img.onerror = function() {
        if (overlay) {
            overlay.classList.remove('hidden');
            overlay.innerHTML = '<p>⚠️ 카메라 연결 실패</p>';
        }
    };
}

function handleStreamError() {
    const overlay = document.getElementById('stream-overlay');
    if (overlay) {
        overlay.classList.remove('hidden');
        overlay.innerHTML = '<p>⚠️ 카메라 연결 실패</p>';
    }
}

// ==================== FPS 카운터 ====================
function startFpsCounter() {
    setInterval(() => {
        const now = Date.now();
        const elapsed = (now - lastFpsTime) / 1000;
        const fps = Math.round(frameCount / elapsed);
        
        document.getElementById('fps-counter').textContent = `FPS: ${fps}`;
        
        frameCount = 0;
        lastFpsTime = now;
    }, 1000);
}

// ==================== 모터 제어 ====================
async function sendControl(command) {
    try {
        const response = await fetch(`/api/control/${command}`);
        const data = await response.json();
        
        if (data.success) {
            addLog(`모터 제어: ${command}`, 'success');
        } else {
            addLog(`모터 제어 실패: ${command}`, 'error');
        }
    } catch (error) {
        console.error('모터 제어 오류:', error);
        addLog('모터 제어 오류: ' + error.message, 'error');
    }
}

// ==================== 속도 제어 ====================
async function sendSpeed(operation, step) {
    try {
        const response = await fetch(`/api/speed/${operation}?step=${step}`);
        const data = await response.json();
        
        if (data.success) {
            addLog(`속도 ${operation === 'plus' ? '증가' : '감소'}: ${step}`, 'success');
            // 즉시 상태 업데이트
            setTimeout(updateStatus, 100);
        } else {
            addLog(`속도 제어 실패`, 'error');
        }
    } catch (error) {
        console.error('속도 제어 오류:', error);
        addLog('속도 제어 오류: ' + error.message, 'error');
    }
}

// ==================== LED 제어 ====================
async function sendLED(state) {
    try {
        const response = await fetch(`/api/led/${state}`);
        const data = await response.json();
        
        if (data.success) {
            addLog(`LED ${state}`, 'success');
            // 즉시 상태 업데이트
            setTimeout(updateStatus, 100);
        } else {
            addLog(`LED 제어 실패`, 'error');
        }
    } catch (error) {
        console.error('LED 제어 오류:', error);
        addLog('LED 제어 오류: ' + error.message, 'error');
    }
}

// LED 토글 스위치 핸들러
async function toggleLED() {
    const toggle = document.getElementById('led-toggle');
    const isOn = toggle.checked;
    const state = isOn ? 'on' : 'off';
    
    try {
        const response = await fetch(`/api/led/${state}`);
        const data = await response.json();
        
        if (data.success) {
            addLog(`LED ${state}`, 'success');
            updateLEDToggleUI(isOn);
            // 즉시 상태 업데이트
            setTimeout(updateStatus, 100);
        } else {
            addLog(`LED 제어 실패`, 'error');
            // 실패 시 토글 원래대로
            toggle.checked = !isOn;
        }
    } catch (error) {
        console.error('LED 제어 오류:', error);
        addLog('LED 제어 오류: ' + error.message, 'error');
        // 실패 시 토글 원래대로
        toggle.checked = !isOn;
    }
}

// ==================== 카메라 설정 ====================
let cameraUpdateTimeout = null;

function updateCamera(param, value) {
    // 슬라이더 값 표시 업데이트
    const displayId = param === 'agc_gain' ? 'agc-display' : `${param}-display`;
    document.getElementById(displayId).textContent = value;
    
    // 디바운싱: 마지막 변경 후 300ms 후에 전송
    clearTimeout(cameraUpdateTimeout);
    cameraUpdateTimeout = setTimeout(async () => {
        try {
            // 정수 변환 (슬라이더에서 문자열이 전달될 수 있음)
            const normalizedValue = parseInt(value, 10);
            const response = await fetch(`/api/camera/${param}?value=${normalizedValue}`);
            const data = await response.json();

            if (response.status === 501) {
                // 아두이노 미지원 파라미터: 슬라이더 비활성화 및 안내
                const sliderId = getSliderIdForParam(param);
                const slider = document.getElementById(sliderId);
                if (slider) {
                    slider.disabled = true;
                }
                addLog(`미지원 파라미터: ${param} (아두이노)`, 'error');
                return;
            }
            
            if (data.success) {
                addLog(`카메라 ${param}: ${normalizedValue}`, 'success');
            } else {
                addLog(`카메라 설정 실패`, 'error');
            }
        } catch (error) {
            console.error('카메라 설정 오류:', error);
            addLog('카메라 설정 오류: ' + error.message, 'error');
        }
    }, 300);
}

async function resetCamera() {
    // 기본값으로 리셋 (아두이노 초기값 기반)
    const defaults = {
        brightness: 2,
        contrast: 2,
        saturation: 1,
        agc_gain: 30,
        gainceiling: 6,
        aec_value: 2000,
        aec2: 1,
        quality: 10,
        denoise: 0,
    };
    
    await applyCameraSettings(defaults, '카메라 설정 리셋 완료');
}

// 야간 모드 설정 (모든 설정 최대치)
async function applyNightMode() {
    const nightSettings = {
        brightness: 2,      // 최대
        contrast: 2,        // 최대
        saturation: 2,      // 최대
        agc_gain: 30,       // 최대
        gainceiling: 6,     // 최대 (128x)
        aec_value: 2400,    // 최대 노출
        aec2: 1,            // DSP 켜기
        quality: 10,        // 고품질
        denoise: 4,         // 노이즈 제거 중간값
    };
    
    await applyCameraSettings(nightSettings, '야간 모드 적용 완료 🌙 (모든 설정 최대)');
}

// 주간 모드 설정 (밝은 환경)
async function applyDayMode() {
    const daySettings = {
        brightness: 0,
        contrast: 2,
        saturation: 2,
        agc_gain: 10,
        gainceiling: 3,
        aec_value: 100,
        aec2: 1,
        quality: 10,
        denoise: 0,
    };
    
    await applyCameraSettings(daySettings, '주간 모드 적용 완료 ☀️');
}

// 카메라 설정 일괄 적용
async function applyCameraSettings(settings, logMessage) {
    for (const [param, value] of Object.entries(settings)) {
        try {
            await fetch(`/api/camera/${param}?value=${value}`);
            
            // 슬라이더 업데이트
            const sliderId = getSliderIdForParam(param);
            const displayId = getDisplayIdForParam(param);
            
            const slider = document.getElementById(sliderId);
            const display = document.getElementById(displayId);
            
            if (slider) slider.value = value;
            if (display) display.textContent = value;
            
        } catch (error) {
            console.error(`${param} 설정 실패:`, error);
        }
    }
    
    addLog(logMessage, 'success');
}

// 파라미터에 따른 슬라이더 ID 반환
function getSliderIdForParam(param) {
    const idMap = {
        'agc_gain': 'agc-slider',
        'aec_value': 'aec-slider',
        'gainceiling': 'gainceiling-slider',
        'aec2': 'aec2-slider',
    };
    return idMap[param] || `${param}-slider`;
}

// 파라미터에 따른 디스플레이 ID 반환
function getDisplayIdForParam(param) {
    const idMap = {
        'agc_gain': 'agc-display',
        'aec_value': 'aec-display',
        'gainceiling': 'gainceiling-display',
        'aec2': 'aec2-display',
    };
    return idMap[param] || `${param}-display`;
}

// ==================== 로그 시스템 ====================
function addLog(message, type = 'info') {
    const logContainer = document.getElementById('log-container');
    const timestamp = new Date().toLocaleTimeString('ko-KR');
    
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    logEntry.innerHTML = `<span class="timestamp">[${timestamp}]</span> ${message}`;
    
    // 최신 로그를 위에 추가
    logContainer.insertBefore(logEntry, logContainer.firstChild);
    
    // 최대 50개 로그 유지
    while (logContainer.children.length > 50) {
        logContainer.removeChild(logContainer.lastChild);
    }
}

function clearLog() {
    const logContainer = document.getElementById('log-container');
    logContainer.innerHTML = '';
    addLog('로그 초기화', 'info');
}

// ==================== 키보드 제어 (선택사항) ====================
document.addEventListener('keydown', function(event) {
    // 입력 필드에 포커스가 있으면 무시
    if (event.target.tagName === 'INPUT') return;
    
    switch(event.key) {
        case 'ArrowUp':
        case 'w':
        case 'W':
            sendControl('center');
            event.preventDefault();
            break;
        case 'ArrowLeft':
        case 'a':
        case 'A':
            sendControl('left');
            event.preventDefault();
            break;
        case 'ArrowRight':
        case 'd':
        case 'D':
            sendControl('right');
            event.preventDefault();
            break;
        case ' ':
        case 's':
        case 'S':
            sendControl('stop');
            event.preventDefault();
            break;
        case '+':
        case '=':
            sendSpeed('plus', 10);
            event.preventDefault();
            break;
        case '-':
        case '_':
            sendSpeed('minus', 10);
            event.preventDefault();
            break;
        case 'l':
        case 'L':
            sendLED('toggle');
            event.preventDefault();
            break;
    }
});

document.addEventListener('keyup', function(event) {
    // 입력 필드에 포커스가 있으면 무시
    if (event.target.tagName === 'INPUT') return;
    
    // 방향키나 WASD를 놓으면 정지
    if (['ArrowUp', 'ArrowLeft', 'ArrowRight', 'w', 'W', 'a', 'A', 'd', 'D'].includes(event.key)) {
        sendControl('stop');
    }
});

// ==================== 페이지 언로드 시 정리 ====================
window.addEventListener('beforeunload', function() {
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval);
    }
    if (imageCaptureInterval) {
        clearInterval(imageCaptureInterval);
    }
    // 정지 명령 전송
    sendControl('stop');
});



