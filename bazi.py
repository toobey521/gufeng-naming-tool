"""
八字计算引擎
基于出生年月日计算生辰八字，分析五行旺衰，推荐喜用神
"""

from datetime import datetime, date
import math

# ============ 天干地支 ============
TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 天干五行
GAN_WU_XING = {
    '甲': '木', '乙': '木',
    '丙': '火', '丁': '火',
    '戊': '土', '己': '土',
    '庚': '金', '辛': '金',
    '壬': '水', '癸': '水'
}

# 地支五行
ZHI_WU_XING = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木',
    '辰': '土', '巳': '火', '午': '火', '未': '土',
    '申': '金', '酉': '金', '戌': '土', '亥': '水'
}

# 地支藏干 (main element only for simplicity)
ZHI_CANG_GAN = {
    '子': ['癸'],
    '丑': ['己', '癸', '辛'],
    '寅': ['甲', '丙', '戊'],
    '卯': ['乙'],
    '辰': ['戊', '乙', '癸'],
    '巳': ['丙', '庚', '戊'],
    '午': ['丁', '己'],
    '未': ['己', '丁', '乙'],
    '申': ['庚', '壬', '戊'],
    '酉': ['辛'],
    '戌': ['戊', '辛', '丁'],
    '亥': ['壬', '甲']
}

# 五行相生
WU_XING_SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
# 五行相克
WU_XING_KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}

# ============ 生肖 ============
SHENG_XIAO = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']

# ============ 年份对应 (粗略立春调整) ============
# 立春日期（每年大约2月4日）
LICHUN_DATES = {
    2024: (2, 4), 2025: (2, 3), 2026: (2, 4),
    2027: (2, 4), 2028: (2, 4), 2029: (2, 3),
    2030: (2, 4), 2031: (2, 4), 2032: (2, 4),
}

def get_lichun_date(year):
    """获取给定年份的立春日期"""
    base = LICHUN_DATES.get(year)
    if base:
        return base
    # 近似：2月4日
    return (2, 4)

def get_year_ganzhi(year, birth_date):
    """获取年柱（以立春为界）"""
    lichun_month, lichun_day = get_lichun_date(year)
    # 如果生日在立春之后，使用该年的干支；否则使用前一年的干支
    actual_year = year
    if (birth_date.month < lichun_month or
        (birth_date.month == lichun_month and birth_date.day < lichun_day)):
        actual_year = year - 1
    idx = (actual_year - 4) % 60  # 甲子为第0年，公元4年为甲子年
    gan_idx = idx % 10
    zhi_idx = idx % 12
    return TIAN_GAN[gan_idx], DI_ZHI[zhi_idx]

def get_month_ganzhi(year, birth_date, year_gan):
    """获取月柱（节气月）"""
    # 简化的月干支计算：每月的地支固定
    # 正月寅、二月卯...十一月子、十二月丑
    # 但以节气为界。这里简化：当月15日前用上月，之后用本月
    month = birth_date.month
    day = birth_date.day
    
    # 简化的节气月映射
    jieqi_month = {
        1: '寅', 2: '卯', 3: '辰', 4: '巳', 5: '午', 6: '未',
        7: '申', 8: '酉', 9: '戌', 10: '亥', 11: '子', 12: '丑'
    }
    
    # 节气大致日（每月4~8号为节）
    jieqi_days = {1: 6, 2: 4, 3: 6, 4: 5, 5: 6, 6: 6,
                  7: 7, 8: 7, 9: 8, 10: 8, 11: 7, 12: 7}
    
    actual_month = month
    if day < jieqi_days.get(month, 6):
        actual_month = month - 1 if month > 1 else 12
    
    zhi = jieqi_month.get(actual_month, '子')
    
    # 月干计算：年干起月
    year_gan_idx = TIAN_GAN.index(year_gan)
    month_zhi_idx = DI_ZHI.index(zhi)
    month_gan_idx = (year_gan_idx % 5) * 2 + month_zhi_idx
    gan = TIAN_GAN[month_gan_idx % 10]
    
    return gan, zhi

