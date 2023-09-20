import asyncio
import logging
import sqlite3
from sqlite3 import Error
import atexit
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.middlewares import BaseMiddleware
import typing

# 从配置文件导入必要的设置
from config import BOT_TOKEN, BOT_USERNAME, CHANNEL_USERNAME, JOIN_CHANNEL_MESSAGE, SUPPORT_LINK, HELP_MESSAGE, EXCHANGE_SCORE, RESERVED_MESSAGE, LINK_BUTTONS_MESSAGE, LINK_BUTTON_1_TEXT, LINK_BUTTON_1_URL, LINK_BUTTON_2_TEXT, LINK_BUTTON_2_URL, CHANNEL_LINK

# 创建一个Logger对象
logger = logging.getLogger(__name__)

# 添加一个控制台处理器，将日志输出到控制台
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # 设置日志级别为DEBUG
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# 设置日志级别为DEBUG
logger.setLevel(logging.DEBUG)

# 创建异步函数来获取机器人的信息
async def get_bot_info():
    bot = Bot(token=BOT_TOKEN)
    bot_info = await bot.get_me()
    return bot_info

# 获取机器人信息，包括用户名
bot_info = asyncio.run(get_bot_info())
bot_username = bot_info.username
invite_links = {}

# 创建事件循环
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# 创建机器人实例
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# 自定义中间件以记录传入的消息
class LoggingMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        logger.info(f"接收到消息: {message.text}")

    async def on_post_process_message(self, message: types.Message, data: dict, response: typing.Any):
        logger.info(f"回复消息给用户: {message.text}")

dp.middleware.setup(LoggingMiddleware())

# 定义6个常驻选项
options = [
    "免费节点",
    "邀请好友",
    "兑换奖励",
    "查询积分",
    "联系客服",
    "帮助",
]

# 创建带有6个选项的自定义键盘
custom_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
custom_keyboard.add(*options)

# 创建字典用于存储用户信息、邀请关系和积分
user_data = {}
invite_links = {}  # 用于存储邀请链接

# 创建连接到SQLite数据库的函数，并添加错误处理
def create_database_connection():
    try:
        connection = sqlite3.connect('mydatabase.db')  # 替换为你的数据库文件名
        return connection
    except Error as e:
        logger.error(f"数据库连接错误: {e}")
        return None

