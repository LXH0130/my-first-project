#同花顺版本
import sys
import socket
import struct
import json
import threading, time, datetime
import pytesseract
import pyautogui
import re
import logging
import pyperclip

pyautogui.FAILSAFE=False
logging.basicConfig(filename='gp.log',level=logging.INFO)

#基本参数初始化
tt = 0.5        #输入间隔
price_flag = 0  #是否需要输入价格

# 基本按钮坐标初始化
x_buy, y_buy = 50 , 93
x_sell, y_sell = 50 , 130

x_code, y_code = 334, 137
x_price, y_price = 321, 188
x_count, y_count = 312, 278
x_trade, y_trade = 334, 306

#截图坐标初始化
x_code_cap, y_code_cap = 284, 125
width, height = 100, 20

# 识别指定图片的字符串
def simple_capture_and_recognize(x, y, width, height):
    try:
        # 截图
        screenshot = pyautogui.screenshot(region=(x, y, width, height))

        # 直接识别（不进行复杂预处理）
        custom_config = r'--oem 3 --psm 8'
        text = pytesseract.image_to_string(screenshot, config=custom_config)

        text = re.sub(r'\D', '', text)
        # 清理结果
        text = ''.join(filter(str.isalnum, text))

        return text

    except Exception as e:
        print(f"识别过程中出错: {e}")
        return None, None, False

def clear():
    pyautogui.doubleClick(x=x_code, y=y_code, button="left") #双击选中
    pyautogui.press('del')
    time.sleep(tt)
    
def judge():
    pyautogui.doubleClick(x=x_code, y=y_code, button="left") #双击选中
    pyautogui.hotkey('ctrl', 'c')
    content=pyperclip.paste()
    if len(content)!=6:
        logging.error('import code is error, code len is %d, please import again.', len(content))
        return False
    return content
    
def auto_buy(stock_code,price, amount):
    clear()
    # 点击买入
    pyautogui.click(x=x_buy, y=y_buy) #点击买入
    time.sleep(tt)    
    pyautogui.click(x=x_code, y=y_code) #点击证券代码
    time.sleep(tt)
    # 输入股票代码
    pyautogui.typewrite(stock_code)
    time.sleep(tt)

    pyautogui.click(x=x_code, y=y_code)  # 点击证券代码
    time.sleep(tt)

    #检测代码是否输入错误
    while True:
        ident_result = simple_capture_and_recognize(x_code_cap, y_code_cap, width, height)
        if len(ident_result) == 6:  # 对比代码显示正确
            break
        else:
            logging.info('identy code is %s, len is not 6.', ident_result,)
            pyautogui.typewrite(stock_code)
            time.sleep(tt)
    
    pyautogui.press('enter')
    time.sleep(tt)
    if price_flag:
        #输入价格
        pyautogui.press('backspace')
        pyautogui.press('backspace')
        pyautogui.press('backspace')
        pyautogui.press('backspace')
        pyautogui.press('backspace')
        pyautogui.press('backspace')
        pyautogui.press('backspace')
        pyautogui.typewrite(str(price))
        time.sleep(tt)
    
    pyautogui.press('enter')
    time.sleep(tt)
    # 输入买入数量
    pyautogui.typewrite(str(amount))
    time.sleep(tt)
    # 确认买入
    pyautogui.click(x=x_trade, y=y_trade)
    time.sleep(tt)
    pyautogui.click(x=900, y=617)
    time.sleep(tt)
    pyautogui.click(x=910, y=600)

def auto_sell(stock_code,price, amount):
    clear()
    #  点击卖出
    pyautogui.click(x=x_sell, y=y_sell)
    time.sleep(tt)
    pyautogui.click(x=x_code, y=y_code) #点击证券代码
    time.sleep(tt)
    # 输入股票代码
    pyautogui.typewrite(stock_code)
    time.sleep(tt)

    pyautogui.click(x=x_code, y=y_code)  # 点击证券代码
    time.sleep(tt)

    # 检测代码是否输入错误
    while True:
        ident_result = simple_capture_and_recognize(x_code_cap, y_code_cap, width, height)
        if len(ident_result) == 6:  # 对比代码显示正确
            break
        else:
            logging.info('identy code is %s, len is not 6.', ident_result, )
            pyautogui.typewrite(stock_code)
            time.sleep(tt)
    
    pyautogui.press('enter')
    time.sleep(tt)
    if price_flag:
        #输入价格
        pyautogui.press('backspace')
        pyautogui.press('backspace')
        pyautogui.press('backspace')
        pyautogui.press('backspace')
        pyautogui.press('backspace')
        pyautogui.press('backspace')
        pyautogui.press('backspace')
        pyautogui.typewrite(str(price))
        time.sleep(tt)
    
    pyautogui.press('enter')
    time.sleep(tt)
    # 输入卖出数量
    pyautogui.typewrite(str(amount))
    time.sleep(tt)
    # 确认买入
    pyautogui.click(x=x_trade, y=y_trade)
    time.sleep(tt)
    pyautogui.click(x=900, y=617)
    time.sleep(tt)
    pyautogui.click(x=910, y=600)
    
def handle_gp(args):
    #print(args)
    
    #return
    try:
        s = args[0]
        dict = json.loads(s)
        dict = dict[0]
        print(dict)

        ss = dict
        token = ss['token']
        #print(token)
        
        if ss:
            #print(ss['action'])
            
            if ss['action'] == 'buy':
                if token == 123:
                    stock = ss['zqdm'][:6]
                    num = ss['qty']
                    strategy = ss['strategy']
                    trade_time = ss['trade_time']
                    now_time = ss['time']
                    price = ss['price']

                    logging.info(f'%s %s %s %s %s %s %s' % (stock, num, 'buy', price, trade_time, strategy, now_time))
                    auto_buy(stock,price, num)
            elif ss['action'] == 'sell':
                if token == 123:
                    stock = ss['zqdm'][:6]
                    num = ss['qty']
                    strategy = ss['strategy']
                    trade_time = ss['trade_time']
                    now_time = ss['time']
                    price = ss['price']
                    
                    logging.info(f'%s %s %s %s %s %s %s' % (stock, num, 'sell', price, trade_time, strategy, now_time))
                    auto_sell(stock,price, num)
            
        #     print("recv params:")
        #     for i, arg in enumerate(args, 1):
        #         print(f"params {i}: {arg}")
    except Exception as e:
        print('error')
        print(e)
    
#获取当前时间
def get_now():
    from datetime import datetime
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_datetime

def main():
    # sys.argv[0] 是脚本名称
    # sys.argv[1:] 是传递的参数
    args = sys.argv[1:]
    
    if not args:
        print("Usage: python script.py [arg1] [arg2] ...")
        return
    #do it
    handle_gp(args)

if __name__ == "__main__":
    main()