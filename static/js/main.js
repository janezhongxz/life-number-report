document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('lifeForm');
    const birthdayInput = document.getElementById('birthday');
    const genderSelect = document.getElementById('gender');
    const ageInput = document.getElementById('age');
    const questionInput = document.getElementById('question');
    const calcBtn = document.getElementById('calcBtn');
    const resultArea = document.getElementById('resultArea');
    const lifeNumberEl = document.getElementById('lifeNumber');
    const masterLabel = document.getElementById('masterLabel');
    const redeemSection = document.getElementById('redeemSection');
    const redeemCodeInput = document.getElementById('redeemCode');
    const checkCodeBtn = document.getElementById('checkCodeBtn');
    const codeStatus = document.getElementById('codeStatus');
    const generateBtn = document.getElementById('generateBtn');
    const loading = document.getElementById('loading');
    const historyList = document.getElementById('historyList');

    let currentLifeNumber = null;
    let codeValid = false;

    loadHistory();

    birthdayInput.addEventListener('change', function() {
        if (this.value) {
            const birthDate = new Date(this.value);
            const today = new Date();
            let age = today.getFullYear() - birthDate.getFullYear();
            const monthDiff = today.getMonth() - birthDate.getMonth();
            if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) age--;
            ageInput.value = age;
        }
    });

    calcBtn.addEventListener('click', async function() {
        const birthday = birthdayInput.value;
        const gender = genderSelect.value;
        if (!birthday || !gender) { alert('请填写出生日期和性别'); return; }

        try {
            const response = await fetch('/api/calculate', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ birthday, gender })
            });
            const data = await response.json();
            if (data.error) { alert(data.error); return; }
            currentLifeNumber = data.life_number;
            lifeNumberEl.textContent = data.life_number;
            masterLabel.classList.toggle('hidden', !data.is_master);
            resultArea.classList.remove('hidden');
            redeemSection.classList.remove('hidden');
            resultArea.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } catch (error) {
            console.error(error); alert('计算失败，请重试');
        }
    });

    checkCodeBtn.addEventListener('click', async function() {
        const code = redeemCodeInput.value.trim().toUpperCase();
        if (!code) { alert('请输入兑换码'); return; }
        try {
            const response = await fetch('/api/redeem/check', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code })
            });
            const data = await response.json();
            if (data.valid) {
                codeStatus.textContent = ' ✓ 兑换码有效';
                codeStatus.className = 'code-status valid';
                codeValid = true;
                generateBtn.classList.remove('hidden');
            } else {
                codeStatus.textContent = ' ✗ ' + data.message;
                codeStatus.className = 'code-status invalid';
                codeValid = false;
                generateBtn.classList.add('hidden');
            }
        } catch (error) {
            console.error(error); alert('验证失败，请重试');
        }
    });

    generateBtn.addEventListener('click', async function(e) {
        e.preventDefault();
        if (!codeValid) { alert('请先验证兑换码'); return; }
        showLoading(true);
        try {
            const codeResponse = await fetch('/api/redeem/use', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
回复 Jane.zhong: 
继续最后一个！
code: redeemCodeInput.value.trim().toUpperCase() })
            });
            const codeData = await codeResponse.json();
            if (!codeData.success) { showLoading(false); alert(codeData.message); return; }
            const response = await fetch('/api/generate', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ birthday: birthdayInput.value, gender: genderSelect.value, question: questionInput.value })
            });
            const data = await response.json();
            showLoading(false);
            if (data.error) { alert(data.error); return; }
            window.location.href = '/report/' + data.report_id;
        } catch (error) {
            showLoading(false); console.error(error); alert('生成失败，请重试');
        }
    });

    async function loadHistory() {
        try {
            const response = await fetch('/api/reports/history');
            const reports = await response.json();
            if (reports.length === 0) { historyList.innerHTML = '暂无记录'; return; }
            historyList.innerHTML = reports.map(r => `${r.birthday} (${r.age}岁)生命数字 ${r.life_number}`).join('');
        } catch (error) { console.error(error); }
    }

    function showLoading(show) { loading.classList.toggle('hidden', !show); }
});
