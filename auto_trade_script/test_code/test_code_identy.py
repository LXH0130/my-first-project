import pyautogui
from PIL import Image
import pytesseract
import time
import threading

# 全局变量
monitoring = False


def simple_capture_and_recognize(x, y, width, height):
    """简化版本的验证码识别"""
    try:
        # 截图
        screenshot = pyautogui.screenshot(region=(x, y, width, height))

        # 直接识别（不进行复杂预处理）
        custom_config = r'--oem 3 --psm 8'
        text = pytesseract.image_to_string(screenshot, config=custom_config)

        # 清理结果
        text = ''.join(filter(str.isalnum, text))

        return text, screenshot, True if text else False

    except Exception as e:
        print(f"识别过程中出错: {e}")
        return None, None, False


def real_time_monitor(x, y, width, height, interval=3):
    """实时监测验证码 - 重复验证码不处理"""
    global monitoring

    print(f"开始实时监测，每 {interval} 秒检查一次...")
    print("监测规则: 只处理新验证码，重复验证码不处理")
    print("按 Ctrl+C 停止监测")

    last_captcha = None
    check_count = 0

    try:
        while monitoring:
            check_count += 1
            print(f"\n第 {check_count} 次检查 - {time.strftime('%H:%M:%S')}")

            # 识别验证码
            text, screenshot, success = simple_capture_and_recognize(x, y, width, height)

            if success:
                if text != last_captcha:
                    print(f"✅ 发现新验证码: {text}")
                    print("正在自动输入...")

                    # 点击输入框
                    pyautogui.click(808, 400)
                    time.sleep(0.2)

                    # 输入识别结果
                    pyautogui.write(text, interval=0.05)

                    # 按Enter确认（可选）
                    time.sleep(0.5)
                    pyautogui.press('enter')

                    print(f"✅ 验证码 {text} 已输入完成")
                    last_captcha = text
                else:
                    print(f"⏳ 验证码未变化: {text} (跳过处理)")
            else:
                print("❌ 未检测到验证码")

            # 等待
            for i in range(interval):
                if not monitoring:
                    break
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n监测被用户中断")
    except Exception as e:
        print(f"监测出错: {e}")


def start_monitoring(x, y, width, height, interval=3):
    """开始监测"""
    global monitoring

    if monitoring:
        print("监测已经在运行中")
        return

    monitoring = True
    monitor_thread = threading.Thread(
        target=real_time_monitor,
        args=(x, y, width, height, interval)
    )
    monitor_thread.daemon = True
    monitor_thread.start()
    print("监测已启动")


def stop_monitoring():
    """停止监测"""
    global monitoring
    monitoring = False
    print("监测已停止")


def single_detection(x, y, width, height):
    """单次检测"""
    print("执行单次检测...")
    result, image, success = simple_capture_and_recognize(x, y, width, height)
    if success:
        print(f"识别结果: {result}")

        # 自动输入
        pyautogui.click(808, 400)
        time.sleep(0.2)
        pyautogui.write(result, interval=0.05)
        time.sleep(0.5)
        pyautogui.press('enter')
        print(f"验证码 {result} 已输入")
    else:
        print("未识别到验证码")
    return result, image, success


# 使用示例
if __name__ == "__main__":
    # 验证码区域坐标
    x, y, width, height = 880, 390, 100, 30

    print("=" * 50)
    print("验证码实时监测系统")
    print("=" * 50)
    print("功能说明:")
    print("- 自动监测验证码区域")
    print("- 只处理新出现的验证码")
    print("- 重复验证码自动跳过")
    print("- 按 Ctrl+C 停止程序")
    print("=" * 50)

    try:
        # 选择模式
        print("请选择模式:")
        print("1 - 单次检测")
        print("2 - 开始实时监测")
        print("3 - 退出")

        choice = input("请输入选择 (1/2/3): ").strip()

        if choice == "1":
            # 单次检测
            single_detection(x, y, width, height)

        elif choice == "2":
            # 实时监测
            interval = input("请输入检查间隔(秒，默认3秒): ").strip()
            try:
                interval = int(interval) if interval else 3
            except:
                interval = 3

            print(f"检查间隔设置为: {interval}秒")
            print("5秒后开始监测...")
            time.sleep(5)

            start_monitoring(x, y, width, height, interval)

            # 保持主线程运行
            try:
                while monitoring:
                    time.sleep(1)
            except KeyboardInterrupt:
                stop_monitoring()

        else:
            print("退出程序")

    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")
    finally:
        # 清理资源
        stop_monitoring()
        print("程序结束")