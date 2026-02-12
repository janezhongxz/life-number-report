"""
生命数字解读报告生成器
Life Number Report Generator
"""

import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from openai import OpenAI

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# 初始化数据库
def init_db():
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    
    # 创建报告记录表
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            life_number INTEGER,
            birthday TEXT,
            gender TEXT,
            age INTEGER,
            question TEXT,
            report_content TEXT,
            created_at TEXT
        )
    ''')
    
    # 创建兑换码表
    c.execute('''
        CREATE TABLE IF NOT EXISTS redeem_codes (
            code TEXT PRIMARY KEY,
            is_used INTEGER DEFAULT 0,
            used_at TEXT,
            created_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# 初始化数据库
init_db()

# 计算生命数字
def calculate_life_number(birthday):
    """
    计算生命数字
    规则：将出生年月日拆分求和，直至得到个位数或11/22/33
    """
    # 移除分隔符，只保留数字
    digits = [int(d) for d in birthday.replace('-', '').replace('/', '')]
    
    def sum_digits(n):
        return sum(int(d) for d in str(n))
    
    total = sum(digits)
    
    # 主数字
    master_numbers = [11, 22, 33]
    if total in master_numbers:
        return total
    
    # 继续拆分直到个位数
    while total > 9:
        total = sum_digits(total)
        if total in master_numbers:
            return total
    
    return total

# 生成AI报告
def generate_report(life_number, gender, age, question):
    """
    调用AI生成生命数字解读报告
    """
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    
    # 根据年龄确定解读方向
    if age < 18:
        focus = "养育建议、兴趣班推荐、性格培养重点"
    elif age < 24:
        focus = "专业选择、院校方向、学业规划"
    elif age < 40:
        focus = "职业发展、人生规划、人际关系"
    elif age < 60:
        focus = "第二曲线打造、自我价值实现、事业转型"
    else:
        focus = "养老规划、传承建议（经验/财富/家族文化）"
    
    prompt = f"""
你是一位资深的生命数字解读师。请为用户生成一份详细的生命数字解读报告，要求如下：

**用户信息：**
- 生命数字：{life_number}
- 性别：{gender}
- 年龄：{age}岁
- 当前困惑：{question}
- 解读重点：{focus}

**报告要求：**
1. 字数≥5000字
2. 结构清晰，包含以下部分：
   - 生命数字解析（{life_number}的含义、性格特点、天赋使命）
   - 年龄阶段适配建议（针对{age}岁的具体指导）
   - 困惑点针对性解答
   - 行动建议与提醒

3. 语言温暖、专业、有洞察力
4. 使用流畅的散文式写作，避免过多列表

请开始生成报告：
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "你是一位资深的生命数字解读师，拥有20年经验，帮助无数人了解自己的人生使命与潜能。你的解读温暖、专业、富有洞察力。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=4000
    )

    return response.choices[0].message.content


# ============ 路由 ============

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/calculate', methods=['POST'])
def calculate():
    """计算生命数字"""
    data = request.json
    
    birthday = data.get('birthday')
    if not birthday:
        return jsonify({'error': '请输入出生日期'}), 400
    
    try:
        birth_date = datetime.strptime(birthday, '%Y-%m-%d')
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    except:
        return jsonify({'error': '日期格式无效'}), 400
    
    life_number = calculate_life_number(birthday)
    
    return jsonify({
        'life_number': life_number,
        'is_master': life_number in [11, 22, 33],
        'age': age
    })


@app.route('/api/generate', methods=['POST'])
def generate():
    """生成报告"""
    data = request.json
    
    birthday = data.get('birthday')
    gender = data.get('gender')
回复 Jane.zhong: 
全部删除了
question = data.get('question', '')
    if not all([birthday, gender]):
        return jsonify({'error': '请填写完整信息'}), 400
    # 计算年龄
    birth_date = datetime.strptime(birthday, '%Y-%m-%d')
    today = datetime.now()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    # 计算生命数字
    life_number = calculate_life_number(birthday)
    try:
        # 生成报告
        report_content = generate_report(life_number, gender, age, question)
        # 保存到数据库
        conn = sqlite3.connect('reports.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO reports (life_number, birthday, gender, age, question, report_content, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (life_number, birthday, gender, age, question, report_content, datetime.now().isoformat()))
        report_id = c.lastrowid
        conn.commit()
        conn.close()
        return jsonify({
            'success': True,
            'report_id': report_id,
            'life_number': life_number,
            'report': report_content
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/report/')
def view_report(report_id):
    """查看报告"""
    conn = sqlite3.connect('reports.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM reports WHERE id = ?', (report_id,))
    report = c.fetchone()
    conn.close()
    if not report:
        return "报告不存在", 404
    return render_template('report.html', report=dict(report))


@app.route('/api/reports/history')
def history():
    """历史记录"""
    conn = sqlite3.connect('reports.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT id, life_number, birthday, age, created_at FROM reports ORDER BY id DESC LIMIT 50')
    reports = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(reports)


# ============ 兑换码相关 ============

@app.route('/api/redeem/generate', methods=['POST'])
def generate_code():
    """生成兑换码（管理用）"""
    import secrets
    code = ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(12))
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    c.execute('INSERT INTO redeem_codes (code, created_at) VALUES (?, ?)',
              (code, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({'code': code})


@app.route('/api/redeem/check', methods=['POST'])
def check_code():
    """检查兑换码"""
    data = request.json
    code = data.get('code', '').upper()
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    c.execute('SELECT is_used FROM redeem_codes WHERE code = ?', (code,))
    result = c.fetchone()
    conn.close()
    if not result:
        return jsonify({'valid': False, 'message': '兑换码不存在'})
    if result[0] == 1:
        return jsonify({'valid': False, 'message': '兑换码已被使用'})
    return jsonify({'valid': True})


@app.route('/api/redeem/use', methods=['POST'])
def use_code():
    """使用兑换码"""
    data = request.json
    code = data.get('code', '').upper()
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    c.execute('SELECT is_used FROM redeem_codes WHERE code = ?', (code,))
    result = c.fetchone()
    if not result:
        conn.close()
        return jsonify({'success': False, 'message': '兑换码不存在'})
    if result[0] == 1:
        conn.close()
        return jsonify({'success': False, 'message': '兑换码已被使用'})
    c.execute('UPDATE redeem_codes SET is_used = 1, used_at = ? WHERE code = ?',
              (datetime.now().isoformat(), code))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


if name == 'main':
    app.run(debug=True, host='0.0.0.0', port=5000)
