import datetime
from service.weilai.task import start_task



start_task_list = [
    '13225269130-eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMzM3NTQ2MTczMTIyNjgyODgwIiwiZXhwIjoxNzUxNDMzNTYxfQ.jG4JSHUTWbUwiH7hxm2XKhgdrvk46Q664ULRKEFuWzU-123123-{"金宝":3,"法老":3,"探索未来":3,"魔礼寿":3,"魔礼红":3,"魔礼海":3,"魔礼青":3,"龙":3,"水宝":3,"炎宝":3,"双鱼瑟琳":3,"水瓶西尔":3,"金牛维塔":3,"貔貅":3,"白羊诺亚":3,"青鸾":3,"星海机甲":3,"蛇来运转":3}'
]


if __name__ == "__main__":
    start_task(start_task_list, 5)
