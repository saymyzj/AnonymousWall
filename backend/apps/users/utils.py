import random
import hashlib
import uuid

ANIMALS = [
    '熊猫', '水母', '海豚', '企鹅', '考拉', '兔子', '猫咪', '柴犬',
    '树懒', '松鼠', '鹦鹉', '仓鼠', '浣熊', '狐狸', '鲸鱼', '猫头鹰',
    '小鹿', '海龟', '蝴蝶', '刺猬', '白鸽', '萤火虫', '独角兽', '小龙',
]


def generate_nickname():
    animal = random.choice(ANIMALS)
    number = random.randint(1000, 9999)
    return f'匿名{animal}#{number}'


def generate_avatar_seed():
    return hashlib.md5(uuid.uuid4().hex.encode()).hexdigest()