def get_day_ganzhi(birth_date):
    """获取日柱"""
    # 使用基准日算法：2000年1月1日 = 甲子日
    # 实际计算用公式
    y = birth_date.year
    m = birth_date.month
    d = birth_date.day
    
    # 蔡勒公式变体：计算日干支序号
    if m <= 2:
        y -= 1
        m += 12
    
    A = y % 100
    B = y // 100
    
    # 计算从基准到该日的天数，mod 60
    # 日干支基数值
    if birth_date.year >= 2000:
        # 2000-2099 公式
        day_offset = (6 + 5 * (y - 2000) + (y - 2000) // 4 + 
                       (13 * (m + 1)) // 5 + d - 1) % 60
    else:
        day_offset = (5 * (B - 19) + (B - 19) // 4 + 15 + 
                      5 * A + A // 4 + (13 * (m + 1)) // 5 + d - 1) % 60
    
    # 修正：需要精确到公元前才能用标准公式，这里用查表法简版
    from datetime import date as dt_date
    base = dt_date(1900, 1, 1)  # 1900-01-01 = 甲戌日 (10, 10) = 干支索引10
    target = dt_date(birth_date.year, birth_date.month, birth_date.day)
    delta = (target - base).days
    idx = (10 + delta) % 60  # 甲戌 = 索引10
    
    # 如果为负，adjust
    idx = idx % 60
    
    gan_idx = idx % 10
    zhi_idx = idx % 12
    return TIAN_GAN[gan_idx], DI_ZHI[zhi_idx]

def get_hour_ganzhi(day_gan, hour=12):
    """获取时柱
    
    Args:
        day_gan: 日干
        hour: 出生时辰（0-23），默认12（午时）
    """
    # 时辰地支
    hour_zhi_map = [
        (23, '子'), (1, '丑'), (3, '寅'), (5, '卯'),
        (7, '辰'), (9, '巳'), (11, '午'), (13, '未'),
        (15, '申'), (17, '酉'), (19, '戌'), (21, '亥')
    ]
    
    if hour == 23:
        zhi = '子'
    else:
        for start, z in hour_zhi_map:
            if start <= hour < start + 2:
                # 特殊处理子时跨天
                if start == 23:
                    zhi = '子'
                else:
                    zhi = z
                break
        else:
            zhi = '子'
    
    zhi_idx = DI_ZHI.index(zhi)
    
    # 日干定时辰天干
    day_gan_idx = TIAN_GAN.index(day_gan)
    hour_gan_idx = (day_gan_idx % 5) * 2 + zhi_idx
    gan = TIAN_GAN[hour_gan_idx % 10]
    
    return gan, zhi


def get_ganzhi_from_time(hour):
    """根据小时获取时辰地支"""
    if hour < 0 or hour >= 24:
        return '子'
    if hour == 23:
        return '子'
    idx = (hour + 1) // 2
    if idx >= 12:
        idx = 0
    return DI_ZHI[idx]


def analyze_wuxing(ganzhi_list):
    """分析五行旺衰
    
    Args:
        ganzhi_list: [(天干, 地支), ...] 四柱列表
    Returns:
        dict: 五行分布及分析
    """
    wx_count = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
    
    for gan, zhi in ganzhi_list:
        # 天干五行
        gan_wx = GAN_WU_XING.get(gan, '')
        if gan_wx:
            wx_count[gan_wx] = wx_count.get(gan_wx, 0) + 2  # 天干权重2
        
        # 地支本气五行
        zhi_wx = ZHI_WU_XING.get(zhi, '')
        if zhi_wx:
            wx_count[zhi_wx] = wx_count.get(zhi_wx, 0) + 1  # 地支权重1
        
        # 地支藏干（简化：取第一个藏干）
        cang_gans = ZHI_CANG_GAN.get(zhi, [])
        for cg in cang_gans[:1]:  # 仅取本气
            cg_wx = GAN_WU_XING.get(cg, '')
            if cg_wx:
                wx_count[cg_wx] = wx_count.get(cg_wx, 0) + 1
    
    # 按分数排序
    sorted_wx = sorted(wx_count.items(), key=lambda x: -x[1])
    
    # 找出最旺和最弱的五行
    max_wx = sorted_wx[0][0] if sorted_wx[0][1] > 0 else '土'
    min_wx = sorted_wx[-1][0] if sorted_wx[-1][1] < sorted_wx[0][1] else '木'
    
    # 推荐喜用神：最弱五行所生的，或生最弱五行的
    # 缺啥补啥
    weak_elements = [wx for wx, count in sorted_wx if count <= 1]
    
    # 推荐五行（补最弱的）
    if weak_elements:
        recommend = weak_elements[0]
    else:
        # 如果五行均衡，用日干五行
        _, day_gan = ganzhi_list[2]
        recommend = GAN_WU_XING.get(day_gan, '土')
    
    return {
        'counts': wx_count,
        'sorted': sorted_wx,
        'strongest': max_wx,
        'weakest': min_wx,
        'recommend_element': recommend,
        'summary': _build_wuxing_summary(wx_count, recommend)
    }


def _build_wuxing_summary(wx_count, recommend):
    """生成五行分析文字"""
    labels = {
        '金': '金旺，刚毅果断',
        '木': '木旺，仁慈宽厚',
        '水': '水旺，智慧灵活',
        '火': '火旺，热情进取',
        '土': '土旺，稳重诚信'
    }
    weak_labels = {
        '金': '金弱，可补金增强决断力',
        '木': '木弱，补木增仁寿',
        '水': '水弱，补水增智慧',
        '火': '火弱，补火增活力',
        '土': '土弱，补土增稳重'
    }
    
    strengths = []
    for wx, cnt in sorted(wx_count.items(), key=lambda x: -x[1]):
        if cnt >= 2:
            strengths.append(labels.get(wx, ''))
    
    weakness = weak_labels.get(recommend, '')
    
    # 用神建议
    rec_text = {
        '金': '名字宜选用含金元素的字（铭、钧、锐、铮、锦等）',
        '木': '名字宜选用含木元素的字（林、柏、楷、桐、森等）',
        '水': '名字宜选用含水元素的字（涵、清、泽、澜、润等）',
        '火': '名字宜选用含火元素的字（煜、昕、晟、灿、灵等）',
        '土': '名字宜选用含土元素的字（城、峥、岚、屿、岩等）'
    }
    
    return {
        'strengths': '；'.join(strengths) if strengths else '五行较均衡',
        'weakness': weakness,
        'recommend_text': rec_text.get(recommend, '')
    }


def calculate_bazi(year, month, day, gender, hour=12):
    """计算八字主函数
    
    Args:
        year, month, day: 公历出生日期
        gender: 'male' 或 'female'
        hour: 出生小时（0-23），默认午时
    Returns:
        dict: 完整的八字分析结果
    """
    birth_date = date(year, month, day)
    
    # 四柱
    year_gan, year_zhi = get_year_ganzhi(year, birth_date)
    month_gan, month_zhi = get_month_ganzhi(year, birth_date, year_gan)
    day_gan, day_zhi = get_day_ganzhi(birth_date)
    hour_gan, hour_zhi = get_hour_ganzhi(day_gan, hour)
    
    pillars = [
        ('年柱', year_gan, year_zhi),
        ('月柱', month_gan, month_zhi),
        ('日柱', day_gan, day_zhi),
        ('时柱', hour_gan, hour_zhi)
    ]
    
    ganzhi_list = [(year_gan, year_zhi), (month_gan, month_zhi),
                   (day_gan, day_zhi), (hour_gan, hour_zhi)]
    
    # 五行分析
    wx_result = analyze_wuxing(ganzhi_list)
    
    # 生肖
    zodiac_idx = (year - 4) % 12
    zodiac = SHENG_XIAO[zodiac_idx]
    
    # 日主（日干）
    ri_zhu = day_gan
    ri_zhu_wx = GAN_WU_XING.get(ri_zhu, '')
    
    # 性别标签
    gender_label = '男' if gender == 'male' else '女'
    
    return {
        'birth_date': f'{year}年{month}月{day}日',
        'gender': gender_label,
        'hour': f'{hour}时',
        'zodiac': zodiac,
        'pillars': pillars,
        'bazi_str': f'{year_gan}{year_zhi} {month_gan}{month_zhi} {day_gan}{day_zhi} {hour_gan}{hour_zhi}',
        'ri_zhu': ri_zhu,
        'ri_zhu_wx': ri_zhu_wx,
        'wuxing': wx_result,
        'recommend_element': wx_result['recommend_element']
    }


def get_five_element_char(element):
    """获取某五行的推荐用字列表（核心用字）"""
    char_map = {
        '金': ['铭', '钧', '锐', '铮', '锦', '钊', '钦', '锟', '锋', '鑫',
               '瑞', '琛', '瑜', '瑾', '琪', '瑶', '环', '玺', '玥', '珏',
               '钢', '钒', '钰', '铄', '铠', '铉', '锴', '镕', '镜', '钟'],
        '木': ['林', '柏', '楷', '桐', '森', '彬', '杉', '楠', '槿', '桦',
               '松', '枫', '柯', '棠', '梁', '棋', '栋', '桥', '桓', '栩',
               '荣', '梓', '杭', '杰', '森', '柳', '杨', '梧', '棉', '樵'],
        '水': ['涵', '清', '泽', '澜', '润', '潇', '瀚', '沛', '澄', '洛',
               '泓', '淳', '渝', '沁', '溪', '江', '源', '波', '涛', '浩',
               '泰', '沛', '洋', '洲', '川', '泉', '澜', '灏', '漪', '淳'],
        '火': ['煜', '昕', '晟', '灿', '灵', '昭', '昱', '曦', '曜', '旻',
               '昊', '昀', '晖', '焕', '炜', '炫', '炯', '炳', '炽', '烁',
               '亮', '宁', '暖', '炎', '畅', '朗', '熹', '烈', '然', '煦'],
        '土': ['城', '峥', '岚', '屿', '岩', '峰', '峻', '屹', '岭', '岗',
               '维', '远', '安', '宇', '辰', '宸', '坤', '垣', '坡', '培',
               '坦', '垚', '圣', '圭', '志', '磐', '岳', '峡', '岱', '峨']
    }
    return char_map.get(element, [])


if __name__ == '__main__':
    # 测试
    result = calculate_bazi(2023, 6, 1, 'male', 14)
    for p_name, p_gan, p_zhi in result['pillars']:
        print(f"{p_name}: {p_gan}{p_zhi}")
    print(f"\n八字: {result['bazi_str']}")
    print(f"日主: {result['ri_zhu']}({result['ri_zhu_wx']})")
    print(f"生肖: {result['zodiac']}")
    print(f"\n五行分布: {result['wuxing']['counts']}")
    print(f"推荐用神: {result['recommend_element']}")
    print(f"建议: {result['wuxing']['summary']['recommend_text']}")
