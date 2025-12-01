from pynput import mouse

def on_click(x, y, button, pressed):
    if pressed:
        print(f'鼠标 {button} 在位置 ({x}, {y}) 按下')
    else:
        print(f'鼠标 {button} 在位置 ({x}, {y}) 释放')

# 创建监听器
listener = mouse.Listener(on_click=on_click)

# 启动监听器
listener.start()

# 等待监听器结束（阻塞当前线程）
listener.join()
print("监听器已停止")