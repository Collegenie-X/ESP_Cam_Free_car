#!/usr/bin/env python3
"""
ESP32-CAM /capture 엔드포인트 테스트 스크립트

사용법:
    python test_esp32_capture.py
"""

import requests
import time
import sys
import config


def print_header(text):
    """헤더 출력"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def test_ping(ip):
    """
    ESP32-CAM 기본 연결 테스트
    """
    print(f"\n🔍 1. ESP32-CAM 연결 테스트 ({ip})")
    print("-" * 60)
    
    try:
        url = f"http://{ip}/status"
        print(f"요청: {url}")
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print("✅ 성공: ESP32-CAM 연결됨")
            try:
                data = response.json()
                print(f"응답 데이터: {data}")
            except:
                print(f"응답 텍스트: {response.text}")
            return True
        else:
            print(f"❌ 실패: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 실패: 연결 시간 초과 (5초)")
        print("   → ESP32-CAM이 켜져 있는지 확인하세요")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 실패: 연결 거부됨")
        print(f"   → IP 주소가 올바른지 확인하세요: {ip}")
        print("   → ESP32-CAM과 같은 네트워크에 연결되어 있는지 확인하세요")
        return False
    except Exception as e:
        print(f"❌ 실패: {e}")
        return False


def test_capture(ip, num_frames=5):
    """
    /capture 엔드포인트 테스트 (연속 캡처)
    """
    print(f"\n📸 2. /capture 엔드포인트 테스트 ({num_frames}프레임)")
    print("-" * 60)
    
    url = f"http://{ip}/capture"
    print(f"URL: {url}")
    
    success_count = 0
    total_time = 0
    total_size = 0
    
    for i in range(num_frames):
        try:
            start_time = time.time()
            response = requests.get(url, timeout=5)
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                image_size = len(response.content)
                total_size += image_size
                total_time += elapsed_time
                success_count += 1
                
                print(f"  [{i+1}/{num_frames}] ✅ 성공 - "
                      f"크기: {image_size/1024:.1f} KB, "
                      f"시간: {elapsed_time*1000:.0f} ms")
            else:
                print(f"  [{i+1}/{num_frames}] ❌ 실패 - HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  [{i+1}/{num_frames}] ❌ 오류 - {e}")
        
        # 프레임 간 대기 (200ms = 5fps)
        if i < num_frames - 1:
            time.sleep(0.2)
    
    print("\n📊 결과:")
    print(f"  성공률: {success_count}/{num_frames} ({success_count/num_frames*100:.1f}%)")
    
    if success_count > 0:
        avg_time = total_time / success_count
        avg_size = total_size / success_count
        fps = 1.0 / avg_time if avg_time > 0 else 0
        
        print(f"  평균 응답 시간: {avg_time*1000:.0f} ms")
        print(f"  평균 이미지 크기: {avg_size/1024:.1f} KB")
        print(f"  예상 FPS: {fps:.1f} fps")
        
        # 권장 사항
        if avg_time > 0.5:
            print("\n⚠️  경고: 응답 시간이 느립니다 (500ms 이상)")
            print("   → WiFi 신호를 확인하세요")
        elif avg_time > 0.2:
            print("\n💡 팁: 응답 시간이 약간 느립니다")
            print("   → 5fps 이하로 설정하는 것을 권장합니다")
        else:
            print("\n✅ 좋음: 응답 시간이 빠릅니다")
            print("   → 10fps까지 가능할 수 있습니다")
    
    return success_count == num_frames


def test_control(ip):
    """
    /control 엔드포인트 테스트
    """
    print(f"\n🎮 3. /control 엔드포인트 테스트")
    print("-" * 60)
    
    commands = ["center", "left", "right", "stop"]
    success_count = 0
    
    for cmd in commands:
        try:
            url = f"http://{ip}/control"
            params = {"cmd": cmd}
            print(f"  명령: {cmd} → {url}?cmd={cmd}")
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                print(f"    ✅ 성공 - {response.text.strip()}")
                success_count += 1
            else:
                print(f"    ❌ 실패 - HTTP {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ 오류 - {e}")
        
        time.sleep(0.5)  # 명령 간 대기
    
    print(f"\n📊 결과: {success_count}/{len(commands)} 명령 성공")
    return success_count == len(commands)


def save_test_image(ip):
    """
    테스트 이미지 저장
    """
    print(f"\n💾 4. 테스트 이미지 저장")
    print("-" * 60)
    
    try:
        url = f"http://{ip}/capture"
        print(f"이미지 가져오는 중: {url}")
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            filename = "test_capture.jpg"
            with open(filename, "wb") as f:
                f.write(response.content)
            
            print(f"✅ 이미지 저장 완료: {filename}")
            print(f"   크기: {len(response.content)/1024:.1f} KB")
            return True
        else:
            print(f"❌ 실패: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False


def main():
    """메인 함수"""
    print_header("🚗 ESP32-CAM /capture 엔드포인트 테스트")
    
    # ESP32 IP 설정
    esp32_ip = config.DEFAULT_ESP32_IP
    print(f"\nESP32-CAM IP: {esp32_ip}")
    print("(config.py에서 변경 가능)")
    
    # 사용자 확인
    response = input("\n계속 진행하시겠습니까? (y/N): ")
    if response.lower() != 'y':
        print("테스트 취소됨")
        sys.exit(0)
    
    # 테스트 실행
    results = {
        "ping": False,
        "capture": False,
        "control": False,
        "save": False
    }
    
    results["ping"] = test_ping(esp32_ip)
    
    if results["ping"]:
        results["capture"] = test_capture(esp32_ip, num_frames=5)
        results["control"] = test_control(esp32_ip)
        results["save"] = save_test_image(esp32_ip)
    else:
        print("\n⚠️  기본 연결 테스트 실패. 나머지 테스트를 건너뜁니다.")
    
    # 최종 결과
    print_header("📋 테스트 결과 요약")
    
    test_names = {
        "ping": "1. ESP32-CAM 연결",
        "capture": "2. /capture 엔드포인트",
        "control": "3. /control 엔드포인트",
        "save": "4. 이미지 저장"
    }
    
    for key, name in test_names.items():
        status = "✅ 성공" if results[key] else "❌ 실패"
        print(f"{name}: {status}")
    
    success_rate = sum(results.values()) / len(results) * 100
    print(f"\n전체 성공률: {success_rate:.1f}%")
    
    # 권장 사항
    if success_rate == 100:
        print("\n🎉 모든 테스트 통과!")
        print("자율주행 시스템을 시작할 수 있습니다:")
        print("  python app.py")
        print("\n웹 브라우저에서 접속:")
        print("  http://localhost:5000/autonomous")
    elif results["ping"] and results["capture"]:
        print("\n⚠️  기본 기능은 동작합니다.")
        print("일부 고급 기능에 문제가 있을 수 있습니다.")
        print("\n자율주행 시스템을 시도해볼 수 있습니다:")
        print("  python app.py")
    else:
        print("\n❌ 중요한 테스트가 실패했습니다.")
        print("\n문제 해결:")
        print("  1. ESP32-CAM 전원 확인")
        print("  2. WiFi 연결 확인")
        print(f"  3. IP 주소 확인: {esp32_ip}")
        print("  4. 브라우저에서 직접 테스트:")
        print(f"     http://{esp32_ip}/capture")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n테스트 중단됨")
        sys.exit(0)

