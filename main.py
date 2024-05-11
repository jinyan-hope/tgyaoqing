import sqlite3
import yaml
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.types import Message
from config import *


# 设置日志记录配置
logging.basicConfig(level=logging.INFO)

# 创建一个日志记录器
logger = logging.getLogger(__name__)

# 初始化机器人和调度器
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
channel_members_cache = {}
user_data = {}


def create_tables():
    # 连接到数据库文件
    conn = sqlite3.connect(db_filename)

    # 创建游标对象，用于执行SQL命令
    cursor = conn.cursor()

    # 创建名为"users"的表，如果该表不存在
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,  -- 用户ID，主键
            chat_id INTEGER,              -- 聊天ID
            invite_link TEXT,             -- 邀请链接
            invited_by INTEGER,           -- 邀请者
            score INTEGER                 -- 分数
        )
    ''')

    # 关闭游标
    cursor.close()

    # 提交更改到数据库
    conn.commit()

    # 关闭数据库连接
    conn.close()


def create_invite_links_table():
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invite_links (
            user_id INTEGER PRIMARY KEY,
            link TEXT
        )
    ''')
    cursor.close()
    conn.commit()
    conn.close()

# 保存邀请人ID为 inviting_chat_id
def save_inviting_user_id(user_id, inviting_chat_id):
    try:
        conn = sqlite3.connect(db_filename)  # 连接到数据库
        cursor = conn.cursor()

        # 创建 users 表格，如果不存在
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,  -- 用户ID，主键
                chat_id INTEGER,              -- 聊天ID
                invite_link TEXT,             -- 邀请链接
                invited_by INTEGER,           -- 邀请者
                score INTEGER                 -- 分数
            )
        ''')

        # 使用 SQL 语句更新用户记录中的邀请人 ID 为 inviting_chat_id
        cursor.execute("UPDATE users SET invited_by = ? WHERE user_id = ?", (inviting_chat_id, user_id))

        # 提交更改并关闭连接
        conn.commit()
        conn.close()
    except Exception as e:
        # 如果出现错误，打印错误信息
        print(f"Error saving inviting user ID to the database: {e}")

# 获取邀请人的ID
def get_inviting_user_id(chat_id):
    # 连接数据库
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    # 查询指定chat_id的用户邀请人的ID
    cursor.execute("SELECT invited_by FROM users WHERE chat_id = ?", (chat_id,))
    inviting_user_id = cursor.fetchone()

    # 关闭游标和数据库连接
    cursor.close()
    conn.close()

    # 如果找到邀请人ID，返回该ID，否则返回None
    if inviting_user_id:
        return inviting_user_id[0]
    else:
        return None


# 添加积分的函数
def add_score(user_id, amount):
    with sqlite3.connect(db_filename) as conn:
        cursor = conn.cursor()

        # 使用 SQL 更新语句增加或减少用户的积分
        cursor.execute("UPDATE users SET score = score + ? WHERE user_id = ?", (amount, user_id))

    # 记得提交更改
    conn.commit()



def create_user(user_id, chat_id, invite_link=None, invited_by=None):
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    # 先查询用户是否已存在
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        # 用户已存在，可以选择更新用户的其他信息，而不是插入新记录
        cursor.execute("UPDATE users SET chat_id = ?, invite_link = ?, invited_by = ? WHERE user_id = ?",
                       (chat_id, invite_link, invited_by, user_id))
    else:
        # 用户不存在，插入新记录
        cursor.execute("INSERT INTO users (user_id, chat_id, invite_link, invited_by, score) VALUES (?, ?, ?, ?, 0)",
                       (user_id, chat_id, invite_link, invited_by))

    cursor.close()
    conn.commit()
    conn.close()


# 查询用户的积分值
def get_score(user_id):
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute(f"SELECT score FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        return result[0]
    else:
        return 0


# 检查用户是否存在于数据库中
def is_user_in_db(user_id):
    conn = sqlite3.connect(db_filename)  # 连接到数据库
    cursor = conn.cursor()

    # 使用 SQL 查询语句检查用户是否在数据库中
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()  # 尝试获取查询结果

    cursor.close()
    conn.close()

    # 如果查询结果非空，表示用户存在于数据库中
    if result:
        return True
    else:
        # 否则，用户不在数据库中
        return False


# 异步函数，检查用户是否是频道的成员，并添加错误处理
async def check_channel_membership(user_id):
    try:
        # 使用 bot 对象获取用户在频道中的成员信息
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)

        # 检查用户的成员状态
        is_member = chat_member.status in ['member', 'administrator', 'creator']
        return is_member
    except Exception as e:
        # 如果发生错误，记录错误信息并返回 False
        logger.error(f"Error checking channel membership: {e}")
        return False


# 生成邀请链接
def generate_invite_link(user_id, inviting_chat_id):
    invite_link = f"https://t.me/{BOT_USERNAME}?start=invite_{user_id}"

    # 保存邀请人 ID
    save_inviting_user_id(user_id, inviting_chat_id)

    return invite_link

# 将邀请链接保存到数据库中
def save_invite_link_to_db(user_id, invite_link):
    try:
        conn = sqlite3.connect(db_filename)  # 连接到数据库
        cursor = conn.cursor()

        # 使用 SQL 语句插入数据
        cursor.execute("INSERT INTO invite_links (user_id, link) VALUES (?, ?)", (user_id, invite_link))

        # 提交更改并关闭连接
        conn.commit()
        conn.close()
    except Exception as e:
        # 如果出现错误，打印错误信息
        print(f"Error saving invite link to the database: {e}")


# 定义扣除积分的函数
def subtract_score(user_id, amount):
    with sqlite3.connect(db_filename) as conn:
        cursor = conn.cursor()

        # 使用 SQL 更新语句减少用户的积分
        cursor.execute("UPDATE users SET score = score - ? WHERE user_id = ?", (amount, user_id))

    # 记得提交更改
    conn.commit()






def has_accepted_invitation(user_id):
    conn = sqlite3.connect(db_filename)  # 连接到数据库
    cursor = conn.cursor()

    # 使用 SQL 查询语句检查用户是否在 users 或 invite_links 表中
    cursor.execute(
        "SELECT user_id FROM users WHERE user_id = ? UNION SELECT user_id FROM invite_links WHERE user_id = ?",
        (user_id, user_id))
    result = cursor.fetchone()  # 尝试获取查询结果

    cursor.close()
    conn.close()

    if result:
        # 用户已经在其中一个表中
        return True
    else:
        # 用户没有在任何一个表中
        return False


# 获取用户ID列表从 invite_links 表中
def get_users_from_invite_links_table():
    users = []  # 创建一个空列表以存储用户 ID

    conn = None
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_filename)

        # 创建游标
        cursor = conn.cursor()

        # 执行 SQL 查询以获取所有用户 ID
        cursor.execute("SELECT user_id FROM invite_links")

        # 获取查询结果中的所有行
        rows = cursor.fetchall()

        # 提取每行中的用户 ID 并添加到 users 列表中
        users = [row[0] for row in rows]

    except sqlite3.Error as e:
        # 处理数据库错误
        print(f"数据库错误: {e}")

    except Exception as ex:
        # 处理其他异常
        print(f"发生异常: {ex}")

    finally:
        if conn:
            conn.close()

    return users
    return users  # 返回用户 ID 列表


def get_user_count():
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_filename)

        # 创建游标
        cursor = conn.cursor()

        # 执行 SQL 查询以获取用户计数
        cursor.execute("SELECT COUNT(*) FROM invite_links")

        # 获取查询结果中的计数值
        count = cursor.fetchone()[0]

        return count

    except sqlite3.Error as e:
        # 处理数据库错误
        print(f"数据库错误: {e}")
        return None

    except Exception as ex:
        # 处理其他异常
        print(f"发生异常: {ex}")
        return None

    finally:
        if conn:
            conn.close()


# 创建一个常驻菜单
options = [
    "免费节点",
    "邀请好友",
    "兑换奖励",
    "查询积分",
    "联系客服",
    "帮助",
]

custom_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
custom_keyboard.add(*options)


# 处理用户点击 "免费节点" 命令
@dp.message_handler(lambda message: message.text == "免费节点")
async def handle_free_node(message: types.Message):
    user_id = message.from_user.id

    # 检查用户是否是频道成员
    is_member = await check_channel_membership(user_id)

    if not is_member:
        # 如果用户没有加入频道，发送提示消息和频道链接按钮
        channel_button = types.InlineKeyboardButton(text="加入频道", url=CHANNEL_LINK)
        keyboard = types.InlineKeyboardMarkup().add(channel_button)
        await message.answer("加入我们的频道才可以获取免费节点。", reply_markup=keyboard)
    else:
        # 如果用户已经是频道成员，读取免费节点信息并发送给用户
        try:
            with open("mf.txt", "r") as node_file:
                free_node_info = node_file.read()
            await message.answer(free_node_info)
        except FileNotFoundError:
            await message.answer("很抱歉，暂时没有可用的免费节点信息。请稍后再试。")


# 处理用户点击 "邀请好友" 命令
@dp.message_handler(lambda message: message.text == "邀请好友")
async def invite_friends(message: types.Message):
    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    
    # 获取 inviting_chat_id，这里假设 inviting_chat_id 就是当前聊天的 chat_id
    inviting_chat_id = chat_id
    
    invite_link = generate_invite_link(user_id, inviting_chat_id)
    inviting_user_id = get_inviting_user_id(chat_id)
    create_user(user_id, chat_id, invite_link, inviting_user_id)

    await message.reply(f"分享这个链接给您的朋友：\n<code>{invite_link}</code>\n点击复制，当您的朋友关注我们时，您将获得积分！", parse_mode='HTML', reply_markup=custom_keyboard)




@dp.message_handler(lambda message: message.text == "兑换奖励")
async def exchange_reward(message: types.Message):
    user_id = message.from_user.id

    # 获取用户的当前积分
    current_score = get_score(user_id)

    # 检查用户积分是否足够兑换奖励
    if current_score >= exchange_score:
        # 读取奖励列表
        with open('jl.txt', 'r', encoding='utf-8') as file:
            rewards = file.readlines()

        if rewards:
            # 获取第一个奖励，并移除两端空白字符
            reward_to_exchange = rewards[0].strip()

            # 删除已经兑换的奖励
            rewards.pop(0)

            # 更新奖励列表到文件
            with open('jl.txt', 'w', encoding='utf-8') as file:
                file.writelines(rewards)

            # 减少用户的积分
            subtract_score(user_id, exchange_score)

            # 添加新的链接按钮
            exchange_reward_link_button = types.InlineKeyboardButton(text=EXCHANGE_REWARD_TEXT, url=EXCHANGE_REWARD_URL)
            keyboard = types.InlineKeyboardMarkup().add(exchange_reward_link_button)

            # 发送兑换的奖励给用户（在更新积分之后），包含所需积分信息
            await message.answer(
                f"恭喜！你成功兑换了奖励：{reward_to_exchange}，消耗了 {exchange_score} 积分。点击下面的链接获取更多信息:",
                reply_markup=keyboard)
        else:
            await message.answer("抱歉，没有可用的奖励.")
    else:
        # 如果积分不足，发送一条消息告知用户当前积分和所需积分
        await message.answer(f"抱歉，你没有足够的积分来兑换奖励。当前积分为 {current_score}，所需积分为 {exchange_score}。")


# 处理用户点击 "查询积分" 命令
@dp.message_handler(lambda message: message.text == "查询积分")
async def check_score(message: types.Message):
    user_id = str(message.from_user.id)

    # 查询用户的积分值
    score = get_score(user_id)

    # 发送用户的积分值
    await message.answer(f"您的当前积分是 {score}。", reply_markup=custom_keyboard)


# 处理用户点击 "联系客服" 命令
@dp.message_handler(lambda message: message.text == "联系客服")
async def contact_support(message: types.Message):
    """处理用户选择的联系客服选项"""
    support_link = SUPPORT_LINK  # 从配置文件中获取客服链接

    # 创建包含客服链接的内联键盘按钮
    support_button = types.InlineKeyboardButton(text="联系客服", url=support_link)
    keyboard = types.InlineKeyboardMarkup().add(support_button)

    # 发送包含客服链接的消息
    await message.answer("点击下面的链接联系客服:", reply_markup=keyboard)


# 处理用户点击 "帮助" 命令
@dp.message_handler(lambda message: message.text == "帮助")
async def help(message: types.Message):
    """处理用户选择的帮助选项"""
    # 从配置文件中获取帮助消息内容
    help_message = HELP_MESSAGE

    # 发送帮助消息给用户
    await message.answer(help_message)


@dp.message_handler(commands=['inquire_user'])
async def inquire_user_command(message: types.Message):
    if message.from_user.id == ADMIN_USER_ID:  # 仅管理员可以使用此命令
        user_count = get_user_count()
        await message.answer(f"当前用户数量为: {user_count}")

        # 添加以下调试语句
        print("inquire_user_command 被触发了")
        print(f"message.from_user.id: {message.from_user.id}")
    else:
        await message.answer("只有管理员可以使用此命令.")


@dp.message_handler(commands=['xx'])
async def send_message_to_all_users(message: Message):
    # 检查是否是管理员
    if message.from_user.id == ADMIN_USER_ID:  # 替换为您的管理员用户ID
        # 解析要发送的消息
        try:
            _, message_text = message.text.split(' ', 1)
        except ValueError:
            await message.answer("请提供要发送的消息文本。用法：/xx [消息文本]")
            return

        # 获取所有在 invite_links 表中的用户ID
        user_ids = get_users_from_invite_links_table()

        # 遍历所有用户并发送消息
        for user_id in user_ids:
            try:
                await bot.send_message(user_id, message_text)
            except Exception as e:
                print(f"向用户 {user_id} 发送消息时出错：{str(e)}")

        await message.answer("消息已成功发送给所有关注机器人的用户。")
    else:
        await message.answer("只有管理员可以使用此功能。")
        

# 处理/gx命令
@dp.message_handler(commands=['gx'])
async def handle_gx_command(message: types.Message):
    # 检查是否是管理员发送的消息
    if message.from_user.id == ADMIN_USER_ID:
        try:
            # 获取/gx命令后的文本
            content_to_save = message.text.replace('/gx', '').strip()

            # 打开mf.txt文件，以覆盖模式保存内容（清空文件内容并写入新的内容）
            with open('mf.txt', 'w', encoding='utf-8') as file:
                file.write(content_to_save + '\n')

            # 发送确认消息给管理员
            await message.reply('内容已成功保存（清空并覆盖模式）。')
        except Exception as e:
            # 发生错误时发送错误消息给管理员
            await message.reply(f'保存内容时出错：{str(e)}')
    else:
        # 如果不是管理员发送的消息，发送提示消息
        await message.reply('只有管理员可以使用此命令。')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id  # 获取当前聊天的 chat_id

    # 强制发送常驻菜单
    keyboard_for_start = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard_for_start.add(*options)

    # 发送常驻菜单
    await message.answer("节点更新机器人，长期免费更新，欢迎关注。", reply_markup=keyboard_for_start)

    # 检查是否有邀请参数
    invite_params = message.get_args()
    inviting_user_id = None

    if invite_params and invite_params.startswith("invite_"):
        inviter_id = int(invite_params.split("_")[1])

        # 检查用户是否已经接受过邀请，如果是，则不再增加积分
        if not has_accepted_invitation(user_id):
            inviting_user_id = inviter_id
            add_score(inviter_id, 1)  # 给邀请人增加积分
        else:
            inviting_user_id = None

    # 保存邀请人 ID 到数据库，但只在用户未接受过邀请时保存
    if inviting_user_id:
        try:
            # 连接到数据库
            conn = sqlite3.connect(db_filename)

            # 创建游标
            cursor = conn.cursor()

            # 检查 inviting_users 表格是否存在，如果不存在，则创建它
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inviting_users (
                    user_id INTEGER PRIMARY KEY,
                    inviting_user_id INTEGER
                )
            ''')

            # 插入新的邀请记录
            cursor.execute("INSERT INTO inviting_users (user_id, inviting_user_id) VALUES (?, ?)", (user_id, inviting_user_id))

            # 提交更改
            conn.commit()
        except sqlite3.Error as e:
            # 处理数据库错误
            print(f"数据库错误: {e}")
        finally:
            if conn:
                conn.close()

    # 检查用户是否已经加入频道
    is_member = await check_channel_membership(user_id)

    if not is_member:
        # 用户没有加入频道，提示用户加入频道
        invite_link = generate_invite_link(user_id, chat_id)  # 传递当前聊天的 chat_id
        save_invite_link_to_db(user_id, invite_link)
        channel_button = types.InlineKeyboardButton(text="加入频道", url=CHANNEL_LINK)
        keyboard = types.InlineKeyboardMarkup().add(channel_button)
        await message.answer(RESERVED_MESSAGE1, reply_markup=keyboard)
    else:
        # 用户已经加入频道，创建机器人邀请链接并保存到数据库
        invite_link = generate_invite_link(user_id, chat_id)  # 传递当前聊天的 chat_id
        save_invite_link_to_db(user_id, invite_link)

        # 发送 RESERVED_MESSAGE2 给用户
        keyboard = types.InlineKeyboardMarkup()
        link_button_1 = types.InlineKeyboardButton(text=LINK_BUTTON_1_TEXT, url=LINK_BUTTON_1_URL)
        link_button_2 = types.InlineKeyboardButton(text=LINK_BUTTON_2_TEXT, url=LINK_BUTTON_2_URL)
        keyboard.add(link_button_1, link_button_2)
        await message.answer(RESERVED_MESSAGE2, reply_markup=keyboard)


if __name__ == '__main__':
    create_tables()  # 创建用户表格
    create_invite_links_table()  # 创建邀请链接表格
    executor.start_polling(dp, skip_updates=True)
    