# 创建用户积分表，并添加错误处理
def create_score_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_scores (
                user_id INTEGER PRIMARY KEY,
                score INTEGER DEFAULT 0
            )
        ''')
        connection.commit()
    except Error as e:
        logger.error(f"创建积分表时出错: {e}")

# 异步函数，检查用户是否是频道的成员，并添加错误处理
async def check_channel_membership(user_id):
    try:
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Error checking channel membership: {e}")
        return False

# 注册一个关闭机器人时保存积分数据的处理程序
def save_scores_on_exit():
    connection = create_database_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            for user_id, user_info in user_data.items():
                score = user_info.get("score", 0)
                cursor.execute("INSERT OR REPLACE INTO user_scores (user_id, score) VALUES (?, ?)", (user_id, score))
            connection.commit()
        except Error as e:
            logger.error(f"保存积分数据时出错: {e}")
        finally:
            connection.close()

# 创建一个定时保存数据的任务
async def save_data_periodically():
    while True:
        save_scores_on_exit()  # 定期保存积分数据
        await asyncio.sleep(300)  # 5分钟保存一次数据

# 启动定时保存数据的任务
async def start_data_saving_task():
    while True:
        try:
            await save_data_periodically()
        except Exception as e:
            logger.error(f"定时保存数据时出错: {e}")

# 创建带有6个选项的自定义键盘
custom_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
custom_keyboard.add(*options)

# 添加一个函数来提取邀请者的用户ID
def extract_inviter_user_id(invite_params):
    # 在这里编写从邀请参数中提取邀请者用户ID的逻辑
    # 例如，你可以检查 invite_params 中是否包含某种标识来提取用户ID
    # 如果无法提取，可以返回 None
    # 示例代码如下：

    if invite_params:
        # 假设邀请参数格式为 invite_user_id_12345
        parts = invite_params.split('_')
        if len(parts) == 3 and parts[0] == 'invite' and parts[1] == 'user' and parts[2].isdigit():
            return int(parts[2])  # 返回邀请者的用户ID

    return None  # 无法提取邀请者用户ID时返回 None

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """处理/start命令"""
    await message.answer(RESERVED_MESSAGE, reply_markup=custom_keyboard)
    user_id = message.from_user.id

    # 获取带有邀请参数的 /start 命令
    invite_params = message.get_args()

    # 检查用户是否已经在字典中，如果不在则添加
    if user_id not in user_data:
        user_data[user_id] = {"invited_by": None, "invited_friends": [], "score": 0}

    # 检查是否包含邀请参数
    if invite_params and invite_params.startswith("invite_"):
        inviter_id = int(invite_params.split("_")[1])
        # 记录邀请人
        user_data[user_id]["invited_by"] = inviter_id
        # 增加邀请人的积分
        if inviter_id in user_data:
            user_data[inviter_id]["invited_friends"].append(user_id)
            user_data[inviter_id]["score"] += 1

    # 继续处理邀请逻辑
    is_member = await check_channel_membership(user_id)

    if is_member:
        # 用户是频道成员，可以继续发送欢迎消息和邀请链接

        keyboard = types.InlineKeyboardMarkup()

        # 创建本机器人的邀请链接
        invite_link = f"https://t.me/{bot_username}?start=invite_{user_id}"

        # 存储本机器人的邀请链接
        invite_links[user_id] = invite_link

        # 创建链接按钮
        link_button_1 = types.InlineKeyboardButton(text=LINK_BUTTON_1_TEXT, url=LINK_BUTTON_1_URL)
        link_button_2 = types.InlineKeyboardButton(text=LINK_BUTTON_2_TEXT, url=LINK_BUTTON_2_URL)

        # 将链接按钮添加到键盘
        keyboard.add(link_button_1, link_button_2)

        # 发送欢迎消息和链接按钮
        await message.answer(LINK_BUTTONS_MESSAGE, reply_markup=keyboard)
    else:
        # 如果用户不是频道成员，发送提示消息和频道链接按钮

        # 创建频道加入按钮
        channel_button = types.InlineKeyboardButton(text="加入频道", url=CHANNEL_LINK)
        keyboard = types.InlineKeyboardMarkup().add(channel_button)

        await message.answer("请先加入我们的频道才能使用此机器人的功能。", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "免费节点")
async def handle_free_node(message: types.Message):
    """处理用户选择的免费节点选项"""
    user_id = message.from_user.id

    # 检查用户是否是频道成员
    is_member = await check_channel_membership(user_id)

    if not is_member:
        # 如果用户没有加入频道，发送提示消息和频道链接按钮

        # 创建频道加入按钮
        channel_button = types.InlineKeyboardButton(text="加入频道", url=CHANNEL_LINK)
        keyboard = types.InlineKeyboardMarkup().add(channel_button)

        await message.answer("请先加入我们的频道才能访问免费节点。", reply_markup=keyboard)
        return

    # 读取mf.txt文件内容
    with open('mf.txt', 'r', encoding='utf-8') as file:
        mf_content = file.read()

    # 发送mf.txt文件内容给用户
    await message.answer(mf_content)


@dp.message_handler(lambda message: message.text == "兑换奖励")
async def exchange_reward(message: types.Message):
    user_id = message.from_user.id

    # 用户数据字典中获取当前积分
    user_info = user_data.get(user_id)
    if user_info is None:
        await message.answer("抱歉，你没有足够的积分来兑换奖励。")
        return

    current_score = user_info.get("score", 0)

    # 检查用户积分是否足够兑换奖励
    if current_score >= EXCHANGE_SCORE:
        # 读取奖励列表
        with open('jl.txt', 'r', encoding='utf-8') as file:
            rewards = file.readlines()

        # 如果有可兑换的奖励
        if rewards:
            reward_to_exchange = rewards[0].strip()  # 获取第一个奖励，并移除两端空白字符

            # 删除已经兑换的奖励
            rewards.pop(0)

            # 更新用户积分
            new_score = current_score - EXCHANGE_SCORE
            user_info["score"] = new_score

            # 更新奖励列表到文件
            with open('jl.txt', 'w', encoding='utf-8') as file:
                file.writelines(rewards)

            # 发送兑换的奖励给用户（在更新积分之后），包含所需积分信息
            await message.answer(f"恭喜！你成功兑换了奖励：{reward_to_exchange}，消耗了 {EXCHANGE_SCORE} 积分。")
        else:
            await message.answer("抱歉，没有可用的奖励.")
    else:
        await message.answer(f"抱歉，你没有足够的积分来兑换奖励。所需积分为 {EXCHANGE_SCORE}。")
        
# 处理邀请好友选项，发送邀请链接给用户
@dp.message_handler(lambda message: message.text == "邀请好友")
async def invite_friends(message: types.Message):
    user_id = message.from_user.id

    # 获取用户的本机器人的邀请链接
    if user_id in invite_links:
        invite_link = invite_links[user_id]
        await message.answer(f"分享以下本机器人的邀请链接给你的好友：{invite_link}")

        # 增加邀请者的积分
        inviter_user_id = user_data[user_id]["invited_by"]

        if inviter_user_id is not None:
            if inviter_user_id in user_data:
                user_data[inviter_user_id]["score"] += 1

        # 获取用户的当前积分并发送积分信息
        if user_id in user_data:
            score = user_data[user_id]["score"]
            await message.answer(f"你的当前积分为: {score}")

@dp.message_handler(lambda message: message.text == "查询积分")
async def check_score(message: types.Message):
    """处理用户选择的查询积分选项"""
    user_id = message.from_user.id

    # 获取用户的当前积分
    if user_id in user_data:
        score = user_data[user_id]["score"]
        await message.answer(f"你的当前积分为: {score}")
        
@dp.message_handler(lambda message: message.text == "联系客服")
async def contact_support(message: types.Message):
    """处理用户选择的联系客服选项"""
    support_link = SUPPORT_LINK  # 从配置文件中获取客服链接

    # 创建包含客服链接的内联键盘按钮
    support_button = types.InlineKeyboardButton(text="联系客服", url=support_link)
    keyboard = types.InlineKeyboardMarkup().add(support_button)

    # 发送包含客服链接的消息
    await message.answer("点击下面的链接联系客服:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "帮助")
async def help(message: types.Message):
    """处理用户选择的帮助选项"""
    # 从配置文件中获取帮助消息内容
    help_message = HELP_MESSAGE

    # 发送帮助消息给用户
    await message.answer(help_message)

if __name__ == '__main__':
    # 启动定时保存数据的任务
    loop.create_task(start_data_saving_task())

    # 启动机器人
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True, loop=loop)
